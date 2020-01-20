#! /usr/bin/env python3

import argparse
from ha_magiwand import HomeAssistantWands

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--loglevel", dest="loglevel", default="WARNING",
        help="Loglevel: CRITICAL, ERROR, WARNING (default), INFO, DEBUG",
    )
    args = parser.parse_args()

    if args.loglevel not in ["CRITICAL", "ERROR", "WARNING" , "INFO", "DEBUG"]:
        args.loglevel="WARNING"

    myclass = HomeAssistantWands(loglevel=args.loglevel)

    try:
        myclass.run()
    except KeyboardInterrupt:
        myclass.wandreader.popen.terminate()
