from optparse import OptionParser
from default import VERSION, USAGE, DEFAULT_CONF_PATH


def get_parser():
    """
    Get command line arguments parser
    """
    parser = OptionParser(version=VERSION, usage=USAGE)

    parser.add_option(
        '--config', dest='config_path', default=DEFAULT_CONF_PATH, type='string',
        help='path to the config file'
    )
    parser.add_option(
        '--check', action='store_true', dest='print_only', default=False,
        help='print alerts instead of sending notifications'
    )

    return parser
