import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
from notifier import Notifier
from easy_alert.i18n import EMAIL_ENCODING


class EmailNotifier(Notifier):
    def __init__(self,
                 group_id,
                 from_address,
                 to_address_list,
                 smtp_server,
                 smtp_port,
                 print_only,
                 logger):
        super(EmailNotifier, self).__init__(
            group_id, from_address=from_address, to_address_list=to_address_list, smtp_server=smtp_server,
            smtp_port=smtp_port, print_only=print_only, logger=logger)

    def notify(self, alert):
        subject = self.get_subject(alert)
        body = alert.message

        if self.print_only:
            self.logger.info('Would send a message:')
            self.logger.info('Subject: %s' % subject)
            self.logger.info('From: %s' % self.from_address)
            self.logger.info('To: %s' % self.to_address_list)
            self.logger.info('Body:')
            for line in body.split('\n'):
                self.logger.info(line)
        else:
            msg = self.__create_message(self.from_address, self.to_address_list, subject, body)
            s = smtplib.SMTP(self.smtp_server, self.smtp_port)
            try:
                s.sendmail(self.from_address, self.to_address_list, msg.as_string())
            finally:
                s.close()
            self.logger.info('Sent mail to %s.' % self.to_address_list)

    @staticmethod
    def __create_message(from_addr, to_addr_list, subject, body, encoding=EMAIL_ENCODING):
        """create MIMEText object"""

        msg = MIMEText(body.encode(encoding, 'ignore'), 'plain', encoding)
        msg['Subject'] = Header(subject, charset=encoding, header_name='Subject')
        msg['From'] = from_addr
        msg['To'] = to_addr_list
        msg['Date'] = formatdate(localtime=True)
        return msg
