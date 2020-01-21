#!/usr/bin/env python3

# Libraries
import argparse
from blessings import Terminal
import os
import sys

# Constants
NAME = 'gitlabci-runner-local'

# Terminal
force_styling = False
if os.environ.get('FORCE_STYLING') is not None:
    force_styling = True
term = Terminal(force_styling=force_styling)

# Components
from .dumper import dumper
from .menu import selector
from .parser import reader
from .runner import launcher

# Main
def main():

    # Variables
    interactive = (sys.stdin.isatty() and sys.stdout.isatty())
    result = False

    # Arguments creation
    parser = argparse.ArgumentParser(
        prog=NAME, description='%s: Launch .gitlab-ci.yml jobs locally' % (NAME),
        add_help=False, formatter_class=argparse.RawTextHelpFormatter)

    # Arguments optional definitions
    parser.add_argument('-h', dest='help', action='store_true',
                        help='Show this help message')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='Hide jobs execution context')
    parser.add_argument('-c', dest='configuration', default='.gitlab-ci.yml',
                        help='Path to the .gitlab-ci.yml configuration')
    parser.add_argument('-b', '--before', dest='before', action='store_true',
                        help='Enable before_script executions')
    parser.add_argument('-a', '--after', dest='after', action='store_true',
                        help='Enable after_script executions')
    parser.add_argument('-m', '--manual', dest='manual', action='store_true',
                        help='Allow manual jobs to be used')
    parser.add_argument(
        '-t', dest='manual_tags', default='deploy,local,publish',
        help='Handle listed tags as manual jobs\nDefault list: %(default)s')
    parser.add_argument('-p', '--pipeline', dest='pipeline', action='store_true',
                        help='Run complete stages rather than jobs')

    # Arguments exclusive definitions
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dump', dest='dump', action='store_true',
                       help='Dump parsed .gitlab-ci.yml configuration')
    group.add_argument('-s', '--select', dest='select', action='store_true',
                       help='Force jobs selection from enumerated names')
    group.add_argument('-l', '--list', dest='list', action='store_true',
                       help='Select one job to run (implies --manual)')

    # Arguments positional definitions
    parser.add_argument('names', nargs='*',
                        help='Names of specific jobs (or stages with --pipeline)')

    # Arguments parser
    options = parser.parse_args()
    if options.help:
        print(' ')
        parser.print_help()
        print(' ', flush=True)
        sys.exit(0)

    # Prepare manual_tags
    options.manual_tags = options.manual_tags.split(',')

    # Prepare paths
    options.path = os.path.dirname(os.path.abspath(options.configuration))

    # Read configuration
    jobs = reader(options)

    # Header
    print(' ', flush=True)

    # Dump configuration
    if options.dump:
        result = dumper(options, jobs)

    # Select job
    elif options.list and interactive:
        options.manual = True
        result = selector(options, jobs)

    # Select jobs
    elif options.select and interactive:
        result = selector(options, jobs)

    # Launch pipeline
    elif options.pipeline:
        result = launcher(options, jobs)

    # Launch jobs
    elif options.names:
        result = launcher(options, jobs)

    # Select jobs
    elif interactive:
        result = selector(options, jobs)

    # Unsupported case
    else:
        print(' %s%s: %sERROR: %sUnsupported non-interactive context...%s' %
              (term.green + term.bold, NAME, term.red + term.bold,
               term.normal + term.bold, term.normal))
        print(' ', flush=True)

    # Result
    if result:
        sys.exit(0)
    else:
        sys.exit(1)

# Entrypoint
if __name__ == '__main__':
    main()
