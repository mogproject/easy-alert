import traceback
from logger import Logger


class PrintLogger(Logger):
    def __init__(self):
        super(PrintLogger, self).__init__('PrintLogger')

    def _log(self, priority, message):
        print(message)

    def traceback(self):
        print('')
        print(traceback.format_exc())
