import sys
from setting import Setting
from itertools import chain


def main():
    """
    Main function
    """
    setting = Setting().parse_args(sys.argv)
    setting.logger.info('Script started.')

    try:
        setting = setting.load_config()
        for alert in chain.from_iterable(w.watch() for w in setting.watchers):
            for n in setting.notifiers:
                n.notify(alert)
    except Exception as e:
        setting.logger.error('Script ended with error: %s: %s' % (e.__class__.__name__, e))
        setting.logger.traceback()
        return 1

    setting.logger.info('Script ended successfully.')
    return 0
