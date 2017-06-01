import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
from notifier import Notifier
from easy_alert.i18n import EMAIL_ENCODING
from easy_alert.setting.setting_error import SettingError


class EmailNotifier(Notifier):
    COMMASPACE = ', '

    def __init__(self, notify_setting, print_only, logger):
        if not isinstance(notify_setting, dict):
            raise SettingError('EmailNotifier settings not a dict: %s' % notify_setting)
        try:
            super(EmailNotifier, self).__init__(
                notify_setting['group_id'],
                from_address=notify_setting['from_address'],
                to_address_list=[s.strip() for s in notify_setting['to_address_list'].split(',')],
                smtp_server=notify_setting['smtp_server'],
                smtp_port=notify_setting['smtp_port'],
                smtp_user=notify_setting.get('smtp_user'),
                smtp_password=notify_setting.get('smtp_password'),
                print_only=print_only,
                logger=logger)
        except KeyError as e:
            raise SettingError('EmailNotifier not found config key: %s' % e)

    def notify(self, alert):
        subject = self.get_subject(alert)
        body = alert.message

        if self.print_only:
            self.logger.info('Would send a message:')
            self.logger.info('Subject: %s' % subject)
            self.logger.info('From: %s' % self.from_address)
            self.logger.info('To: %s' % self.COMMASPACE.join(self.to_address_list))
            self.logger.info('Body:')
            for line in body.split('\n'):
                self.logger.info(line)
        else:
            msg = self.__create_message(self.from_address, self.to_address_list, subject, body)
            s = smtplib.SMTP(self.smtp_server, self.smtp_port)
            try:
                if self.smtp_user:
                    s.starttls()
                    s.login(self.smtp_user, self.smtp_password)
                s.sendmail(self.from_address, self.to_address_list, msg.as_string())
            finally:
                s.close()
            self.logger.info('Sent mail to %s.' % self.COMMASPACE.join(self.to_address_list))

    @classmethod
    def __create_message(cls, from_addr, to_addr_list, subject, body, encoding=EMAIL_ENCODING):
        """create MIMEText object"""

        msg = MIMEText(body.encode(encoding, 'ignore'), 'plain', encoding)
        msg['Subject'] = Header(subject, charset=encoding, header_name='Subject')
        msg['From'] = from_addr
        msg['To'] = cls.COMMASPACE.join(to_addr_list)
        msg['Date'] = formatdate(localtime=True)
        return msg
