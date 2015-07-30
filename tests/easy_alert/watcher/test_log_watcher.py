import sys
import os
import logging
from easy_alert.setting.setting_error import SettingError
from easy_alert.watcher.log_watcher import LogWatcher
from easy_alert.entity.level import Level
from tests.easy_alert.util.util_for_test import captured_output

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestLogWatcher(unittest.TestCase):
    def test_init_error(self):
        def assert_err(setting, expected):
            with self.assertRaises(SettingError) as cm:
                LogWatcher(setting, False)
            self.assertEqual(cm.exception.args[0], expected)

        assert_err('xxx', 'LogWatcher settings not a dict: xxx')
        assert_err([], 'LogWatcher settings not a dict: []')
        assert_err({}, "LogWatcher not found config key: 'watch_dir'")
        assert_err({'watch_dir': '.', 'message_num_threshold': 'a'},
                   "LogWatcher settings syntax error: invalid literal for int() with base 10: 'a'")
        assert_err({'watch_dir': '.', 'message_len_threshold': 'a'},
                   "LogWatcher settings syntax error: invalid literal for int() with base 10: 'a'")
        assert_err({'watch_dir': '.', 'pending_threshold': 'a'},
                   "LogWatcher settings syntax error: invalid literal for int() with base 10: 'a'")

    def test_init_normal(self):
        s1 = LogWatcher({'watch_dir': 'watch_dir'}, True)
        self.assertEqual(s1.watch_dir, 'watch_dir')
        self.assertEqual(s1.target_pattern, os.path.join('watch_dir', 'alert.????????_????_*.log'))
        self.assertEqual(s1.pending_pattern, os.path.join('watch_dir', 'alert.????????_????*'))
        self.assertEqual(s1.message_num_threshold, 15)
        self.assertEqual(s1.message_len_threshold, 1024)
        self.assertEqual(s1.pending_threshold, 3)
        self.assertEqual(s1.print_only, True)
        self.assertEqual(s1.target_paths, None)

        s2 = LogWatcher({
                            'watch_dir': 'watch_dir',
                            'target_pattern': '*.log',
                            'pending_pattern': '*.tmp',
                            'message_num_threshold': 100,
                            'message_len_threshold': 100,
                            'pending_threshold': 100,
                        }, False)
        self.assertEqual(s2.watch_dir, 'watch_dir')
        self.assertEqual(s2.target_pattern, os.path.join('watch_dir', '*.log'))
        self.assertEqual(s2.pending_pattern, os.path.join('watch_dir', '*.tmp'))
        self.assertEqual(s2.message_num_threshold, 100)
        self.assertEqual(s2.message_len_threshold, 100)
        self.assertEqual(s2.pending_threshold, 100)
        self.assertEqual(s2.print_only, False)
        self.assertEqual(s2.target_paths, None)

        s3 = LogWatcher({
                            'watch_dir': 'watch_dir',
                            'target_pattern': '',
                            'pending_pattern': '',
                            'message_num_threshold': 0,
                            'message_len_threshold': 0,
                            'pending_threshold': 0,
                        }, False)
        self.assertEqual(s3.watch_dir, 'watch_dir')
        self.assertEqual(s3.target_pattern, os.path.join('watch_dir', 'alert.????????_????_*.log'))
        self.assertEqual(s3.pending_pattern, os.path.join('watch_dir', 'alert.????????_????*'))
        self.assertEqual(s3.message_num_threshold, 15)
        self.assertEqual(s3.message_len_threshold, 1024)
        self.assertEqual(s3.pending_threshold, 3)
        self.assertEqual(s3.print_only, False)
        self.assertEqual(s3.target_paths, None)

    def test_watch(self):
        w = LogWatcher({'watch_dir': 'tests/resources/log_watcher'}, True)
        result = w.watch()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].level, Level(logging.ERROR))
        self.assertEqual(w.target_paths, [
            'tests/resources/log_watcher/alert.20150801_1234_1.log',
            'tests/resources/log_watcher/alert.20150801_1234_2.log',
            'tests/resources/log_watcher/alert.20150801_1234_3.log'
        ])

    def test_watch_pending(self):
        w = LogWatcher({'watch_dir': 'tests/resources/log_watcher', 'target_pattern': 'xxx'}, True)
        result = w.watch()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].level, Level(logging.WARN))
        self.assertEqual(w.target_paths, [])

    def test_watch_error(self):
        def assert_err(setting, expected):
            with self.assertRaises(Exception) as cm:
                LogWatcher(setting, True).watch()
            self.assertEqual(cm.exception.args[0], expected)

        s1 = {'watch_dir': 'tests/resources/log_watcher', 'target_pattern': 'err.20150801_1234_1.log'}
        s2 = {'watch_dir': 'tests/resources/log_watcher', 'target_pattern': 'err.20150801_1234_2.log'}
        s3 = {'watch_dir': 'tests/resources/log_watcher', 'target_pattern': 'err.20150801_1234_3.log'}
        s4 = {'watch_dir': 'tests/resources/log_watcher', 'target_pattern': 'err.20150801_1234_4.log'}
        s5 = {'watch_dir': 'tests/resources/log_watcher', 'target_pattern': 'err.20150801_1234_5.log'}
        s6 = {'watch_dir': 'tests/resources/log_watcher', 'target_pattern': 'err.20150801_1234_6.log'}

        assert_err(s1, 'LogWatcher parse error: file=tests/resources/log_watcher/err.20150801_1234_1.log, '
                       'line=2015-08-01T12:34:56.789')
        assert_err(s2, 'LogWatcher parse error: file=tests/resources/log_watcher/err.20150801_1234_2.log, '
                       'line=2015-08-01T12:34:56.789\tmonitor.syslog.warn')
        assert_err(s3, 'LogWatcher parse error: KeyError: \'Unknown level string: war\': '
                       'file=tests/resources/log_watcher/err.20150801_1234_3.log, '
                       'line=2015-08-01T12:34:56.789\tmonitor.syslog.war\t{"message":"Invalid alert level."}')
        assert_err(s4, 'LogWatcher parse error: file=tests/resources/log_watcher/err.20150801_1234_4.log, '
                       'line=2015-08-01T12:34:56.789\tmonitor.syslog.warn\t1\t2')
        assert_err(s5, "LogWatcher parse error: KeyError: 'message': "
                       "file=tests/resources/log_watcher/err.20150801_1234_5.log, "
                       "line=2015-08-01T12:34:56.789\tmonitor.syslog.warn\t{}")
        with self.assertRaises(Exception) as cm:
            LogWatcher(s6, True).watch()
        self.assertIn(cm.exception.args[0], [
            'LogWatcher parse error: ValueError: Expecting object: line 1 column 1 (char 0): '
            'file=tests/resources/log_watcher/err.20150801_1234_6.log, '
            'line=2015-08-01T12:34:56.789\tmonitor.syslog.warn\t[',
            'LogWatcher parse error: ValueError: Expecting object: line 1 column 1 (char 1): '
            'file=tests/resources/log_watcher/err.20150801_1234_6.log, '
            'line=2015-08-01T12:34:56.789\tmonitor.syslog.warn\t[',
        ])

    def test_after_success_print_only(self):
        path = 'tests/resources/log_watcher/dummy1.tmp'
        try:
            with open(path, 'w') as f:
                f.write('2015-08-01T12:34:56.789\tmonitor.syslog.warn\t{"message":"Alert message."}')
            w = LogWatcher({'watch_dir': 'tests/resources/log_watcher', 'target_pattern': 'dummy1.tmp'}, True)
            w.watch()

            with captured_output() as (out, err):
                w.after_success()
            self.assertEqual(out.getvalue(), 'Would remove: tests/resources/log_watcher/dummy1.tmp\n')
            self.assertEqual(err.getvalue(), '')

            self.assertTrue(os.path.exists(path))
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_after_success(self):
        path = 'tests/resources/log_watcher/dummy2.tmp'
        try:
            with open(path, 'w') as f:
                f.write('2015-08-01T12:34:56.789\tmonitor.syslog.warn\t{"message":"Alert message."}')
            w = LogWatcher({'watch_dir': 'tests/resources/log_watcher', 'target_pattern': 'dummy2.tmp'}, False)
            w.watch()
            w.after_success()

            self.assertFalse(os.path.exists(path))
        finally:
            if os.path.exists(path):
                os.remove(path)
