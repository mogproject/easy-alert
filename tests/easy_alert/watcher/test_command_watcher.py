import sys
import logging
import re
from easy_alert.setting.setting_error import SettingError
from easy_alert.watcher.command_watcher import CommandWatcher
from easy_alert.entity.level import Level

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestCommandWatcher(unittest.TestCase):
    def test_init_error(self):
        def assert_err(setting, expected):
            with self.assertRaises(SettingError) as cm:
                CommandWatcher(setting)
            self.assertEqual(cm.exception.args[0], expected)

        assert_err('xxx', 'CommandWatcher settings not a list: xxx')
        assert_err({}, 'CommandWatcher settings not a list: {}')
        assert_err([[]], 'CommandWatcher settings not a dict: []')
        assert_err([{}], "CommandWatcher not found config key: 'name'")
        assert_err([{'name': 'name'}], "CommandWatcher not found config key: 'level'")
        assert_err([{'name': 'name', 'level': 'error'}], "CommandWatcher not found config key: 'command'")
        assert_err([{'name': 'name', 'level': 'xxx', 'command': 'echo'}], "CommandWatcher invalid level: xxx")
        assert_err([{'name': 'name', 'level': 'error', 'command': 'echo'}],
                   "CommandWatcher any of expect_code, expect_stdout or expect_stderr should be set.")
        assert_err([{'name': 'name', 'level': 'error', 'command': 'echo', 'expect_code': 'a'}],
                   "CommandWatcher settings syntax error: invalid literal for int() with base 10: 'a'")
        assert_err([{'name': 'name', 'level': 'error', 'command': 'echo', 'expect_stdout': '.['}],
                   "CommandWatcher settings syntax error: unexpected end of regular expression")
        assert_err([{'name': 'name', 'level': 'error', 'command': 'echo', 'expect_stderr': '.['}],
                   "CommandWatcher settings syntax error: unexpected end of regular expression")
        assert_err([{'name': 'name', 'level': 'error', 'command': 'echo', 'max_output_len': 'a'}],
                   "CommandWatcher settings syntax error: invalid literal for int() with base 10: 'a'")

    def test_init_normal(self):
        s = [
            {'name': 'n1', 'level': 'warn', 'command': 'echo abcdefgh', 'expect_code': 0, 'expect_stdout': 'cde'},
            {'name': 'n2', 'level': 'error', 'command': 'echo abcdefgh', 'expect_code': 0, 'expect_stdout': 'cdf'},
            {'name': 'n3', 'level': 'warn', 'command': 'echo abcdefgh', 'expect_code': 1, 'expect_stdout': 'cde',
             'max_output_len': 5},
        ]
        self.assertEqual(CommandWatcher(s).settings, [
            ('n1', Level(logging.WARN), 'echo abcdefgh', 0, re.compile('cde'), None, 1024),
            ('n2', Level(logging.ERROR), 'echo abcdefgh', 0, re.compile('cdf'), None, 1024),
            ('n3', Level(logging.WARN), 'echo abcdefgh', 1, re.compile('cde'), None, 5),
        ])
