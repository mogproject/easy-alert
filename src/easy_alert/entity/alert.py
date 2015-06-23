from easy_alert.util import CaseClass


class Alert(CaseClass):
    """
    Abstract model which can be the output of watchers and the input of notifiers
    """
    keys = ['start_time', 'level', 'title', 'message']

    def __init__(self, start_time, level, title, message):
        super(Alert, self).__init__(self.keys)
        self.start_time = start_time
        self.level = level
        self.title = title
        self.message = message
