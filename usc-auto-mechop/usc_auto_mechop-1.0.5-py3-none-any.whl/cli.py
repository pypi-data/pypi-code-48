import argparse
import sys
import logging
from datetime import datetime
from configparser import ConfigParser
import os
from auto_mechop.runner import Runner

def main():
    log_path = '../logs'
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_name = datetime.now().strftime('/%d_%m_%Y-%H_%M_%S')
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG,
                        handlers=[
                            logging.FileHandler("{0}/{1}.log".format(log_path, log_name)),
                        ])
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(console)

    logger.debug("Running CLI")

    logger.debug("Parsing config file")
    config = ConfigParser()
    config.read("settings.ini")

    parser = argument_parser()

    # print usage by default if no args given
    if len(sys.argv[1:]) == 0:
        logging.debug("No user arguments supplied")
        parser.print_usage()
        parser.exit()

    logging.debug("User argumments were: {args}".format(args=sys.argv[1:]))
    args = parser.parse_args()
    if args.user:
        print(config.get('user', 'login'))
    if hasattr(args, 'func'):
        args.func(args, config)


def argument_parser():
    parser = argparse.ArgumentParser(
        description='Grading distribution program for '
        'USC\'s AME 341 mechoptronics course.',
        prog='auto_mechop')
    parser.add_argument('--version',
        action='version',
        version='%(prog)s 0.1.0')
    parser.add_argument('--user',
        action='store_true')
    subparsers = parser.add_subparsers(title='subcommands')

    # SETUP parsers
    parser_setup = subparsers.add_parser('setup',help='setup help')
    parser_setup.set_defaults(func=setup)

    # SUBMIT parsers
    parser_submit = subparsers.add_parser('submit',
        help='submit help')
    parser_submit.set_defaults(func=submit)
    parser_submit.add_argument("-d", "--download",
        help="download .zip files from Blackboard site",
        action="store_true")
    parser_submit.add_argument('assignment_name',
        help='name of assignment')
    parser_submit.add_argument('section_name',
        help='name of section', type=str.lower)


    # RELEASE parsers
    parser_release = subparsers.add_parser('release',
        help='release help')
    parser_release.set_defaults(func=release)
    parser_release.add_argument('assignment_name',
        help='name of assignment')
    parser_release.add_argument('section_name',
        help='name of section', type=str.lower)


    # REPORT parsers
    parser_report = subparsers.add_parser('report',
        help='report help')
    parser_report.set_defaults(func=report)
    parser_report.add_argument('assignment_name',
        help='name of assignment')


    # CLEAR parsers
    parser_clear = subparsers.add_parser('clear',
        help='clear help')
    parser_clear.set_defaults(func=clear)
    parser_clear.add_argument('assignment_name',
        help='name of assignment')

    return parser


def setup(args, config):
    runner = Runner()
    runner.run_setup_flow()


def submit(args, config):
    runner = Runner()
    runner.run_submit_flow(args)


def release(args, config):
    runner = Runner()
    runner.run_release_flow(args)


def report(args, config):
    runner = Runner()
    runner.run_report_flow(args)

def clear(args, config):
    runner = Runner()
    runner.run_clear_flow(args)


if __name__ == "__main__":
    main()
