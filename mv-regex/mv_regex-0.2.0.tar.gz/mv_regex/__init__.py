r"""mv_regex
    Rename files using regular expressions. The program will prompt the user for
    confirmation before renaming (unless the "--force" options is used).

Usage:
    mv_regex [options] <search> <replace> <files>...

Arguments:
    <search>        Regular expression to search.
    <replace>       Regular expression to use as replace.
    <files>         List of files on which to do the replacement.

Options:
    -f, --force     Force move, don't prompt for user interaction.
    -n, --dry-run   Perform a trial run with no changes made.
    -h, --help      Show help.
        --version   Show version.

Example:
    mv_regex "(.*)(_raw.svg)" "\1.svg" *.svg

(c - MIT) T.W.J. de Geus | tom@geus.me | www.geus.me | github.com/tdegeus/mv_regex
"""

__version__ = '0.2.0'

import sys
import os
import re
import docopt
import click

# --------------------------------------------------------------------------------------------------

def main():

    args = docopt.docopt(__doc__, version=__version__)

    # check that all input files exist
    for file in args['<files>']:
        if not os.path.isfile(file) and not os.path.isdir(file):
            print('Input {0:s} does not exist'.format(file))
            sys.exit(1)

    # only keep input files that match the input regular-expression (gains speed)
    args['<files>'] = [file
        for file in args['<files>'] if re.match(args['<search>'], file)]

    # rename files according to input
    args['renamed'] = [re.sub(args['<search>'], args['<replace>'], file)
        for file in args['<files>']]

    # only keep files that will be renamed
    idx = [i for i, (old, new) in enumerate(zip(args['<files>'], args['renamed'])) if old != new]
    args['<files>'] = [args['<files>'][i] for i in idx]
    args['renamed'] = [args['renamed'][i] for i in idx]

    # no files remaining -> quit
    if len(args['renamed']) == 0:
        sys.exit(0)

    # catch non-recursive limitation
    for file in args['<files>']:
        if os.path.isdir(file):
            print('TODO: Current implementation non-recursive, please file a bug-report on GitHub')
            sys.exit(1)

    # avoid file overwrite
    for file in args['renamed']:
        if os.path.isdir(file):
            print('Output "{0:s}" already exists, aborting"'.format(file))
            sys.exit(1)

    # prompt the user for confirmation
    if not args['--force']:

        w = max([len(file) for file in args['<files>']])
        fmt = 'mv {file:' + str(w) + 's} {new:s}'
        for file, new in zip(args['<files>'], args['renamed']):
            print(fmt.format(file=file, new=new))

        if args['--dry-run']:
            sys.exit(0)

        if not click.confirm('Proceed?'):
            sys.exit(1)

    # rename files
    for file, new in zip(args['<files>'], args['renamed']):
        os.rename(file, new)

