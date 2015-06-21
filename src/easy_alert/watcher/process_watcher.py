import re
from collections import defaultdict
import subprocess
from datetime import datetime

from watcher import Watcher
from easy_alert.entity import Alert, Level
from easy_alert.util import CaseClass, get_server_id
from easy_alert.i18n import *


class ProcessWatcher(Watcher):
    """
    Watch the number of the running processes
    """

    def __init__(self, alert_settings):
        super(ProcessWatcher, self).__init__(alert_settings=alert_settings)

    def watch(self):
        """
        :return: list of Alert instances
        """
        start_time = datetime.now()
        ps = self.ProcessList()

        result = []
        for s in self.alert_settings:
            st = self.ProcessStatus(s['name'], ps.count(s['regexp']), self._make_conditions(s))
            if st.level:
                result.append(st)

        if result:
            max_level = max(r.level for r in result)
            message = MSG_PROC_ALERT % {'server_id': get_server_id(), 'result': '\n'.join('%s' % s for s in result)}
            return [Alert(start_time, max_level, MSG_PROC_ALERT_TITLE, message)]
        else:
            return []

    @staticmethod
    def _make_conditions(alert_setting):
        """
        :return: list of tuple(Level, condition string)
        """
        ret = [(l, alert_setting.get(l.get_keyword())) for l in Level.seq if l.get_keyword() in alert_setting]
        return ret

    class ProcessList(object):
        def __init__(self):
            self.process_list = self._get_process_list()

        def count(self, regexp):
            pattern = re.compile(regexp)
            return sum(x * bool(pattern.search(s)) for s, x in self.process_list.items())

        @staticmethod
        def _get_process_list():
            """
            Get list of the args string of the running processes
            :return: dict of (args, count)
            """
            cmd = ['/bin/ps', 'ax', '-o', 'args']
            out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

            # trim header line
            d = defaultdict(int)
            for line in out.split('\n')[1:]:
                d[line] += 1
            return d

    class ProcessStatus(CaseClass):
        def __init__(self, name, count, conditions):
            super(ProcessWatcher.ProcessStatus, self).__init__(['name', 'count', 'level', 'condition'])
            self.name = name
            self.count = count
            self.level, self.condition = self._check_conditions(count, conditions)

        def __str__(self):
            count_msg = MSG_PROC_NOT_RUNNING if self.count == 0 else MSG_PROC_RUNNING % {'count': self.count}
            return MSG_PROC_STATUS_FORMAT % {
                'level': self.level.get_text(),
                'name': self.name,
                'count': count_msg,
                'condition': self.condition
            }

        @classmethod
        def _check_conditions(cls, count, conditions):
            for level, condition in conditions:
                # find the first False from the severest level
                if not cls._parse_condition(condition)(count):
                    return level, condition
            return None, None

        @staticmethod
        def _parse_condition(condition):
            op, threshold = re.match("""([=!<>]+)\s*(\d+)""", condition).groups()
            return {
                "=": lambda x: x == int(threshold),
                "==": lambda x: x == int(threshold),
                "!=": lambda x: x != int(threshold),
                "<": lambda x: x < int(threshold),
                "<=": lambda x: x <= int(threshold),
                ">": lambda x: x > int(threshold),
                ">=": lambda x: x >= int(threshold),
            }[op]
