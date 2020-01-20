


import jk_tokenizingparsing



class TagEnd(object):

	def __init__(self, location:jk_tokenizingparsing.SourceCodeLocation, name:str):
		self.locationFrom = location.clone()
		self.locationTo = None
		self.name = name
	#

	def __str__(self):
		return "TagEnd<" + self.name + " @ " + str(self.locationFrom) + ">"
	#

	def __repr__(self):
		return self.__str__()
	#

#






