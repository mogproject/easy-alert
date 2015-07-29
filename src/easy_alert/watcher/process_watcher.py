import re
from collections import defaultdict
import subprocess
from datetime import datetime

from watcher import Watcher
from easy_alert.entity import Alert, Level
from easy_alert.util import CaseClass, get_server_id, Matcher, apply_option
from easy_alert.i18n import *
from easy_alert.setting.setting_error import SettingError


class ProcessReader(object):
    """
    Read process information from operating system
    """

    def read(self):
        """
        Get the running processes information
        :return: dict of process id -> tuple(parent process id, args string)
        """

        def f(line):
            tokens = line.split(None, 2)
            return int(tokens[0]), (int(tokens[1]), tokens[2])

        # trim header line then parse
        return dict(map(f, self._read_raw().splitlines()[1:]))

    def _read_raw(self):
        cmd = ['/bin/ps', 'ax', '-o', 'pid,ppid,args']
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]


class ProcessCounter(CaseClass):
    """
    Count the number of the processes
    """

    def __init__(self, process_dict):
        super(ProcessCounter, self).__init__(['process_dict', 'cache_distinct', 'cache_aggregated'])
        self.process_dict = process_dict
        self.cache_distinct = None
        self.cache_aggregated = None

    def count(self, pattern, aggregate=True):
        d = self._aggregate() if aggregate else self._distinct()
        return sum(x * bool(pattern.search(s)) for s, x in d.items())

    def _distinct(self):
        """
        :return: dict of args string -> count with default value (0)
        """
        if self.cache_distinct is None:
            d = defaultdict(int)
            for ppid, args in self.process_dict.values():
                d[args] += 1
            self.cache_distinct = d
        return self.cache_distinct

    def _aggregate(self):
        """
        Aggregate forked processes.
        That is, if the 'args' strings of one process is same as the parent process, it is not counted.

        :return: dict of args string -> count with default value (0)
        """
        if self.cache_aggregated is None:
            d = defaultdict(int)
            for ppid, args in self.process_dict.values():
                parent = self.process_dict.get(ppid)
                if parent is None or parent[1] != args:
                    d[args] += 1
            self.cache_aggregated = d

        return self.cache_aggregated


class ProcessWatcher(Watcher):
    """
    Watch the number of the running processes

    configuration should be a list of this dict
      name   [required]: short description for the process
      regexp [required]: process argument string to be counted in regular expression
      aggregate        : aggregate forked processes (counted as one) if true (default:true)
      critical      [*]: check the threshold then alert with critical level
      error         [*]: check the threshold then alert with error level
      warn          [*]: check the threshold then alert with warn level
      info          [*]: check the threshold then alert with info level
      debug         [*]: check the threshold then alert with debug level

    * At least one of {critical, error, warn, info, debug} is required.
    """

    def __init__(self, alert_setting, process_reader=ProcessReader()):
        if not isinstance(alert_setting, list):
            raise SettingError('ProcessWatcher settings not a list: %s' % alert_setting)

        settings = []
        for s in alert_setting:
            if not isinstance(s, dict):
                raise SettingError('ProcessWatcher settings not a dict: %s' % s)

            try:
                name = s['name']
                pattern = re.compile(s['regexp'])
                aggregate = self.__verify_bool(s.get('aggregate', True))
                conditions = self._parse_conditions(s)
            except SettingError as e:
                raise e
            except KeyError as e:
                raise SettingError('ProcessWatcher not found config key: %s' % e)
            except Exception as e:
                raise SettingError('ProcessWatcher settings syntax error: %s' % e)

            settings.append((name, pattern, aggregate, conditions))

        super(ProcessWatcher, self).__init__(settings=settings, process_reader=process_reader)

    @staticmethod
    def _parse_conditions(setting):
        """
        :return: sorted list of tuple(Level, Condition) by level (severest first)
        """
        ret = []
        for l in Level.seq:
            v = setting.get(l.get_keyword())
            if v is not None:
                ret.append((l, Matcher(v)))
        if not ret:
            raise SettingError('ProcessWatcher not found threshold: %s' % setting)
        return ret

    @staticmethod
    def __verify_bool(x):
        if not isinstance(x, bool):
            raise SettingError('ProcessWatcher value should be bool: %s' % x)
        return x

    def watch(self):
        """
        :return: list of Alert instances
        """
        start_time = datetime.now()
        pc = ProcessCounter(self.process_reader.read())

        result = []
        for name, pattern, aggregate, conditions in self.settings:
            st = self.ProcessStatus(name, pc.count(pattern, aggregate), conditions)
            if st.level:
                result.append(st)

        if result:
            max_level = max(r.level for r in result)
            message = MSG_PROC_ALERT % {'server_id': get_server_id(), 'result': '\n'.join('%s' % s for s in result)}
            return [Alert(start_time, max_level, MSG_PROC_ALERT_TITLE, message)]
        else:
            return []

    class ProcessStatus(CaseClass):
        def __init__(self, name, count, conditions):
            super(ProcessWatcher.ProcessStatus, self).__init__(['name', 'count', 'level', 'condition'])
            self.name = name
            self.count = count
            self.level = None
            self.condition = None

            # check condition
            for level, condition in conditions:
                # find the first False from the severest level
                if not condition.check(count):
                    self.level = level
                    self.condition = condition
                    break

        def __str__(self):
            count_msg = MSG_PROC_NOT_RUNNING if self.count == 0 else MSG_PROC_RUNNING % {'count': self.count}
            return MSG_PROC_STATUS_FORMAT % {
                'level': self.level.get_text(),
                'name': self.name,
                'count': count_msg,
                'condition': self.condition
            }
