from abc import ABCMeta, abstractmethod
from easy_alert.util import CaseClass


class Watcher(CaseClass):
    __metaclass__ = ABCMeta

    def __init__(self, **args):
        super(Watcher, self).__init__(args.keys())
        for k in args:
            setattr(self, k, args[k])

    @abstractmethod
    def watch(self):
        """abstract method"""

    def after_success(self):
        """do nothing in default"""
