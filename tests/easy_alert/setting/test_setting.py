import sys
from contextlib import contextmanager
from StringIO import StringIO
from easy_alert.setting import Setting, SettingError
from yaml.scanner import ScannerError
from easy_alert.watcher import ProcessWatcher, LogWatcher
from easy_alert.notifier import EmailNotifier
from easy_alert.logger import SystemLogger, PrintLogger

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestSetting(unittest.TestCase):
    default_setting = Setting(
        watcher_types=[], config_path='/etc/easy-alert/easy-alert.yml', print_only=False, watchers=[], notifiers=[], )

    def _assert_system_exit(self, expected_code, f):
        with self.assertRaises(SystemExit) as cm:
            f()
        if isinstance(cm.exception, int):
            self.assertEqual(cm.exception, expected_code)
        else:
            self.assertEqual(cm.exception.code, expected_code)

    def test_parse_args_usage(self):
        with captured_output() as (out, err):
            self._assert_system_exit(2, lambda: Setting().parse_args(['easy-alert']))
        lines = err.getvalue().splitlines()
        self.assertIn('Usage: ', lines)
        self.assertNotIn('Options:', lines)

    def test_parse_args_version(self):
        with captured_output() as (out, err):
            self._assert_system_exit(0, lambda: Setting().parse_args(['easy-alert', '--version']))
        lines = out.getvalue().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith('easy-alert '))

    def test_parse_args_help(self):
        with captured_output() as (out, err):
            self._assert_system_exit(0, lambda: Setting().parse_args(['easy-alert', '--help']))
        lines = out.getvalue().splitlines()
        self.assertIn('Usage: ', lines)
        self.assertIn('Options:', lines)

    def test_parse_args_invalid_syntax(self):
        with captured_output() as (out, err):
            self._assert_system_exit(2, lambda: Setting().parse_args(['easy-alert', 'process', '--config']))
        lines = err.getvalue().splitlines()
        self.assertIn('Usage: ', lines)
        self.assertNotIn('Options:', lines)

    def test_parse_args_invalid_watcher(self):
        with captured_output() as (out1, err1):
            self._assert_system_exit(2, lambda: Setting().parse_args(['easy-alert', 'xxx']))
        lines1 = err1.getvalue().splitlines()
        self.assertIn('Usage: ', lines1)
        self.assertNotIn('Options:', lines1)

        with captured_output() as (out2, err2):
            self._assert_system_exit(
                2,
                lambda: Setting().parse_args(['easy-alert', 'ssh', 'process', 'log', 'yyy', 'yyy']))
        lines2 = err2.getvalue().splitlines()
        self.assertIn('Usage: ', lines2)
        self.assertNotIn('Options:', lines2)

    def test_parse_args_normal(self):
        s1 = Setting().parse_args(['easy-alert', 'process'])
        self.assertEqual(s1, Setting(['process'], '/etc/easy-alert/easy-alert.yml', False))

        # duplicated entry is allowed
        s2 = Setting().parse_args(['easy-alert', 'process', 'ssh', 'process'])
        self.assertEqual(s2, Setting(['process', 'ssh'], '/etc/easy-alert/easy-alert.yml', False))

    def test_parse_args_config(self):
        s1 = Setting().parse_args(['easy-alert', 'process', '--config', '/etc/easy-alert.yml'])
        self.assertEqual(s1, Setting(['process'], '/etc/easy-alert.yml', False))

        s2 = Setting().parse_args(['easy-alert', 'process', 'ssh', 'process', '--config', '/etc/easy-alert.yml'])
        self.assertEqual(s2, Setting(['process', 'ssh'], '/etc/easy-alert.yml', False))

    def test_parse_args_check(self):
        s1 = Setting().parse_args(['easy-alert', '--check', 'process'])
        self.assertEqual(s1, Setting(['process'], '/etc/easy-alert/easy-alert.yml', True, logger=PrintLogger()))

        s2 = Setting().parse_args(['easy-alert', 'process', 'ssh', '--config', '/etc/easy-alert.yml', '--check'])
        self.assertEqual(s2, Setting(['process', 'ssh'], '/etc/easy-alert.yml', True, logger=PrintLogger()))

    def test_load_config_assertion(self):
        with self.assertRaises(AssertionError) as cm:
            Setting().load_config()
        self.assertEqual(cm.exception.message, 'watcher_types should be set before load_config')
        with self.assertRaises(AssertionError) as cm:
            Setting(['process']).load_config()
        self.assertEqual(cm.exception.message, 'config_path should be set before load_config')
        with self.assertRaises(AssertionError) as cm:
            Setting(['process'], 'xxx').load_config()
        self.assertEqual(cm.exception.message, 'print_only should be set before load_config')

    def test_load_config_not_found(self):
        self.assertRaises(IOError, Setting(['process'], 'tests/resources/__not_exist__', False).load_config)

    def test_load_config_no_watcher_entry(self):
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-000.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'Syntax error: tests/resources/easy-alert-test-000.yml')
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-001.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'Syntax error: tests/resources/easy-alert-test-001.yml')
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-002.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'Not found "watchers" entry: tests/resources/easy-alert-test-002.yml')

    def test_load_config_invalid_yaml(self):
        self.assertRaises(ScannerError,
                          Setting(['process'], 'tests/resources/easy-alert-test-010.yml', False).load_config)

    def test_load_config_watcher_parse_error(self):
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-020.yml', False).load_config()
        self.assertEqual(cm.exception.message,
                         'Not found watcher configuration for "process": tests/resources/easy-alert-test-020.yml')
        with self.assertRaises(SettingError) as cm:
            Setting(['xxx'], 'tests/resources/easy-alert-test-021.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'Unsupported watcher type: xxx')
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-022.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'Syntax error: tests/resources/easy-alert-test-022.yml')
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-023.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'Syntax error: tests/resources/easy-alert-test-023.yml')

    def test_load_config_notifier_parser_error(self):
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-030.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'Not found "notifiers" entry: tests/resources/easy-alert-test-030.yml')
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-031.yml', False).load_config()
        self.assertEqual(cm.exception.message,
                         'Unsupported notifier type: xxx in tests/resources/easy-alert-test-031.yml')
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-032.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'Syntax error: tests/resources/easy-alert-test-032.yml')
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-033.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'Syntax error: tests/resources/easy-alert-test-033.yml')

    def test_load_config_email_notifier(self):
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-040.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'EmailNotifier not found config key: group_id')
        with self.assertRaises(SettingError) as cm:
            Setting(['process'], 'tests/resources/easy-alert-test-041.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'EmailNotifier settings not a dict: xxx')

    def test_load_config_normal(self):
        proc_watcher = ProcessWatcher([
            {'name': 'a', 'regexp': '.*', 'error': '=1'},
            {'name': 'b', 'regexp': '.*', 'error': '<=1'},
            {'name': 'c', 'regexp': '.*', 'error': '>=1'},
        ])
        log_watcher = LogWatcher({
            'watch_dir': 'resources/log_watcher'
        }, False, SystemLogger())
        notifier = EmailNotifier(
            {
                'group_id': 'awesome',
                'smtp_server': 'mail.example.com',
                'smtp_port': 587,
                'from_address': 'from_address@example.com',
                'to_address_list': 'to1@example.com,to2@example.com',
            }, False, SystemLogger())
        expect1 = Setting(
            watcher_types=['process'],
            config_path='tests/resources/easy-alert-test-100.yml',
            print_only=False,
            watchers=[proc_watcher],
            notifiers=[notifier],
        )
        expect2 = Setting(
            watcher_types=['process', 'log'],
            config_path='tests/resources/easy-alert-test-100.yml',
            print_only=False,
            watchers=[proc_watcher, log_watcher],
            notifiers=[notifier],
        )
        self.assertEqual(
            Setting(['process'], 'tests/resources/easy-alert-test-100.yml', False).load_config(), expect1)
        self.assertEqual(
            Setting(['process', 'log'], 'tests/resources/easy-alert-test-100.yml', False).load_config(), expect2)

    def test_load_config_log_watcher_error(self):
        with self.assertRaises(SettingError) as cm:
            Setting(['log'], 'tests/resources/easy-alert-test-050.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'LogWatcher settings not a dict: xxx')
        with self.assertRaises(SettingError) as cm:
            Setting(['log'], 'tests/resources/easy-alert-test-051.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'LogWatcher settings not a dict: [{}, {}]')
        with self.assertRaises(SettingError) as cm:
            Setting(['log'], 'tests/resources/easy-alert-test-052.yml', False).load_config()
        self.assertEqual(cm.exception.message, 'LogWatcher not found config key: watch_dir')
        with self.assertRaises(SettingError) as cm:
            Setting(['log'], 'tests/resources/easy-alert-test-053.yml', False).load_config()
        self.assertEqual(cm.exception.message,
                         "LogWatcher settings syntax error: invalid literal for int() with base 10: 'a'")
        with self.assertRaises(SettingError) as cm:
            Setting(['log'], 'tests/resources/easy-alert-test-054.yml', False).load_config()
        self.assertEqual(cm.exception.message,
                         "LogWatcher settings syntax error: invalid literal for int() with base 10: 'a'")
        with self.assertRaises(SettingError) as cm:
            Setting(['log'], 'tests/resources/easy-alert-test-055.yml', False).load_config()
        self.assertEqual(cm.exception.message,
                         "LogWatcher settings syntax error: invalid literal for int() with base 10: 'a'")
