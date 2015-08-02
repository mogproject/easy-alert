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
            {'name': 'n4', 'level': 'warn', 'command': 'echo abcdefgh', 'expect_code': 0},
            {'name': 'n5', 'level': 'warn', 'command': 'echo abcdefgh', 'expect_stdout': ''},
            {'name': 'n6', 'level': 'warn', 'command': 'echo abcdefgh', 'expect_stderr': ''},
        ]
        self.assertEqual(CommandWatcher(s).settings, [
            ('n1', Level(logging.WARN), 'echo abcdefgh', 0, re.compile('cde'), None, 1024),
            ('n2', Level(logging.ERROR), 'echo abcdefgh', 0, re.compile('cdf'), None, 1024),
            ('n3', Level(logging.WARN), 'echo abcdefgh', 1, re.compile('cde'), None, 5),
            ('n4', Level(logging.WARN), 'echo abcdefgh', 0, None, None, 1024),
            ('n5', Level(logging.WARN), 'echo abcdefgh', None, re.compile(''), None, 1024),
            ('n6', Level(logging.WARN), 'echo abcdefgh', None, None, re.compile(''), 1024),
        ])

    def test_watch(self):
        # Note: use external 'echo' command
        r1 = CommandWatcher([{
            'name': 'n1',
            'level': 'warn',
            'command': 'echo abc',
            'expect_code': 0,
            'expect_stdout': 'abc',
            'expect_stderr': '',
        }]).watch()
        r2 = CommandWatcher([{
            'name': 'n2',
            'level': 'warn',
            'command': 'echo abc',
            'expect_code': 0,
        }]).watch()
        r3 = CommandWatcher([{
            'name': 'n3',
            'level': 'warn',
            'command': 'echo abc',
            'expect_stdout': 'abc',
        }]).watch()
        r4 = CommandWatcher([{
            'name': 'n4',
            'level': 'warn',
            'command': 'echo abc',
            'expect_stderr': '',
        }]).watch()
        r5 = CommandWatcher([{
            'name': 'n5',
            'level': 'warn',
            'command': 'echo',
            'expect_code': 1,
        }]).watch()
        r6 = CommandWatcher([{
            'name': 'n6',
            'level': 'warn',
            'command': 'echo',
            'expect_stdout': 'abc',
        }]).watch()
        r7 = CommandWatcher([{
            'name': 'n7',
            'level': 'warn',
            'command': 'echo',
            'expect_stderr': 'abc',
        }]).watch()
        r8 = CommandWatcher([{
            'name': 'n8',
            'level': 'warn',
            'command': 'echo',
            'expect_code': '1',
            'expect_stdout': 'abc',
            'expect_stderr': 'abc',
        }]).watch()

        self.assertEqual(r1, [])
        self.assertEqual(r2, [])
        self.assertEqual(r3, [])
        self.assertEqual(r4, [])

        self.assertEqual(len(r5), 1)
        self.assertEqual(r5[0].level, Level(logging.WARN))
        m = r5[0].message.splitlines()
        self.assertIn('  actual: {code:0, stdout:', m)
        self.assertIn(', stderr:}', m)
        self.assertIn('  expect: {code:1, stdout:None, stderr:None}', m)

        self.assertEqual(len(r6), 1)
        self.assertEqual(r6[0].level, Level(logging.WARN))
        m = r6[0].message.splitlines()
        self.assertIn('  actual: {code:0, stdout:', m)
        self.assertIn(', stderr:}', m)
        self.assertIn('  expect: {code:None, stdout:abc, stderr:None}', m)

        self.assertEqual(len(r7), 1)
        self.assertEqual(r7[0].level, Level(logging.WARN))
        m = r7[0].message.splitlines()
        self.assertIn('  actual: {code:0, stdout:', m)
        self.assertIn(', stderr:}', m)
        self.assertIn('  expect: {code:None, stdout:None, stderr:abc}', m)

        self.assertEqual(len(r8), 1)
        self.assertEqual(r8[0].level, Level(logging.WARN))
        m = r8[0].message.splitlines()
        self.assertIn('  actual: {code:0, stdout:', m)
        self.assertIn(', stderr:}', m)
        self.assertIn('  expect: {code:1, stdout:abc, stderr:abc}', m)
