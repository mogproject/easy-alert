import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from easy_alert.setting.setting_error import SettingError
from easy_alert.watcher.ssh_watcher import SSHWatcher


class TestSSHWatcher(unittest.TestCase):
    def test_init_error(self):
        def assert_err(setting, expected):
            with self.assertRaises(SettingError) as cm:
                SSHWatcher(setting)
            self.assertEqual(cm.exception.message, expected)

        assert_err('xxx', 'SSHWatcher settings not a list: xxx')
        assert_err({}, 'SSHWatcher settings not a list: {}')
        assert_err([[]], 'SSHWatcher settings not a dict: []')
        assert_err([{}], 'SSHWatcher not found config key: user')
        assert_err([{'user': 'user'}], 'SSHWatcher not found config key: key')
        assert_err([{'user': 'user', 'key': 'path/to/key'}], 'SSHWatcher not found config key: name')
        assert_err([{'user': 'user', 'key': 'path/to/key', 'name': 's'}], 'SSHWatcher not found config key: host')
        assert_err([{'user': 'user', 'key': 'path/to/key', 'port': 'a', 'name': 's', 'host': 'h'}],
                   "SSHWatcher settings syntax error: invalid literal for int() with base 10: 'a'")

    def test_init_normal(self):
        s = [
            {'user': 'u1', 'key': 'k1', 'name': 'n1', 'host': 'h1'},
            {'user': 'u2', 'key': 'k2', 'port': 22222, 'name': 'n2', 'host': 'h2'},
            {'user': 'u3', 'key': 'k3', 'port': 33333, 'dynamic': 'd3'},
        ]
        self.assertEqual(SSHWatcher(s).settings, [
            ('u1', 'k1', 22, False, 'n1', 'h1', None),
            ('u2', 'k2', 22222, False, 'n2', 'h2', None),
            ('u3', 'k3', 33333, True, None, None, 'd3')
        ])
