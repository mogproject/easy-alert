import sys
from datetime import datetime
from easy_alert.notifier.email_notifier import EmailNotifier
from easy_alert.logger.system_logger import SystemLogger
from easy_alert.entity import Alert, Level

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestEmailNotifier(unittest.TestCase):
    def test_get_subject(self):
        e = EmailNotifier(
            {
                'group_id': 'awesome',
                'smtp_server': 'mail.example.com',
                'smtp_port': 587,
                'from_address': 'from_address@example.com',
                'to_address_list': 'to1@example.com,to2@example.com',
            }, False, SystemLogger())
        s = e.get_subject(Alert(datetime(2015, 8, 1, 12, 34,
                                         56, 789), Level('warn'), 'titleA0', 'message'))
        self.assertTrue(s.find('titleA0') != -1)
        self.assertTrue(s.find('titleA1') == -1)

    def test_init(self):
        e = EmailNotifier(
            {
                'group_id': 'awesome',
                'smtp_server': 'mail.example.com',
                'smtp_port': 587,
                'from_address': 'from_address@example.com',
                'to_address_list': 'to1@example.com,to2@example.com',
                'smtp_user': 'SMTP_USER',
                'smtp_password': 'SMTP_PASSWORD',
            }, False, SystemLogger())

        self.assertEqual(e.smtp_user, 'SMTP_USER')
        self.assertEqual(e.smtp_password, 'SMTP_PASSWORD')
