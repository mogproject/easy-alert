import unittest
import os


class TestI18N(unittest.TestCase):
    def get_email_encoding(self):
        import easy_alert

        reload(easy_alert.i18n)
        return easy_alert.i18n.EMAIL_ENCODING

    def test_lang_detection_jp(self):
        os.environ['LANG'] = 'ja_JP.UTF-8'
        self.assertEqual(self.get_email_encoding(), 'iso-2022-jp')

    def test_lang_detection_en(self):
        os.environ['LANG'] = 'C'
        self.assertEqual(self.get_email_encoding(), 'utf-8')

        del os.environ['LANG']
        self.assertNotEqual(self.get_email_encoding(), None)  # the result depends on the system
