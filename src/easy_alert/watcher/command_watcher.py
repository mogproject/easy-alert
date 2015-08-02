import subprocess
import re
from datetime import datetime
from watcher import Watcher
from easy_alert.entity import Alert, Level
from easy_alert.i18n import *
from easy_alert.setting.setting_error import SettingError
from easy_alert.util import get_server_id, exists


class CommandWatcher(Watcher):
    """
    Check the result of executing the external command

    configuration should be a list of this dict
      name    [required]: short description for the command
      level   [required]: alert level (should be in {critical, error, warn, info, debug})
      command [required]: command line string
      expect_code       : expected exit code number
      expect_stdout  [*]: expected stdout pattern in regexp
      expect_stderr  [*]: expected stderr pattern in regexp
      max_output_len [*]: maximum length for each stdout/stderr

    * Any of {expect_code, expect_stdout, expect_stderr} is required.
    """

    DEFAULT_MAX_OUTPUT_LEN = 1024

    def __init__(self, command_setting):
        if not isinstance(command_setting, list):
            raise SettingError('CommandWatcher settings not a list: %s' % command_setting)

        settings = []
        for s in command_setting:
            if not isinstance(s, dict):
                raise SettingError('CommandWatcher settings not a dict: %s' % s)

            try:
                name = s['name']
                level_str = s['level']
                level = [l for l in Level.seq if l.get_keyword() == level_str]
                command = s['command']
                expect_code = s.get('expect_code')
                if expect_code is not None:
                    expect_code = int(expect_code)
                expect_stdout = s.get('expect_stdout')
                if expect_stdout is not None:
                    expect_stdout = re.compile(expect_stdout)
                expect_stderr = s.get('expect_stderr')
                if expect_stderr is not None:
                    expect_stderr = re.compile(expect_stderr)
                max_output_len = int(s.get('max_output_len', self.DEFAULT_MAX_OUTPUT_LEN))
            except KeyError as e:
                raise SettingError('CommandWatcher not found config key: %s' % e)
            except Exception as e:
                raise SettingError('CommandWatcher settings syntax error: %s' % e)

            if not level:
                raise SettingError('CommandWatcher invalid level: %s' % level_str)
            if all([expect_code is None, expect_stdout is None, expect_stderr is None]):
                raise SettingError('CommandWatcher any of expect_code, expect_stdout or expect_stderr should be set.')

            settings.append((name, level[0], command, expect_code, expect_stdout, expect_stderr, max_output_len))

        super(CommandWatcher, self).__init__(settings=settings)

    def watch(self):
        """
        :return: list of Alert instances
        """
        start_time = datetime.now()

        result = []
        for name, level, command, expect_code, expect_stdout, expect_stderr, max_output_len in self.settings:
            code, stdout, stderr = self._execute_external_command(command)
            if self._should_alert(code, stdout, stderr, expect_code, expect_stdout, expect_stderr):
                message = MSG_CMD_ALERT_FORMAT % {
                    'level': level.get_text(),
                    'name': name,
                    'code': code,
                    'stdout': stdout[:max_output_len],
                    'stderr': stderr[:max_output_len],
                    'expect_code': expect_code,
                    'expect_stdout': expect_stdout.pattern if expect_stdout else None,
                    'expect_stderr': expect_stderr.pattern if expect_stderr else None,
                }
                result.append((level, message))

        if result:
            max_level = max(r[0] for r in result)
            message = MSG_CMD_ALERT % {'server_id': get_server_id(), 'result': '\n'.join(r[1] for r in result)}
            return [Alert(start_time, max_level, MSG_CMD_ALERT_TITLE, message)]
        else:
            return []

    @staticmethod
    def _execute_external_command(command):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        stdout, stderr = p.communicate()
        return p.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')

    @staticmethod
    def _should_alert(code, stdout, stderr, expect_code, expect_stdout, expect_stderr):
        return any([
            exists(expect_code, lambda x: x != code),
            exists(expect_stdout, lambda x: not x.findall(stdout)),
            exists(expect_stderr, lambda x: not x.findall(stderr)),
        ])
