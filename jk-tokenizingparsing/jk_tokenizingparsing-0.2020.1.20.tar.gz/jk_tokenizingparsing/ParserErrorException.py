#!/usr/bin/env python3



from .SourceCodeLocation import *




class ParserErrorException(Exception):

	def __init__(self, location, message, stateName:str = None, textClip:str = None):
		assert isinstance(location, SourceCodeLocation)
		if textClip is not None:
			assert isinstance(textClip, str)

		super().__init__(str(location) + " :: " + message)

		self.__location = location
		self.__message = message
		self.__stateName = stateName
		self.__textClip = textClip
	#

	@property
	def stateName(self):
		return self.__stateName			#### !!!SYNC!!! ####
	#

	@property
	def textClip(self):
		return self.__textClip
	#

	@property
	def location(self):
		return self.__location
	#

	@property
	def message(self):
		return self.__message
	#

	@property
	def extraText(self):
		return self.__textClip
	#

	def print(self):
		s = self.__class__.__name__ + " @ " + str(self.__location) + " :: " + self.__message
		if self.__textClip or self.__stateName:
			s += " ("
			if self.__stateName:
				s += self.__stateName
				if self.__textClip:
					s += ", "
			if self.__textClip:
				s += self.__textClip
			s += ")"
		print(s)
	#

#







