from abc import ABCMeta, abstractmethod
from easy_alert.util import CaseClass, get_server_id
from easy_alert.i18n import *


class Notifier(CaseClass):
    __metaclass__ = ABCMeta

    def __init__(self, group_id=None, **args):
        super(Notifier, self).__init__(['group_id'] + args.keys())
        self.group_id = group_id
        for k in args:
            setattr(self, k, args[k])

    def get_subject(self, alert):
        return MSG_SUBJECT_FORMAT % {
            'level': alert.level.get_text(),
            'group_id': self.group_id,
            'server_id': get_server_id(),
            'title': alert.title,
            'start_time': alert.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    @abstractmethod
    def notify(self, alert):
        """abstract method"""
