#!/usr/bin/env python3



from .Token import *
from .TokenizerBase import *
from .SourceCodeLocation import *

from .TokenStreamMark import TokenStreamMark








class TokenStream(object):

	# ////////////////////////////////////////////////////////////////
	# // Constructors/Destructors
	# ////////////////////////////////////////////////////////////////

	def __init__(self, tokens):
		self.__tokens = list(tokens)
		assert len(self.__tokens) > 0
		self.__pos = 0
		self.__maxpos = len(self.__tokens) - 1
		self.__eosToken = self.__tokens[self.__maxpos]
		assert self.__eosToken.type == "eos"
	#

	# ////////////////////////////////////////////////////////////////
	# // Properties
	# ////////////////////////////////////////////////////////////////

	@property
	def location(self):
		t = self.__tokens[self.__pos]
		return SourceCodeLocation.fromToken(t)

	@property
	def isEOS(self):
		return self.__pos == self.__maxpos
	#

	@property
	def position(self):
		return self.__pos
	#

	@property
	def length(self):
		return len(self.__tokens)
	#

	# ////////////////////////////////////////////////////////////////
	# // Methods
	# ////////////////////////////////////////////////////////////////

	def reset(self):
		self.__pos = 0
	#

	def getTextPreview(self, length:int, bInsertSpacesBetweenTokens:bool = False) -> str:
		nAvailable = self.__maxpos - self.__pos
		if nAvailable < length:
			extra = "..."
		else:
			nAvailable = length
			extra = ""
		mid = " " if bInsertSpacesBetweenTokens else ""
		s = mid.join([ c.text for i, c in zip(range(0, nAvailable), self.__tokens[self.__pos:]) ])
		return s + extra
	#

	"""
	def getTokenPostview(self, length:int):
		nAvailable = self.__maxpos - self.__pos
		if nAvailable < length:
			extra = " ..."
		else:
			nAvailable = length
			extra = ""
		s = "  ".join([ (c.type + ":" + repr(c.text)) for i, c in zip(range(0, nAvailable), self.__tokens[self.__pos:]) ])	#### !!!SYNC!!!! ####
		return s + extra
	#
	"""

	def getTokenPreview(self, length:int) -> str:
		nAvailable = self.__maxpos - self.__pos
		if nAvailable < length:
			extra = " ..."
		else:
			nAvailable = length
			extra = ""
		s = "  ".join([
			(c.type + ":" + repr(c.text) + "@" + str(c.lineNo) + ":" + str(c.charPos))
				for i, c in zip(range(0, nAvailable), self.__tokens[self.__pos:])
			])	#### !!!SYNC!!!! ####
		return s + extra
	#

	def mark(self):
		return TokenStreamMark(self)
	#

	def _setPosition(self, pos):
		self.__pos = pos
	#

	def reset(self):
		self.__pos = 0
	#

	def multiPeek(self, nCount):
		if nCount <= 0:
			raise Exception("Invalid nCount value: " + str(nCount))
		if self.__pos + nCount > self.__maxpos:
			ret = []
			for i in range(0, nCount):
				j = self.__pos + i
				if j < self.__maxpos:
					ret.append(self.__tokens[j])
				else:
					ret.append(self.__eosToken)
			return ret
		else:
			return self.__tokens[self.__pos:self.__pos + nCount]
	#

	def peek(self):
		return self.__tokens[self.__pos]
	#

	def read(self):
		t = self.__tokens[self.__pos]
		if self.__pos < self.__maxpos:
			self.__pos += 1
		return t
	#

	def skip(self, n = 1):
		if n < 0:
			raise Exception("Invalid n: " + str(n))
		if self.__pos + n > self.__maxpos:
			raise Exception("Skipping too far!")
		self.__pos += n
	#

	def skipAll(self, tokenType, tokenText):
		assert isinstance(tokenType, str)

		n = 0
		while True:
			t = self.__tokens[self.__pos]
			if t.type == "eos":
				return n
			if t.type != tokenType:
				return n
			if tokenText != None:
				if t.text != tokenText:
					return n
			n += 1
			self.__pos += 1
	#

	def __iter__(self):
		return iter(self.__tokens[self.__pos:])
	#

#







