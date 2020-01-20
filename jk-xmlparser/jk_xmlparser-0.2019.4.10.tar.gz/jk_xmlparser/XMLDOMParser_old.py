

import re

#from jk_testing import Assert
from jk_simplexml import *
from jk_tokenizingparsing import Token

from .XMLDOMParseException import XMLDOMParseException
from .TagBegin import TagBegin
from .TagComment import TagComment
from .TagEnd import TagEnd
from .TagSpecial import TagSpecial
from .XMLTokenizerImpl import XMLTokenizerImpl



class _DebuggingProtocol(object):

	def __init__(self):
		self.data = []
	#

	def print(self, s):
		self.data.append(str(s))
	#

#



class XMLDOMParser(object):

	def __init__(self, bNormalizeStr:bool = False, bBeTolerant:bool = True, bPreserveLineEndings:bool = False,
		bEnableDebugging:bool = False):
		self.__xmlTokenizerImpl = XMLTokenizerImpl()
		self.__bNormalizeStr = bNormalizeStr
		self.__bBeTolerant = bBeTolerant
		self.__bPreserveLineEndings = bPreserveLineEndings

		self.__enableDebugging_TokenizingProtocol = bEnableDebugging
		self.__enableDebugging_TokenizationProtocol = bEnableDebugging
		self.__enableDebugging_ParsingProtocol = bEnableDebugging
		self.__debugging_tokenizingProtocol = None
		self.__debugging_tokenizationProtocol = None
		self.__debugging_parsingProtocol = None
	#

	def parseFile(self, filePath:str, logFunction = None, debugMessageWriter = None) -> HElement:
		with open(filePath, "r") as f:
			textData = f.read()
		return self.parseText(textData, filePath, logFunction = logFunction, debugMessageWriter = debugMessageWriter)
	#
	
	def _enableDebugging(self, bEnableDebugging:bool):
		self.__enableDebugging_TokenizingProtocol = bEnableDebugging
		self.__enableDebugging_TokenizationProtocol = bEnableDebugging
		self.__enableDebugging_ParsingProtocol = bEnableDebugging
	#

	def _debugging_getTokenizingProtocol(self):
		if self.__debugging_tokenizingProtocol:
			return "\n".join(self.__debugging_tokenizingProtocol.data)
		else:
			return None
	#

	def _debugging_getTokenizationProtocol(self):
		if self.__debugging_tokenizationProtocol:
			return "\n".join(self.__debugging_tokenizationProtocol.data)
		else:
			return None
	#

	def _debugging_getParsingProtocol(self):
		if self.__debugging_parsingProtocol:
			return "\n".join(self.__debugging_parsingProtocol.data)
		else:
			return None
	#

	def _debugging_saveProtocols(self, baseName):
		if self.__debugging_tokenizingProtocol:
			with open(baseName + "-tokenizingProtocol.txt", "w") as f:
				f.write(self._debugging_getTokenizingProtocol())

		if self.__debugging_tokenizationProtocol:
			with open(baseName + "-tokenizationProtocol.txt", "w") as f:
				f.write(self._debugging_getTokenizationProtocol())

		if self.__debugging_parsingProtocol:
			with open(baseName + "-parsingProtocol.txt", "w") as f:
				f.write(self._debugging_getParsingProtocol())
	#

	def parseText(self, textData:str, sourceID = None, logFunction = None) -> HElement:
		self.__debugging_tokenizingProtocol = _DebuggingProtocol() if self.__enableDebugging_TokenizingProtocol else None
		self.__debugging_tokenizationProtocol = _DebuggingProtocol() if self.__enableDebugging_TokenizationProtocol else None
		self.__debugging_parsingProtocol = _DebuggingProtocol() if self.__enableDebugging_ParsingProtocol else None

		tokens = list(self.__xmlTokenizerImpl.tokenizeText(textData, sourceID=sourceID, bBeTolerant=True,
			debugMessageWriter = self.__debugging_tokenizingProtocol.print if self.__debugging_tokenizingProtocol else None))

		if self.__debugging_tokenizationProtocol:
			textLines = list(enumerate(textData.split("\n")))
			pos = 0
			for t in tokens:
				if isinstance(t, Token):
					lineNo = t.lineNo + 1
				else:
					lineNo = t.locationFrom.lineNo + 1
				while (pos < len(textLines)) and (textLines[pos][0] < lineNo):
					s = str(pos + 1) + "\t" + repr(textLines[pos][1])
					self.__debugging_tokenizationProtocol.print(s)
					pos += 1

				if isinstance(t, Token):
					s = "\t\tToken<" + t.type + ", " + repr(t.text) + ", @ " + str(t.sourceID) + "(" + str(t.lineNo + 1) + ":" + str(t.charPos + 1) + ")>"
				else:
					s = "\t\t" + str(t)
				self.__debugging_tokenizationProtocol.print(s)

		# now parse

		if not tokens:
			raise XMLDOMParseException("No tokens!")

		# ignore all tokens at the head of the list that are not begin tokens. remember the first begin token.

		while tokens:
			if isinstance(tokens[0], TagBegin):
				break
			else:
				del tokens[0]
		while tokens:
			if isinstance(tokens[-1], TagEnd):
				break
			else:
				del tokens[-1]

		if not tokens:
			raise XMLDOMParseException("No begin token found!")

		if tokens[0].name != tokens[-1].name:
			raise XMLDOMParseException("No matching begin and end tokens found: " + str(tokens[0]) + " vs. " + str(tokens[-1]))

		# ----

		hroot = HElement("PARSING_ROOT")
		self.__buildDomTree([ hroot ], tokens, self.__debugging_parsingProtocol)
		if len(hroot.children) > 1:
			raise XMLDOMParseException("More than one root nodes!")
		return hroot.children[0]
	#

	def __buildDomTree(self, path:list, tokens:list, dp = None):
		for t in tokens:
			if isinstance(t, TagBegin):
				if dp:
					dp.print("Pushing on stack: " + repr(t.name) + " at " + str(t.locationFrom))
				e = HElement(t.name, [ HAttribute(k, v.strip() if v else None) for k, v in t.attributes.items() ], None)
				path[-1].children.append(e)
				if not t.bWithTermination:
					# decend
					path.append(e)
				#print([ repr(x) for x in path ])
				continue

			if isinstance(t, TagEnd):
				if path[-1].name != t.name:
					if self.__bBeTolerant:
						if dp:
							dp.print("No matching begin token found for token " + repr(t.name) + " at " + str(t.locationFrom))
							dp.print("\tStack is:")
							for i, p in enumerate(path):
								dp.print("\t\t" + str(i) + ": " + str(p))
							dp.print("\tTrying to compensate ...")

						# try to find matching begin token
						iFound = -1
						for i in range(len(path) - 2, -1, -1):
							dp.print("\tLooking at " + str(i) + ": " + str(path[i]))
							if path[i].name == t.name:
								iFound = i
								dp.print("\tCompensating: " + repr(path[i].name))
								break
						if iFound >= 0:
							path = path[:i]
							if dp:
								dp.print("\tSkipping " + str(len(path) - i + 1) + " token(s).")
						else:
							if dp:
								dp.print("\tNo match found, ignoring this token.")
						continue
					else:
						raise Exception("No matching begin token found for token: " + str(t))
				else:
					if dp:
						dp.print("Removing from stack: " + repr(path[-1]))
					del path[-1]
					#print([ repr(x) for x in path ])
					continue

			if isinstance(t, TagComment):
				# ignore
				#print([ repr(x) for x in path ])
				continue

			#if isinstance(t, TagSpecial):
			#	# ignore
			#	#print([ repr(x) for x in path ])
			#	continue

			"""
			nodeName = path[-1].name
			bAddAnyway = False
			if nodeName in [ ]:
				# preserve leading and trailing spaces
				s = self.__normalizeStrWithoutTrim(t.text)
				bAddAnyway = True
			elif nodeName in [ ]:
				# preserve everything
				s = t.text
				bAddAnyway = True
			elif self.__bNormalizeStr:
				# preserve leading and trailing spaces
				s = self.__normalizeStrWithoutTrim(t.text)
				bAddAnyway = True
			else:
				# seems to be a structural node: don't preserve leading and trailing spaces
				s = self.__normalizeStrWithTrim(t.text)
			if s and (bAddAnyway or not s.isspace()):
				path[-1].children.append(HText(s))
			"""

			if self.__bNormalizeStr:
				s = t.text.strip()
			else:
				s = t.text
			if s:
				path[-1].children.append(HText(s))
			#print([ repr(x) for x in path ])
	#

	"""
	def __normalizeStrWithTrim(self, s:str):
		bLastWasSpace = False
		ret = []
		if self.__bPreserveLineEndings:
			s = s.strip("\t ")
			for c in s:
				if c == "\n":
					ret.append(c)
					bLastWasSpace = False
				elif c.isspace():
					if bLastWasSpace:
						continue
					else:
						ret.append(" ")
						bLastWasSpace = True
				else:
					ret.append(c)
					bLastWasSpace = False
		else:
			s = s.strip("\n\t ")
			for c in s:
				if c.isspace():
					if bLastWasSpace:
						continue
					else:
						ret.append(" ")
						bLastWasSpace = True
				else:
					ret.append(c)
					bLastWasSpace = False
		return "".join(ret)
	#

	def __normalizeStrWithoutTrim(self, s:str):
		bLastWasSpace = False
		ret = []
		if self.__bPreserveLineEndings:
			for c in s:
				if c == "\n":
					ret.append(c)
					bLastWasSpace = False
				elif c.isspace():
					if bLastWasSpace:
						continue
					else:
						ret.append(" ")
						bLastWasSpace = True
				else:
					ret.append(c)
					bLastWasSpace = False
		else:
			for c in s:
				if c.isspace():
					if bLastWasSpace:
						continue
					else:
						ret.append(" ")
						bLastWasSpace = True
				else:
					ret.append(c)
					bLastWasSpace = False
		return "".join(ret)
	#

	def __isStructuralNode(self, nodeName:str):
		if nodeName in [ "pre", "script" ]:
			return False
		return True
	#
	"""

#













