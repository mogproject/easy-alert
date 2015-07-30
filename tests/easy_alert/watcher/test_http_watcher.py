import sys
import logging
import re
from easy_alert.setting.setting_error import SettingError
from easy_alert.watcher.http_watcher import HTTPWatcher
from easy_alert.entity.level import Level
from easy_alert.util import Matcher

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestHTTPWatcher(unittest.TestCase):
    def test_init_error(self):
        def assert_err(setting, expected):
            with self.assertRaises(SettingError) as cm:
                HTTPWatcher(setting)
            self.assertEqual(cm.exception.args[0], expected)

        assert_err('xxx', 'HTTPWatcher settings not a list: xxx')
        assert_err({}, 'HTTPWatcher settings not a list: {}')
        assert_err([[]], 'HTTPWatcher settings not a dict: []')
        assert_err([{}], "HTTPWatcher not found config key: 'name'")
        assert_err([{'name': 'name'}], "HTTPWatcher not found config key: 'level'")
        assert_err([{'name': 'name', 'level': 'error'}], "HTTPWatcher not found config key: 'url'")
        assert_err([{'name': 'name', 'level': 'xxx', 'url': 'localhost'}], "HTTPWatcher invalid level: xxx")
        assert_err([{'name': 'name', 'level': 'error', 'url': 'localhost'}],
                   "HTTPWatcher any of expect_code, expect_size or expect_regexp should be set.")
        assert_err([{'name': 'name', 'level': 'error', 'url': 'localhost', 'timeout': 'a'}],
                   "HTTPWatcher settings syntax error: invalid literal for int() with base 10: 'a'")
        assert_err([{'name': 'name', 'level': 'error', 'url': 'localhost', 'retry': 'a'}],
                   "HTTPWatcher settings syntax error: invalid literal for int() with base 10: 'a'")
        assert_err([{'name': 'name', 'level': 'error', 'url': 'localhost', 'expect_code': 'a'}],
                   "HTTPWatcher settings syntax error: invalid literal for int() with base 10: 'a'")
        assert_err([{'name': 'name', 'level': 'error', 'url': 'localhost', 'expect_size': 'a'}],
                   "HTTPWatcher settings syntax error: Invalid matcher string: a")
        assert_err([{'name': 'name', 'level': 'error', 'url': 'localhost', 'expect_size': '=== 123'}],
                   "HTTPWatcher settings syntax error: Invalid matcher string: === 123")
        assert_err([{'name': 'name', 'level': 'error', 'url': 'localhost', 'expect_regexp': '.['}],
                   "HTTPWatcher settings syntax error: unexpected end of regular expression")
        assert_err([{'name': 'name', 'level': 'error', 'url': 'xxx://localhost', 'expect_code': 200}],
                   "HTTPWatcher unsupported scheme: xxx")

    def test_init_normal(self):
        s = [
            {'name': 'n1', 'level': 'debug', 'url': 'example.com', 'expect_code': 200},
            {'name': 'n2', 'level': 'debug', 'url': 'http://example.com', 'expect_code': 200},
            {'name': 'n3', 'level': 'debug', 'url': 'https://example.com', 'expect_code': 200},
            {'name': 'n4', 'level': 'debug', 'url': 'HTTP://EXAMPLE.COM', 'expect_code': 200},
            {'name': 'n5', 'level': 'critical', 'url': 'localhost', 'timeout': 60, 'retry': 5, 'additional_info': 'abc',
             'expect_code': 200, 'expect_size': '>= 100', 'expect_regexp': '.*'},
            {'name': 'n6', 'level': 'warn', 'url': 'localhost', 'expect_code': 0},
            {'name': 'n7', 'level': 'warn', 'url': 'localhost', 'expect_size': '=0'},
            {'name': 'n8', 'level': 'warn', 'url': 'localhost', 'expect_regexp': ''},
        ]
        self.assertEqual(HTTPWatcher(s).settings, [
            ('n1', Level(logging.DEBUG), 'example.com', 10, 2, '', 200, None, None),
            ('n2', Level(logging.DEBUG), 'http://example.com', 10, 2, '', 200, None, None),
            ('n3', Level(logging.DEBUG), 'https://example.com', 10, 2, '', 200, None, None),
            ('n4', Level(logging.DEBUG), 'HTTP://EXAMPLE.COM', 10, 2, '', 200, None, None),
            ('n5', Level(logging.CRITICAL), 'localhost', 60, 5, 'abc', 200, Matcher('>=100'), re.compile('.*')),
            ('n6', Level(logging.WARN), 'localhost', 10, 2, '', 0, None, None),
            ('n7', Level(logging.WARN), 'localhost', 10, 2, '', None, Matcher('=0'), None),
            ('n8', Level(logging.WARN), 'localhost', 10, 2, '', None, None, re.compile('')),
        ])
