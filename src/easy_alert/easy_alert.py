import sys
from setting.setting import Setting


def main():
    """
    Main function
    """
    setting = Setting().parse_args(sys.argv)
    setting.logger.info('Script started: args=%s' % sys.argv[1:])

    try:
        setting = setting.load_config()
        for watcher in setting.watchers:
            for alert in watcher.watch():
                for notifier in setting.notifiers:
                    notifier.notify(alert)
            watcher.after_success()
    except Exception as e:
        setting.logger.error('Script ended with error: %s: %s' % (e.__class__.__name__, e))
        setting.logger.traceback()
        return 1

    setting.logger.info('Script ended successfully.')
    return 0
