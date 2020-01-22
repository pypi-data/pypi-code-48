import sys

if sys.version_info.minor == 8:
    import openbci.preprocess38 as preprocess
elif sys.version_info.minor == 7:
    import openbci.preprocess37 as preprocess

from .handlers import eegframe

