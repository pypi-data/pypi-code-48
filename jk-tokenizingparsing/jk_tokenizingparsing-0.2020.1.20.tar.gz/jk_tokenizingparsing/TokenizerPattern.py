

import re
import collections






from .Token import *
from .ParserErrorException import *
from .TokenizerAction import *
from ._TokenizerPatternTuple import _TokenizerPatternTuple






class EnumPattern(object):

	EXACTCHAR = 1
	ANYCHAR = 2
	EXACTSTRING = 3
	REGEX = 4

#




#
# A tokenization pattern. Use the methods provided in `TokenizerPattern` to provide patterns.
#
class TokenizerPattern(object):

	_PREFIXES_POSTFIXES = [
		"$", "^"
	]

	#
	# Is the character encountered equal to the specified character?
	#
	@staticmethod
	def exactChar(data):
		assert isinstance(data, str)
		assert len(data) == 1
		return _TokenizerPatternTuple(EnumPattern.EXACTCHAR, "EXACTCHAR", data, 1)
	#

	#
	# Are the characters encountered exactly the specified sequence?
	#
	@staticmethod
	def exactSequence(data):
		assert isinstance(data, str)
		assert len(data) > 0
		return _TokenizerPatternTuple(EnumPattern.EXACTSTRING, "EXACTSTRING", data, len(data))
	#

	#
	# Is the character encountered any of the specified characters?
	#
	@staticmethod
	def anyOfTheseChars(data):
		assert isinstance(data, str)
		assert len(data) > 0
		return _TokenizerPatternTuple(EnumPattern.ANYCHAR, "ANYCHAR", data, -1)
	#

	#
	# Do the characters encountered match the specified regular expression?
	#
	@staticmethod
	def regEx(regExPattern):
		if (len(regExPattern) == 0) \
			or regExPattern.startswith("$") \
			or regExPattern.startswith("^") \
			or regExPattern.endswith("$") \
			or regExPattern.endswith("^"):
			raise Exception("Unsuitable regular expression!")
		return _TokenizerPatternTuple(EnumPattern.REGEX, "REGEX", re.compile(regExPattern), -1)
	#

#




