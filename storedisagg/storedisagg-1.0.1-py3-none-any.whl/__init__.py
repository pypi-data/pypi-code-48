"""
Copyright (C) 2018 contributors listed in AUTHORS.

storedisagg/__init__.py
~~~~~

storedisagg library for the analysis of storage charging/discharging time scales.
"""


import logging

def _get_logger(name):
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        f_handler = logging.StreamHandler()
        f_handler.setLevel(0)
        format_str = '> %(asctime)s - %(levelname)s - %(name)s - %(message)s'
        f_format = logging.Formatter(format_str, "%H:%M:%S")
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)

    return logger

logger = _get_logger(__name__)


from storedisagg.compcalc import ComponentCalculator
from storedisagg.storagedisaggregator import StDisaggregator

from storedisagg.example.example_data import get_example_data_100

