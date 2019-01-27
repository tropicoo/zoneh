import logging
import sys
from pprint import pprint

from zoneh.zoneh import ZoneH

TABULATE_HEADERS = ["Time", "Notifier", "H", "M", "R", "L", "Special",
                    "Domain", "OS", "View"]

if __name__ == '__main__':
    # TODO: different logging handlers.
    log_level = logging.DEBUG
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=log_format, level=log_level, stream=sys.stdout)

    # TODO: argparse logic
    # parser = argparse.ArgumentParser(description='Host stats')
    #
    # parser.add_argument('-a', '--archive', default='archive',
    #                     action='store',
    #                     choices=('archive', 'special', 'onhold'), dest='archive',
    #                     help='get archive data, (default: %(default)s)')
    # parser.add_argument('--start-page',
    #                     default=1,
    #                     const=1,
    #                     nargs='?', action='store', dest='start_page',
    #                     type=int,
    #                     help='start page')
    #
    # parser.add_argument('--end-page',
    #                     default=None,
    #                     nargs='?', action='store', dest='end_page',
    #                     type=int,
    #                     help='end page')
    #
    # args = parser.parse_args()
    zoneh = ZoneH()
    data = zoneh.get_archive()

    # TODO: Consider using tabulate module
    pprint(data)
