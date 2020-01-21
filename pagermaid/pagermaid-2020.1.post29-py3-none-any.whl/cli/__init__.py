""" Command-line interface of PagerMaid. """

import pagermaid
from sys import argv
from re import sub


def main():
    argv[0] = sub(r'(-script\.pyw|\.exe)?$', '', argv[0])
    exit(pagermaid.pm_main())
