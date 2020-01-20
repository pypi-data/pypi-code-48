#!/usr/bin/env python3


from .Token import Token
from .SourceCodeLocation import SourceCodeLocation
from .TokenizerBase import *

from .AbstractTextConverter import AbstractTextConverter
from .Convert4HexToUnicode import Convert4HexToUnicode
from .TextConverterManager import TextConverterManager
from .CompiledTokenizer import CompiledTokenizer

from .ParserErrorException import ParserErrorException
from .ParserBase import *

from .Serializer import Serializer





from .JSONLoader import JSONLoader as _JSONLoader

fromJSON = _JSONLoader.fromJSON



__version__ = "0.2020.1.20"



