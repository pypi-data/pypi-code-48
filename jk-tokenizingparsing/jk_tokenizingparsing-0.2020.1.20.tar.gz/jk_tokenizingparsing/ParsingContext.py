#!/usr/bin/env python3


from .TokenStream import *
from .ParserErrorException import *





class ParsingContext(object):

	def __init__(self, debugMessageWriter = None):
		if debugMessageWriter != None:
			assert callable(debugMessageWriter)

		self.__bDebugging = debugMessageWriter != None
		self.__debugMessageWriter = debugMessageWriter
		self.indent = 0
		self.__prefix = "                "
	#

	@property
	def debugMessageWriter(self):
		return self.__debugMessageWriter
	#

	@property
	def bDebugging(self):
		return self.__bDebugging
	#

	def _debugBegin(self, functionName, token):
		if self.indent * 2 > len(self.__prefix):
			self.__prefix += "  "
		self.__debugMessageWriter(self.__prefix[:self.indent*2] + functionName + " ... " + str(token))
	#

	def _debugEnd(self, functionName, bSuccess):
		if self.indent * 2 > len(self.__prefix):
			self.__prefix += "  "
		s = "success." if bSuccess else "failed."
		self.__debugMessageWriter(self.__prefix[:self.indent*2] + functionName + " " + s)
	#

#






