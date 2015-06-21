from optparse import OptionParser


VERSION = 'easy-alert %s' % __import__('easy_alert').__version__
DEFAULT_CONF_PATH = '/etc/easy-alert/easy-alert.yml'


def get_parser():
    """
    Get command line arguments parser
    """
    parser = OptionParser(version=VERSION)

    parser.add_option(
        '--config', dest='config_path', default=DEFAULT_CONF_PATH, type='string',
        help='path to the config file'
    )
    parser.add_option(
        '--check', action='store_true', dest='print_only', default=False,
        help='print process information instead of sending notifications'
    )

    return parser
