


import jk_tokenizingparsing



class TagXMLHeader(object):

	def __init__(self, location:jk_tokenizingparsing.SourceCodeLocation):
		self.locationFrom = location.clone()
		self.locationTo = None
		self.items = []
	#

	def __str__(self):
		return "TagXMLHeader< @ " + str(self.locationFrom) + ">"
	#

	def __repr__(self):
		return self.__str__()
	#

#






