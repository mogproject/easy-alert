import sys
import easy_alert.util.util
from datetime import datetime, timedelta

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestUtil(unittest.TestCase):
    def test_with_retry(self):
        self.assertEqual(easy_alert.util.util.with_retry(3, 1)(lambda: 123), 123)

    def test_with_retry_error(self):
        def f():
            raise Exception('xxx')

        t = datetime.now()
        with self.assertRaises(Exception) as cm:
            easy_alert.util.util.with_retry(2, 1)(f)
        s = datetime.now()
        self.assertEqual(cm.exception.args[0], 'xxx')
        self.assertTrue(timedelta(seconds=2) < s - t)
