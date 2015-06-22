import os
import sys
import syslog
import traceback


class SystemLogger(object):
    def __init__(self, print_only=False):
        self.print_only = print_only

    def info(self, message):
        self._log_syslog(syslog.LOG_INFO, message)

    def error(self, message):
        self._log_syslog(syslog.LOG_ERR, message)

    def traceback(self):
        if self.print_only:
            print('')
            print(traceback.format_exc())

    def _log_syslog(self, priority, message):
        prefix = {syslog.LOG_INFO: '[INFO] ', syslog.LOG_ERR: '[ERROR]'}[priority]
        msg = '%s%s' % (prefix, message)

        if self.print_only:
            print(msg)
        else:
            syslog.openlog(os.path.basename(sys.argv[0]))
            syslog.syslog(priority, msg)
