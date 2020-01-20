


from .AbstractTextConverter import AbstractTextConverter
from .SourceCodeLocation import SourceCodeLocation




class TextConverterManager(object):

	def __init__(self):
		self.__converters = dict()
	#

	def register(self, m:AbstractTextConverter):
		self.__converters[m.converterID] = m
	#

	def convertText(self, converterID:str, text:str) -> str:
		return self.__converters[converterID].convertText(text)
	#

	def getConverterE(self, converterID:str, location:SourceCodeLocation = None) -> AbstractTextConverter:
		m = self.getConverter(converterID)
		if m is None:
			if location is None:
				location = SourceCodeLocation.create()
			raise ParserErrorException(location, "No such converter: " + repr(converterID))
		else:
			return m
	#

	def getConverter(self, converterID:str) -> AbstractTextConverter:
		return self.__converters.get(converterID)
	#

#




