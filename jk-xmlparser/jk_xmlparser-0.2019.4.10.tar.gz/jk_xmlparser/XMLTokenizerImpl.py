


import os
import json

import jk_tokenizingparsing

from .TagBegin import TagBegin
from .TagEnd import TagEnd
from .TagComment import TagComment
from .TagXMLHeader import TagXMLHeader




class XMLTokenizerImpl(object):

	def __init__(self):
		textConverterMgr = jk_tokenizingparsing.TextConverterManager()
		textConverterMgr.register(jk_tokenizingparsing.Convert4HexToUnicode())

		tokSpecFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tokenize_xml.json")
		if not os.path.isfile(tokSpecFilePath):
			raise Exception("No such file: " + tokSpecFilePath)

		with open(tokSpecFilePath, "r") as f:
			self.__tokenizer = jk_tokenizingparsing.fromJSON(textConverterMgr, json.load(f))

		self.__tokMethods = [
			self.__tryEatEndTag,
			self.__tryEatBeginTag,
			self.__tryEatComment,
			self.__tryEatHeaderTag,
		]
	#



	def __tryEatHeaderTag(self, ts:jk_tokenizingparsing.TokenStream, bBeTolerant:bool, logFunction) -> TagXMLHeader:
		location = ts.location
		peeks = ts.multiPeek(3)
		if len(peeks) < 3:
			return None
		#print([ (t.type + ":" + t.text) for t in peeks ])
		if peeks[0].type != "xml":
			return None
		tag = TagXMLHeader(location)
		ts.skip(1)

		while True:
			if ts.isEOS:
				raise jk_tokenizingparsing.ParserErrorException(ts.location, "P0001: Unexpected EOS", "tryEatSpecialTag")
			t = ts.peek()
			if t.type == "xmlf":
				ts.skip()
				tag.locationTo = ts.location
				return tag
			if t.type in [ "w", "s", "d" ]:
				ts.skip()
				continue
			if bBeTolerant:
				if logFunction:
					logFunction("Unexpected token: " + str(peeks[0]))
				ts.skip()
			else:
				raise jk_tokenizingparsing.ParserErrorException(ts.location, "P0002: Unexpected token", "tryEatSpecialTag", ts.getTokenPreview(20))
	#



	def __tryEatBeginTag(self, ts:jk_tokenizingparsing.TokenStream, bBeTolerant:bool, logFunction) -> TagBegin:
		location = ts.location
		peeks = ts.multiPeek(2)
		if len(peeks) < 2:
			return None
		if (peeks[0].type != "b") or (peeks[1].type != "w"):
			return None
		tag = TagBegin(location, peeks[1].text)
		ts.skip(2)
		# print()

		while True:
			if ts.isEOS:
				raise jk_tokenizingparsing.ParserErrorException(ts.location, "P0001: Unexpected EOS", "tryEatBeginTag")
			peeks = ts.multiPeek(3)
			# print([ (p.type + ":" + repr(p.text)) for p in peeks ])
			if len(peeks) == 3:
				if (peeks[0].type == "w") and (peeks[1].type == "d") and (peeks[1].text == "=") and (peeks[2].type in [ "s", "w" ]):
					tag.attributes[peeks[0].text] = peeks[2].text
					ts.skip(3)
					continue
			if peeks[0].type == "f":
				if peeks[0].text == "/>":
					tag.bWithTermination = True
				ts.skip()
				tag.locationTo = ts.location
				return tag
			if peeks[0].type == "w":
				tag.attributes[peeks[0].text] = None
				ts.skip()
				continue
			if bBeTolerant:
				if logFunction:
					logFunction("Unexpected token: " + str(peeks[0]))
				ts.skip()
			else:
				raise jk_tokenizingparsing.ParserErrorException(ts.location, "P0002: Unexpected token", "tryEatBeginTag", ts.getTokenPreview(20))
	#



	def __tryEatEndTag(self, ts:jk_tokenizingparsing.TokenStream, bBeTolerant:bool, logFunction) -> TagEnd:
		location = ts.location
		peeks = ts.multiPeek(2)
		if len(peeks) < 2:
			return None
		if (peeks[0].type != "e") or (peeks[1].type != "w"):
			return None
		tag = TagEnd(location, peeks[1].text)
		ts.skip(2)

		while True:
			if ts.isEOS:
				raise jk_tokenizingparsing.ParserErrorException(ts.location, "P0001: Unexpected EOS", "tryEatEndTag")
			peek = ts.peek()
			if peek.type == "f":
				ts.skip()
				tag.locationTo = ts.location
				return tag
			ts.skip()
	#



	def __tryEatComment(self, ts:jk_tokenizingparsing.TokenStream, bBeTolerant:bool, logFunction) -> TagComment:
		location = ts.location
		peeks = ts.multiPeek(3)
		if len(peeks) < 3:
			return None
		#print([ (t.type + ":" + t.text) for t in peeks ])
		if (peeks[0].type != "xb") or (peeks[1].type != "xc") or (peeks[2].type != "xf"):
			return None
		tag = TagComment(location, peeks[1].text)
		ts.skip(3)
		tag.locationTo = ts.location
		return tag
	#



	def tokenizeFile(self, filePath:str, bBeTolerant:bool = False, logFunction = None, debugMessageWriter = None):
		with open(filePath, "r") as f:
			textData = f.read()
		return self.tokenizeText(textData, filePath, bBeTolerant, logFunction, debugMessageWriter)
	#



	#
	# This method tokenizes the specified text data and produces the following output tokens:
	#
	# * TagBegin (with `bWithTermination` == `False`)
	# * TagBegin (with `bWithTermination` == `True`)
	# * TagComment
	# * TagEnd
	# * TagSpecial
	# * Token
	#
	def tokenizeText(self, textData:str, sourceID = None, bBeTolerant:bool = False, logFunction = None, debugMessageWriter = None):
		tokens = list(self.__tokenizer.tokenize(textData, sourceID, debugMessageWriter = debugMessageWriter))
		#for t in tokens:
		#	print(t)
		ts = jk_tokenizingparsing.TokenStream(tokens)
		while not ts.isEOS:
			# print(ts.peek())
			bProcessed = False
			for m in self.__tokMethods:
				t = m(ts, bBeTolerant, logFunction)
				if t:
					yield t
					bProcessed = True
					break
			if not bProcessed:
				yield ts.read()
	#



#



