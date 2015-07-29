from easy_alert.watcher import ProcessWatcher, LogWatcher, SSHWatcher, CommandWatcher, HTTPWatcher
from easy_alert.notifier import EmailNotifier

# dict of the watcher and its factory
WATCHER_FACTORIES = {
    'log': lambda conf, print_only, logger: LogWatcher(conf, print_only),
    'process': lambda conf, print_only, logger: ProcessWatcher(conf),
    'ssh': lambda conf, print_only, logger: SSHWatcher(conf),
    'command': lambda conf, print_only, logger: CommandWatcher(conf),
    'http': lambda conf, print_only, logger: HTTPWatcher(conf),
}

# dict of the notifier and its factory
NOTIFIER_FACTORIES = {
    'email': lambda conf, print_only, logger: EmailNotifier(conf, print_only, logger),
}

WATCHER_KEYS = sorted(WATCHER_FACTORIES.keys())

VERSION = 'easy-alert %s' % __import__('easy_alert').__version__

USAGE = """
%prog [options] <watcher_type> [<watcher_type> ...]

Available watcher types:
  """ + '\n  '.join(WATCHER_KEYS)

DEFAULT_CONF_PATH = '/etc/easy-alert/easy-alert.yml'
