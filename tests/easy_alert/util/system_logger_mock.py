import syslog

from easy_alert.logger.system_logger import SystemLogger


class SystemLoggerMock(SystemLogger):
    def __init__(self, print_only=False, buffer=list()):
        super(SystemLoggerMock, self).__init__(print_only)
        self.buffer = buffer

    def info(self, message):
        self.buffer.append((syslog.LOG_INFO, message))

    def warn(self, message):
        self.buffer.append((syslog.LOG_WARNING, message))

    def error(self, message):
        self.buffer.append((syslog.LOG_ERR, message))

    def traceback(self):
        """Do nothing"""
