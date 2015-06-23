import arg_parser
import yaml
from easy_alert.util import CaseClass, SystemLogger
from easy_alert.watcher import ProcessWatcher, LogWatcher
from easy_alert.notifier import EmailNotifier


class Setting(CaseClass):
    """
    Manages all settings
    """
    parser = arg_parser.get_parser()

    def __init__(self, watcher_type=None, config_path=None, print_only=None, watchers=list(), notifiers=list(),
                 logger=SystemLogger()):
        super(Setting, self).__init__(['watcher_type', 'config_path', 'print_only', 'watchers', 'notifiers'])
        self.watcher_type = watcher_type
        self.config_path = config_path
        self.print_only = print_only
        self.watchers = watchers
        self.notifiers = notifiers
        self.logger = logger

    def parse_args(self, argv):
        """Parse command line arguments and update operation and options"""

        options, args = Setting.parser.parse_args(argv[1:])

        # args should have only one element
        assert len(args) == 1

        return Setting(args[0], options.config_path, options.print_only, self.watchers, self.notifiers,
                       SystemLogger(options.print_only))

    def load_config(self):
        """Load configuration file"""

        assert (self.watcher_type is not None)
        assert (self.config_path is not None)
        assert (self.print_only is not None)

        config = yaml.load(open(self.config_path).read().decode('utf-8'))
        watchers = [self._parse_watcher_config(self.watcher_type, config['watchers'][self.watcher_type])]
        notifiers = [self._parse_notifier_config(k, v) for k, v in config['notifiers'].items()]

        return Setting(self.watcher_type, self.config_path, self.print_only, watchers, notifiers, self.logger)

    def _parse_watcher_config(self, k, v):
        if k == 'process':
            return ProcessWatcher(v)
        elif k == 'log':
            return LogWatcher(v, self.print_only, self.logger)
        else:
            raise Exception('Not supported.')

    def _parse_notifier_config(self, k, v):
        if k == 'email':
            return EmailNotifier(
                v['group_id'],
                v['from_address'],
                v['to_address_list'],
                v['smtp_server'],
                v['smtp_port'],
                self.print_only,
                self.logger
            )
        else:
            raise Exception('Not supported.')
