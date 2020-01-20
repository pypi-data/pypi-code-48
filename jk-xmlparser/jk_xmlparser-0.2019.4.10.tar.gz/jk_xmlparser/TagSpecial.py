


import jk_tokenizingparsing



class TagSpecial(object):

	def __init__(self, location:jk_tokenizingparsing.SourceCodeLocation, name:str):
		self.locationFrom = location.clone()
		self.locationTo = None
		self.name = name
		self.items = []
	#

	def __str__(self):
		return "TagSpecial<" + self.name + " @ " + str(self.locationFrom) + ">"
	#

	def __repr__(self):
		return self.__str__()
	#

#






