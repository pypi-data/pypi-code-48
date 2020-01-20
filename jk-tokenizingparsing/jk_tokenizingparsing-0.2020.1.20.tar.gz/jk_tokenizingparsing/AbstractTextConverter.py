




class AbstractTextConverter(object):

	def __init__(self, converterID:str):
		self.__converterID = converterID
	#

	@property
	def converterID(self):
		return self.__converterID
	#

	def convertText(self, text:str):
		raise NotImplementedError()
	#

#



