import os
import glob
import json
from datetime import datetime
from collections import defaultdict
from logging import WARN, ERROR

from watcher import Watcher
from easy_alert.entity import Alert, Level
from easy_alert.util import get_server_id
from easy_alert.i18n import *
from easy_alert.setting.setting_error import SettingError


class LogFormatError(Exception):
    """Class for log format error"""


class LogWatcher(Watcher):
    """
    Watch log files filtered by Fluentd (td-agent)

    configuration should be this dict
      watch_dir  [required]: path to the directory to watch
      target_pattern       : glob pattern for the target files (default:alert.????????_????_*.log)
      pending_pattern      : glob pattern for checking pending files (default:alert.????????_????*)
      message_num_threshold: maximum number of messages for each log level (default:15)
      message_len_threshold: maximum length for each message (default:1024)
      pending_threshold    : threshold number of files for checking pending files (default:3)

    The settings of td-agent.conf should be like this.

    # Watch a log file
    <source>
      type tail
      path /var/log/messages
      pos_file /var/log/td-agent/tail.syslog.pos
      tag monitor.syslog
      format none
    </source>

    # Rewrite the tag for each line with its severity
    <match monitor.syslog>
      type rewrite_tag_filter
      rewriterule100 message ERROR ${tag}.error
      rewriterule500 message WARN ${tag}.warn
      rewriterule999 message .* clear
    </match>

    # Write the temporary alert queue
    <match monitor.*.*>
      type file
      path /var/log/easy-alert/alert
      time_slice_format %Y%m%d_%H%M
      time_slice_wait 5s
      time_format %Y%m%dT%H%M%S%z
      localtime
      buffer_chunk_limit 256m
    </match>

    # Logs to be ignored
    <match clear>
      type null
    </match>

    The output from Fluentd should be like this.

    <DATE_TIME><TAB><TAG_ID>.<LEVEL><TAB>{"message":"<MESSAGE>"}

    e.g.
    2015-08-01T12:34:56.789<TAB>monitor.syslog.warn<TAB>{"message":"Alert message."}
    """

    DEFAULT_TARGET_PATTERN = 'alert.????????_????_*.log'
    DEFAULT_PENDING_PATTERN = 'alert.????????_????*'
    DEFAULT_MESSAGE_NUM_THRESHOLD = 15
    DEFAULT_MESSAGE_LEN_THRESHOLD = 1024
    DEFAULT_PENDING_THRESHOLD = 3

    def __init__(self, alert_setting, print_only):
        if not isinstance(alert_setting, dict):
            raise SettingError('LogWatcher settings not a dict: %s' % alert_setting)

        try:
            watch_dir = alert_setting['watch_dir']
            tp = os.path.join(watch_dir, alert_setting.get('target_pattern') or self.DEFAULT_TARGET_PATTERN)
            pp = os.path.join(watch_dir, alert_setting.get('pending_pattern') or self.DEFAULT_PENDING_PATTERN)
            nt = int(alert_setting.get('message_num_threshold') or self.DEFAULT_MESSAGE_NUM_THRESHOLD)
            lt = int(alert_setting.get('message_len_threshold') or self.DEFAULT_MESSAGE_LEN_THRESHOLD)
            pt = int(alert_setting.get('pending_threshold') or self.DEFAULT_PENDING_THRESHOLD)
        except KeyError as e:
            raise SettingError('LogWatcher not found config key: %s' % e)
        except Exception as e:
            raise SettingError('LogWatcher settings syntax error: %s' % e)

        super(LogWatcher, self).__init__(
            watch_dir=watch_dir, target_pattern=tp, pending_pattern=pp, message_num_threshold=nt,
            message_len_threshold=lt, pending_threshold=pt, print_only=print_only, target_paths=None
        )

    def watch(self):
        """
        :return: list of Alert instances
        """
        start_time = datetime.now()

        # get target paths
        self.target_paths = glob.glob(self.target_pattern)
        if not self.target_paths:
            return self._check_pending(start_time)

        # parse files
        result, max_level = self._parse_files(self.target_paths)

        # make alert
        message = MSG_LOG_ALERT % {'server_id': get_server_id(), 'result': self._make_result(result)}
        return [Alert(start_time, max_level, MSG_LOG_ALERT_TITLE, message)]

    def after_success(self):
        """Delete parsed files after the notification."""

        assert (self.target_paths is not None)

        for path in self.target_paths:
            if self.print_only:
                print('Would remove: %s' % path)
            else:
                os.remove(path)

    def _check_pending(self, start_time):
        paths = glob.glob(self.pending_pattern)
        ret = []
        if len(paths) >= self.pending_threshold:
            mapping = {'server_id': get_server_id(), 'pattern': self.pending_pattern, 'paths': '\n'.join(paths)}
            ret.append(Alert(start_time, Level(WARN), MSG_LOG_ALERT_PENDING_TITLE, MSG_LOG_ALERT_PENDING % mapping))
        return ret

    def _parse_files(self, paths):
        d = defaultdict(lambda: (0, []))
        max_level = Level(WARN)
        for path in paths:
            for line in open(path):
                try:
                    tokens = line.split('\t')
                    if len(tokens) != 3:
                        raise LogFormatError('LogWatcher parse error: file=%s, line=%s' % (path, line))
                    tag = tokens[1]
                    msg = json.loads(tokens[2].decode('utf-8', 'ignore'))['message']
                    cnt, msgs = d[tag]
                    cnt += 1
                    # trim string
                    msgs += [msg[:self.message_len_threshold]] if cnt <= self.message_num_threshold else []
                    d[tag] = (cnt, msgs)
                    level = Level(tag.split('.')[-1])
                    max_level = max(max_level, level)
                except LogFormatError as e:
                    raise e
                except Exception as e:
                    raise LogFormatError('LogWatcher parse error: %s: %s: file=%s, line=%s'
                                         % (e.__class__.__name__, e, path, line))
        return d, max_level

    def _make_result(self, result):
        buf = []
        for k in sorted(result.keys()):
            cnt, msgs = result[k]
            buf.append(MSG_LOG_SUMMARY % {'tag': k, 'count': cnt})
            buf += msgs
            buf += [MSG_LOG_SNIP] if cnt > self.message_num_threshold else []
            buf.append('')
        return '\n'.join(buf)
