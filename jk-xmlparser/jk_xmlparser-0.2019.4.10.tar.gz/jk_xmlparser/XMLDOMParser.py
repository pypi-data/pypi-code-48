

import re
import xml
import xml.sax

#from jk_testing import Assert
from jk_simplexml import *
from jk_tokenizingparsing import Token

from .XMLDOMParseException import XMLDOMParseException
from .TagBegin import TagBegin
from .TagComment import TagComment
from .TagEnd import TagEnd
from .TagSpecial import TagSpecial
from .XMLTokenizerImpl import XMLTokenizerImpl





class SAXConverter(xml.sax.handler.ContentHandler):

	def __init__(self, sourceID):
		super().__init__()
		self.__sourceID = sourceID
		self.__rootElement = None
		self.__stack = []
	#

	def getRootElement(self) -> HElement:
		return self.__rootElement
	#
		
	def startDocument(self):
		# self._out.write("<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n")
		pass
	#

	def startElement(self, name, attrs):
		# for parsing with line and column numbers: https://stackoverflow.com/questions/15477363/xml-sax-parser-and-line-numbers-etc

		x = HElement(name, [ HAttribute(k, v) for k, v in attrs.items() ])
		if self.__stack:
			self.__stack[-1].children.append(x)
		self.__stack.append(x)

		if self.__rootElement is None:
			self.__rootElement = x
	#

	def endElement(self, name):
		del self.__stack[-1]
	#

	def characters(self, content):
		xElement = self.__stack[-1]
		if xElement.children:
			xLast = xElement.children[-1]
			if isinstance(xLast, HText):
				xLast.text += content
			else:
				xElement.children.append(HText(content))
		else:
			xElement.children.append(HText(content))
	#

	def ignorableWhitespace(self, content):
		xElement = self.__stack[-1]
		if xElement.children:
			xLast = xElement.children[-1]
			if isinstance(xLast, HText):
				xLast.text += content
			else:
				xElement.children.append(HText(content))
		else:
			xElement.children.append(HText(content))
	#
		
	def processingInstruction(self, target, data):
		#self._out.write("<?%s %s?>" % (target, data))
		pass
	#

#



class XMLDOMParser(object):

	def __init__(self):
		pass
	#

	def parseFile(self, filePath:str, logFunction = None) -> HElement:
		with open(filePath, "r") as f:
			textData = f.read()
		return self.parseText(textData, filePath, logFunction = logFunction)
	#

	def parseText(self, textData:str, sourceID = None, logFunction = None) -> HElement:
		saxConverter = SAXConverter(sourceID)
		xml.sax.parseString(textData, saxConverter)
		return saxConverter.getRootElement()
	#

#







