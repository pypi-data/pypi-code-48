


import jk_tokenizingparsing



class TagBegin(object):

	def __init__(self, location:jk_tokenizingparsing.SourceCodeLocation, name:str):
		self.locationFrom = location.clone()
		self.locationTo = None
		self.name = name
		self.attributes = dict()
		self.bWithTermination = False
	#

	def __str__(self):
		if self.bWithTermination:
			return "TagBeginEnd<" + self.name + " @ " + str(self.locationFrom) + ">"
		else:
			return "TagBegin<" + self.name + " @ " + str(self.locationFrom) + ">"
	#

	def __repr__(self):
		return self.__str__()
	#

#






