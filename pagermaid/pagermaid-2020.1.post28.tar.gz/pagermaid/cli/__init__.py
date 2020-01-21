""" Command-line interface of PagerMaid. """

from pagermaid import pm_main
from sys import argv
from re import sub


def main():
    argv[0] = sub(r'(-script\.pyw|\.exe)?$', '', argv[0])
    exit(pm_main())
