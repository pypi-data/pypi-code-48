


import jk_tokenizingparsing



class TagComment(object):

	def __init__(self, location:jk_tokenizingparsing.SourceCodeLocation, text:str):
		self.locationFrom = location.clone()
		self.locationTo = None
		self.text = text
	#

	def __str__(self):
		return "TagComment<" + " @ " + str(self.locationFrom) + ">"
	#

	def __repr__(self):
		return self.__str__()
	#

#






