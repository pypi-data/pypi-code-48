import logging
import os

from time import strftime


class KleenLogger:
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    def __init__(self):
        self.logger = None
        if not os.path.exists('log/'):
            os.mkdir('log/')

    def init_logger(self, app_name, level, fmt, date_fmt, encoding):
        filename = "log/{}-{}.log".format(app_name, strftime("%Y_%m_%d_%H_%M_%S"))
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        handler = logging.FileHandler(filename, 'w', encoding)
        formatter = logging.Formatter(
            fmt=fmt,
            datefmt=date_fmt
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


kleenlogger = KleenLogger()
