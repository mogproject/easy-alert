import arg_parser
import sys
import yaml
from easy_alert.logger import SystemLogger, PrintLogger
from easy_alert.util import CaseClass
from default import WATCHER_KEYS, WATCHER_FACTORIES, NOTIFIER_FACTORIES
from setting_error import SettingError


class Setting(CaseClass):
    """
    Manages all settings
    """

    # argument parser
    parser = arg_parser.get_parser()

    def __init__(self, watcher_types=list(), config_path=None, print_only=None, watchers=list(), notifiers=list(),
                 logger=SystemLogger()):
        super(Setting, self).__init__([
            'watcher_types', 'config_path', 'print_only', 'watchers', 'notifiers', 'logger',
        ])
        self.watcher_types = watcher_types
        self.config_path = config_path
        self.print_only = print_only
        self.watchers = watchers
        self.notifiers = notifiers
        self.logger = logger

    def parse_args(self, argv):
        """Parse command line arguments and update operation and options"""

        options, args = Setting.parser.parse_args(argv[1:])

        # args should be at least one and all watcher should be known
        if not args or set(args) - set(WATCHER_KEYS):
            self.parser.print_usage(sys.stderr)
            self.parser.exit(2)

        return Setting(sorted(set(args), key=args.index), options.config_path, options.print_only, self.watchers,
                       self.notifiers, PrintLogger() if options.print_only else self.logger)

    def load_config(self):
        """Load configuration file"""

        # assertions
        assert self.watcher_types, 'watcher_types should be set before load_config'
        assert (self.config_path is not None), 'config_path should be set before load_config'
        assert (self.print_only is not None), 'print_only should be set before load_config'

        config = yaml.load(open(self.config_path).read().decode('utf-8'))
        if not isinstance(config, dict):
            raise SettingError('Syntax error: %s' % self.config_path)

        # parse watchers
        ws = config.get('watchers')
        if ws:
            if not isinstance(ws, dict):
                raise SettingError('Syntax error: %s' % self.config_path)
            watchers = [self._parse_watcher(t, ws) for t in self.watcher_types]
        else:
            raise SettingError('Not found "watchers" entry: %s' % self.config_path)

        # parse notifiers
        ns = config.get('notifiers')
        if ns:
            if not isinstance(ns, dict):
                raise SettingError('Syntax error: %s' % self.config_path)
            assert ns  # it should not be empty
            notifiers = [self._parse_notifier(k, v) for k, v in ns.items()]
        else:
            raise SettingError('Not found "notifiers" entry: %s' % self.config_path)

        return Setting(self.watcher_types, self.config_path, self.print_only, watchers, notifiers, self.logger)

    def _parse_watcher(self, watcher_type, watcher_config):
        factory = WATCHER_FACTORIES.get(watcher_type)
        if not factory:
            raise SettingError('Unsupported watcher type: %s' % watcher_type)

        conf = watcher_config.get(watcher_type)
        if not conf:
            raise SettingError('Not found watcher configuration for "%s": %s' % (watcher_type, self.config_path))

        return factory(conf, self.print_only, self.logger)

    def _parse_notifier(self, notifier_type, notifier_config):
        factory = NOTIFIER_FACTORIES.get(notifier_type)
        if not factory:
            raise SettingError('Unsupported notifier type: %s in %s' % (notifier_type, self.config_path))

        return factory(notifier_config, self.print_only, self.logger)
