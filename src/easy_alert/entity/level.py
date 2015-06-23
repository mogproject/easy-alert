from logging import DEBUG, INFO, WARN, ERROR, CRITICAL
from easy_alert.util import CaseClass
from easy_alert.i18n import *


class Level(CaseClass):
    def __init__(self, level):
        super(Level, self).__init__(['level'])
        self.level = level

    def get_text(self):
        mapping = {CRITICAL: MSG_CRITICAL, ERROR: MSG_ERROR, WARN: MSG_WARN, INFO: MSG_INFO, DEBUG: MSG_DEBUG}
        return mapping.get(self.level)

    def get_keyword(self):
        mapping = {CRITICAL: 'critical', ERROR: 'error', WARN: 'warn', INFO: 'info', DEBUG: 'debug'}
        return mapping[self.level]

    seq = None


Level.seq = [Level(l) for l in [CRITICAL, ERROR, WARN, INFO, DEBUG]]
