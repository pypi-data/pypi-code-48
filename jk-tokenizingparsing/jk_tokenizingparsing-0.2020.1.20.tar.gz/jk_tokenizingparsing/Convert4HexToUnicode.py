

import binascii



from .AbstractTextConverter import AbstractTextConverter



class Convert4HexToUnicode(AbstractTextConverter):

	def __init__(self):
		super().__init__("convert4HexToUnicode")
	#

	def __removeTrailingZeros(self, byteData):
		if len(byteData) == 0:
			return byteData
		if byteData[0] != 0:
			return byteData
		for i in range(0, len(byteData)):
			if byteData[i] != 0:
				return byteData[i:]
		return bytearray()
	#

	def convertText(self, text:str):
		try:
			binData = self.__removeTrailingZeros(binascii.unhexlify(text))
			return data.decode("utf-8")
		except:
			raise Exception("Not valid unicode: " + repr(text))
	#

#




