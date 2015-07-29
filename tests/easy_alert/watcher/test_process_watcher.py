import logging
import sys
import re
from easy_alert.watcher.process_watcher import ProcessReader, ProcessCounter, ProcessWatcher
from easy_alert.setting.setting_error import SettingError
from easy_alert.entity.level import Level
from easy_alert.util import Matcher

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class MockProcessReader(ProcessReader):
    def __init__(self, expected):
        self.expected = expected
        super(MockProcessReader, self).__init__()

    def _read_raw(self):
        return self.expected


class TestProcessReader(unittest.TestCase):
    def test_read(self):
        ret = MockProcessReader("""  PID  PPID ARGS
    1     0 /sbin/launchd
   37     1 /usr/sbin/syslogd
   38     1 /usr/libexec/UserEventAgent (System)
   40     1 your-awesome-app arg1 arg2 "arg 3"
11111 11112 your-awesome-app arg1 arg2 "arg 3"
11112    40 your-awesome-app arg1 arg2 "arg 3\"""").read()
        self.assertEqual(ret, {
            1: (0, '/sbin/launchd'),
            37: (1, '/usr/sbin/syslogd'),
            38: (1, '/usr/libexec/UserEventAgent (System)'),
            40: (1, 'your-awesome-app arg1 arg2 "arg 3"'),
            11111: (11112, 'your-awesome-app arg1 arg2 "arg 3"'),
            11112: (40, 'your-awesome-app arg1 arg2 "arg 3"'),
        })


class TestProcessCounter(unittest.TestCase):
    def test_distinct(self):
        pc = ProcessCounter({
            1: (0, '/sbin/launchd'),
            37: (1, '/usr/sbin/syslogd'),
            38: (1, '/usr/libexec/UserEventAgent (System)'),
            40: (1, 'your-awesome-app arg1 arg2 "arg 3"'),
            11111: (11112, 'your-awesome-app arg1 arg2 "arg 3"'),
            11112: (40, 'your-awesome-app arg1 arg2 "arg 3"'),
        })
        expected = {
            'your-awesome-app arg1 arg2 "arg 3"': 3,
            '/sbin/launchd': 1,
            '/usr/sbin/syslogd': 1,
            '/usr/libexec/UserEventAgent (System)': 1,
        }
        self.assertEqual(pc.cache_distinct, None)
        self.assertEqual(pc._distinct(), expected)
        self.assertEqual(pc.cache_distinct, expected)

    def test_distinct_binary_tree(self):
        pc = ProcessCounter({
            1: (0, 'A'), 2: (1, 'A'), 3: (1, 'B'), 4: (2, 'A'), 5: (2, 'B'), 6: (3, 'A'), 7: (3, 'B'),
            8: (4, 'A'), 9: (4, 'B'), 10: (5, 'A'), 11: (5, 'B'), 12: (6, 'A'), 13: (6, 'B'), 14: (7, 'A'), 15: (7, 'B')
        })
        self.assertEqual(pc._distinct(), {'A': 8, 'B': 7})

    def test_distinct_straight_trunk(self):
        pc = ProcessCounter(dict((x + 1, (x, 'X')) for x in range(1000)))
        self.assertEqual(pc._distinct(), {'X': 1000})

        pc = ProcessCounter(dict((x + 1, (x, 'X%d' % x)) for x in range(1000)))
        self.assertEqual(pc._distinct(), dict(('X%d' % x, 1) for x in range(1000)))

    def test_distinct_complex_tree(self):
        pc = ProcessCounter({
            1: (0, 'A'),
            10: (1, 'A'), 11: (1, 'A'), 12: (1, 'A'),
            20: (1, 'B'), 21: (1, 'B'), 22: (1, 'B'),
            110: (10, 'B'), 210: (10, 'B'), 310: (10, 'B'),
            111: (11, 'B'), 211: (11, 'B'), 311: (11, 'B'),
            112: (12, 'B'), 212: (12, 'B'), 312: (12, 'B'),
            120: (20, 'A'), 220: (20, 'A'), 320: (20, 'A'),
            121: (21, 'A'), 221: (21, 'A'), 321: (21, 'A'),
            122: (22, 'A'), 222: (22, 'A'), 322: (22, 'A'),
        })
        self.assertEqual(pc._aggregate(), {'A': 10, 'B': 12})

    def test_aggregate(self):
        pc = ProcessCounter({
            1: (0, '/sbin/launchd'),
            37: (1, '/usr/sbin/syslogd'),
            38: (1, '/usr/libexec/UserEventAgent (System)'),
            40: (1, 'your-awesome-app arg1 arg2 "arg 3"'),
            11111: (11112, 'your-awesome-app arg1 arg2 "arg 3"'),
            11112: (40, 'your-awesome-app arg1 arg2 "arg 3"'),
        })
        expected = {
            'your-awesome-app arg1 arg2 "arg 3"': 1,
            '/sbin/launchd': 1,
            '/usr/sbin/syslogd': 1,
            '/usr/libexec/UserEventAgent (System)': 1,
        }
        self.assertEqual(pc.cache_aggregated, None)
        self.assertEqual(pc._aggregate(), expected)
        self.assertEqual(pc.cache_aggregated, expected)

    def test_aggregate_binary_tree(self):
        pc = ProcessCounter({
            1: (0, 'A'), 2: (1, 'A'), 3: (1, 'B'), 4: (2, 'A'), 5: (2, 'B'), 6: (3, 'A'), 7: (3, 'B'),
            8: (4, 'A'), 9: (4, 'B'), 10: (5, 'A'), 11: (5, 'B'), 12: (6, 'A'), 13: (6, 'B'), 14: (7, 'A'), 15: (7, 'B')
        })
        self.assertEqual(pc._aggregate(), {'A': 4, 'B': 4})

    def test_aggregate_straight_trunk(self):
        pc = ProcessCounter(dict((x + 1, (x, 'X')) for x in range(1000)))
        self.assertEqual(pc._aggregate(), {'X': 1})

        pc = ProcessCounter(dict((x + 1, (x, 'X%d' % x)) for x in range(1000)))
        self.assertEqual(pc._aggregate(), dict(('X%d' % x, 1) for x in range(1000)))

    def test_aggregate_complex_tree(self):
        pc = ProcessCounter({
            1: (0, 'A'),
            10: (1, 'A'), 11: (1, 'A'), 12: (1, 'A'),
            20: (1, 'B'), 21: (1, 'B'), 22: (1, 'B'),
            110: (10, 'B'), 210: (10, 'B'), 310: (10, 'B'),
            111: (11, 'B'), 211: (11, 'B'), 311: (11, 'B'),
            112: (12, 'B'), 212: (12, 'B'), 312: (12, 'B'),
            120: (20, 'A'), 220: (20, 'A'), 320: (20, 'A'),
            121: (21, 'A'), 221: (21, 'A'), 321: (21, 'A'),
            122: (22, 'A'), 222: (22, 'A'), 322: (22, 'A'),
        })
        self.assertEqual(pc._aggregate(), {'A': 10, 'B': 12})

    def test_count(self):
        pc = ProcessCounter({
            1: (0, '/sbin/launchd'),
            37: (1, '/usr/sbin/syslogd'),
            38: (1, '/usr/libexec/UserEventAgent (System)'),
            40: (1, 'your-awesome-app arg1 arg2 "arg 3"'),
            11111: (11112, 'your-awesome-app arg1 arg2 "arg 3"'),
            11112: (40, 'your-awesome-app arg1 arg2 "arg 3"'),
        })
        self.assertEqual(pc.count(re.compile('.*')), 4)
        self.assertEqual(pc.count(re.compile('.*'), True), 4)
        self.assertEqual(pc.count(re.compile('.*'), False), 6)
        self.assertEqual(pc.count(re.compile('awesome[-]?app')), 1)
        self.assertEqual(pc.count(re.compile('awesome[-]?app'), False), 3)


