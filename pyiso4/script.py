import argparse
import sys
import pathlib

import pyiso4
from pyiso4.ltwa import Abbreviate


def get_arguments_parser():
    parser = argparse.ArgumentParser(description=pyiso4.__doc__)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + pyiso4.__version__)

    parser.add_argument(
        'titles',
        nargs='*',
        type=str,
        default=sys.stdin,
        help='titles')

    here = pathlib.Path(__file__).parent

    parser.add_argument(
        '-l', '--ltwa', help='CSV of the LTWA', default=here / 'LTWA_20170914-modified.csv')

    parser.add_argument(
        '-s', '--stopwords', help='List of stopwords (one per line)', default=here / 'stopwords.txt')

    parser.add_argument('-k', '--keep-parts', help='keeps PART', action='store_true')

    return parser


def main():
    args = get_arguments_parser().parse_args()

    # load LTWA
    abbreviate = Abbreviate.create(args.ltwa, args.stopwords)

    # abbreviate
    for title in args.titles:
        print(abbreviate(title, remove_part=not args.keep_parts))


if __name__ == '__main__':
    main()
