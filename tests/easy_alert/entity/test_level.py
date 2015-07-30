import logging
import sys
from easy_alert.entity.level import Level

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestLevel(unittest.TestCase):
    def test_init_error(self):
        def assert_err(arg, expect):
            with self.assertRaises(KeyError) as cm:
                Level(arg)
            self.assertEqual(cm.exception.args[0], expect)

        assert_err(1.23, 'Invalid level: 1.23')
        assert_err('', 'Unknown level string: ')
        assert_err('Info', 'Unknown level string: Info')
        assert_err('INFO', 'Unknown level string: INFO')

    def test_get_keyword(self):
        self.assertEqual(Level(logging.DEBUG).get_keyword(), 'debug')
        self.assertEqual(Level(logging.INFO).get_keyword(), 'info')
        self.assertEqual(Level(logging.WARN).get_keyword(), 'warn')
        self.assertEqual(Level(logging.ERROR).get_keyword(), 'error')
        self.assertEqual(Level(logging.CRITICAL).get_keyword(), 'critical')
