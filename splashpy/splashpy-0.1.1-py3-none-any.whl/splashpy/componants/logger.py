# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2019 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from collections import Iterable


class Logger:
    """Splash Logger: Collect & Return Remote Logs"""

    def __init__(self, debug=False):
        """Init Splash Logger"""
        self.debug = debug
        self.prefix = "Splash Py Client"
        self.msg = []
        self.war = []
        self.err = []
        self.deb = []

    def set_debug( self, debug ):
        self.debug = debug

    def set_prefix( self, prefix ):
        self.prefix = prefix

    def info( self, text ):
        self.__add("msg", text)
        return True

    def warn( self, text ):
        self.__add("war", text)

    def error( self, text ):
        self.__add("err", text)
        return False

    def vvv( self, text ):
        if self.debug is True:
            self.__add("deb", text)
        return True

    def clear(self):
        self.msg = []
        self.war = []
        self.err = []
        self.deb = []

    def __add( self, msg_type, text ):
        message = "[" + self.prefix + "] " + text.__str__()
        getattr(self, msg_type).append(message)

    def to_logging( self ):
        """Push All Messages to Logging"""
        import logging

        # Force Logger Level to Show All Messages
        level = logging.getLogger().level
        logging.getLogger().setLevel(logging.DEBUG)

        # Push All Messages to Logger
        for msg in self.msg:
            logging.info(msg)
        # Push All Warnings to Logger
        for war in self.war:
            logging.warning(war)
        # Push All Errors to Logger
        for err in self.err:
            logging.error(err)
        # Push All Debug to Logger
        for deb in self.deb:
            logging.debug(deb)

        # Restore Logger Level
        logging.getLogger().setLevel(level)

    def export( self ):
        """Export All Messages for Messages Packing"""
        # Init Response
        logs = { "msg": {}, "war": {}, "err": {}, "deb": {} }
        # Add All Messages
        for index, text in enumerate(self.msg):
            logs['msg']['msg-'+index.__str__()] = text
        # Add All Warnings
        for index, text in enumerate(self.war):
            logs['war']['war-'+index.__str__()] = text
        # Add All Errors
        for index, text in enumerate(self.err):
            logs['err']['err-'+index.__str__()] = text
        # Add All Debug
        for index, text in enumerate(self.deb):
            logs['deb']['deb-'+index.__str__()] = text

        return logs

    def append(self, raw_logs):
        """Import All Messages from Splash Message"""

        # Import All Messages
        if 'msg' in raw_logs and isinstance(raw_logs['msg'], Iterable):
            for message in raw_logs['msg']:
                getattr(self, "msg").append(raw_logs['msg'][message])
        # Import All Warnings
        if 'war' in raw_logs and isinstance(raw_logs['war'], Iterable):
            for message in raw_logs['war']:
                getattr(self, "war").append(raw_logs['war'][message])
        # Import All Errors
        if 'err' in raw_logs and isinstance(raw_logs['err'], Iterable):
            for message in raw_logs['err']:
                getattr(self, "err").append(raw_logs['err'][message])
        # Import All Debug
        if 'deb' in raw_logs and isinstance(raw_logs['deb'], Iterable):
            for message in raw_logs['deb']:
                getattr(self, "deb").append(raw_logs['deb'][message])

    def on_fault(self, soap_fault):
        """Import Error Message from Soap Fault"""
        getattr(self, "err").append(soap_fault.faultstring)


if __name__ == "__main__":
    # import logging

    logger = Logger()
    logger.info("Test Info Message")
    logger.error("Test Error Message")
    logger.warn("Test Warning Message")
    logger.vvv("Test Debug Message")

    # print logger.msg

    logger.to_logging()

    print (logger.export())
