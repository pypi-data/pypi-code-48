#!/usr/bin/env python3




class TextBuffer(object):

	def __init__(self, beginLineNo = 0, beginCharNo = 0):
		self.__data = ""
		self.beginLineNo = beginLineNo
		self.beginCharNo = beginCharNo
	#

	def clear(self, beginLineNo, beginCharNo):
		self.__data = ""
		self.beginLineNo = beginLineNo
		self.beginCharNo = beginCharNo
	#

	def reset(self):
		self.__data = ""
	#

	def append(self, s):
		assert isinstance(s, str)
		self.__data += s
	#

	def __len__(self):
		return len(self.__data)
	#

	def __str__(self):
		return self.__data
	#

	def __repr__(self):
		return "TextBuffer(" + repr(self.__data) + ")"
	#

#