class TestProcessWatcher(unittest.TestCase):
    def test_init_error(self):
        def assert_err(setting, expected):
            with self.assertRaises(SettingError) as cm:
                ProcessWatcher(setting)
            self.assertEqual(cm.exception.args[0], expected)

        assert_err('xxx', 'ProcessWatcher settings not a list: xxx')
        assert_err({}, 'ProcessWatcher settings not a list: {}')
        assert_err([[]], 'ProcessWatcher settings not a dict: []')
        assert_err([{}], "ProcessWatcher not found config key: 'name'")
        assert_err([{'name': 'name'}], "ProcessWatcher not found config key: 'regexp'")
        assert_err([{'name': 'name', 'regexp': '['}],
                   "ProcessWatcher settings syntax error: unexpected end of regular expression")
        assert_err([{'name': 'name', 'regexp': '.*'}],
                   "ProcessWatcher not found threshold: {'regexp': '.*', 'name': 'name'}")
        assert_err([{'name': 'name', 'regexp': '.*', 'aggregate': 'a'}],
                   "ProcessWatcher value should be bool: a")
        assert_err([{'name': 'name', 'regexp': '.*', 'critical': '>'}],
                   "ProcessWatcher settings syntax error: Invalid matcher string: >")
        assert_err([{'name': 'name', 'regexp': '.*', 'debug': '===123'}],
                   "ProcessWatcher settings syntax error: Invalid matcher string: ===123")

    def test_init_normal(self):
        s = [
            {'name': 'n1', 'regexp': '.*', 'error': '==    1 '},
            {'name': 'n2', 'regexp': '.*', 'aggregate': False,
             'critical': '>10', 'error': '>=8', 'warn': '==6', 'info': '<=4', 'debug': '<2'},
        ]
        self.assertEqual(ProcessWatcher(s).settings, [
            ('n1', re.compile('.*'), True, [(Level(logging.ERROR), Matcher('== 1'))]),
            ('n2', re.compile('.*'), False, [
                (Level(logging.CRITICAL), Matcher('> 10')),
                (Level(logging.ERROR), Matcher('>= 8')),
                (Level(logging.WARN), Matcher('= 6')),
                (Level(logging.INFO), Matcher('<= 4')),
                (Level(logging.DEBUG), Matcher('< 2')),
                ])
        ])

    def test_watch(self):
        process_reader = MockProcessReader("""  PID  PPID ARGS
    1     0 /sbin/launchd
   37     1 /usr/sbin/syslogd
   38     1 /usr/libexec/UserEventAgent (System)
   40     1 your-awesome-app arg1 arg2 "arg 3"
11111 11112 your-awesome-app arg1 arg2 "arg 3"
11112    40 your-awesome-app arg1 arg2 "arg 3\"""")

        w = ProcessWatcher(
            [
                {'name': 'all procs aggregate', 'error': '<=5', 'warn': '<=3', 'regexp': '.*'},
                {'name': 'all procs distinct', 'error': '<=5', 'warn': '<=3', 'aggregate': False,
                 'regexp': '.*'},
                {'name': 'awesome 1', 'warn': '=1', 'regexp': 'awesome[-]?app'},
                {'name': 'awesome 2', 'warn': '=2', 'regexp': 'awesome[-]?app', 'aggregate': True},
                {'name': 'awesome 3', 'warn': '=3', 'regexp': 'awesome[-]?app', 'aggregate': False},
            ], process_reader)

        result = w.watch()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].level, Level(logging.ERROR))
        self.assertEqual(len(result[0].message.splitlines()), 7)
