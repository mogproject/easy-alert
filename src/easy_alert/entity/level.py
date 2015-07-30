from logging import DEBUG, INFO, WARN, ERROR, CRITICAL
from easy_alert.util import CaseClass
from easy_alert.i18n import *


class Level(CaseClass):
    def __init__(self, level):
        super(Level, self).__init__(['level'])

        mapping = {'critical': CRITICAL, 'error': ERROR, 'warn': WARN, 'info': INFO, 'debug': DEBUG}
        if isinstance(level, basestring):
            lv = mapping.get(level)
            if lv is None:
                raise KeyError('Unknown level string: %s' % level)
            self.level = lv
        elif isinstance(level, int):
            self.level = level
        else:
            raise KeyError('Invalid level: %s' % level)

    def get_text(self):
        mapping = {CRITICAL: MSG_CRITICAL, ERROR: MSG_ERROR, WARN: MSG_WARN, INFO: MSG_INFO, DEBUG: MSG_DEBUG}
        return mapping.get(self.level)

    def get_keyword(self):
        mapping = {CRITICAL: 'critical', ERROR: 'error', WARN: 'warn', INFO: 'info', DEBUG: 'debug'}
        return mapping[self.level]

    seq = None


Level.seq = [Level(l) for l in [CRITICAL, ERROR, WARN, INFO, DEBUG]]
