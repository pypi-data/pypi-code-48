#!/usr/bin/env python3


import re
import collections






from .Token import *
from .ParserErrorException import *
from .TokenizerAction import *
from .TokenizerPattern import *
from .TokenizingTable import *
from .TextBuffer import *
from ._TokenizerPatternTuple import _TokenizerPatternTuple






#
# The base class or tokenizers.
#
class TokenizerBase(object):

	class _TokenizationState(object):

		def __init__(self, tables, text, sourceID):
			assert isinstance(tables, (tuple, list))
			assert isinstance(text, str)
			if sourceID:
				assert isinstance(sourceID, str)
			self.__tables = tables
			self.textData = text
			self.sourceID = sourceID
			self.buffer = ""
			self.lineNo = 0
			self.charPos = 0
			self.i = 0
			self.spanEndI = 0
			self.spanLength = 0
			self.spanText = ""
			self.stateID = 0
			self.buffer = TextBuffer()
		#

		def dump(self, debugMessageWriter):
			assert callable(debugMessageWriter)
			debugMessageWriter("State(")
			debugMessageWriter("\tstateID=" + str(self.stateID))
			debugMessageWriter("\tstateName=" + self.__tables[self.stateID].tableName)
			debugMessageWriter("\tlineNo=" + str(self.lineNo))
			debugMessageWriter("\tcharPos=" + str(self.charPos))
			debugMessageWriter("\ti=" + str(self.i))
			debugMessageWriter("\tspanEndI=" + str(self.spanEndI))
			debugMessageWriter("\tspanLength=" + str(self.spanLength))
			debugMessageWriter("\tspanText=" + repr(self.spanText))
			debugMessageWriter("\tbuffer=" + repr(self.buffer))
			debugMessageWriter(")")
		#
	#



	# ////////////////////////////////////////////////////////////////
	# // Constructors
	# ////////////////////////////////////////////////////////////////



	def __init__(self, tables):
		assert isinstance(tables, (tuple, list))
		if len(tables) == 0:
			raise Exception("Invalid data!")

		i = 0
		for table in tables:
			assert isinstance(table, TokenizingTable)
			assert table.tableID == i
			i += 1

		self.__tables = tuple(tables)
	#



	# ////////////////////////////////////////////////////////////////
	# // Properties
	# ////////////////////////////////////////////////////////////////



	# ////////////////////////////////////////////////////////////////
	# // Static Methods
	# ////////////////////////////////////////////////////////////////



	#
	# Create a set of empty tables.
	#
	# @param	int numberOfTables		The number of tables to create.
	# @return	tuple					A tuple containing exactly the number of tables specified.
	#
	@staticmethod
	def createTables(numberOfTables):
		assert isinstance(numberOfTables, int)
		assert numberOfTables > 1

		ret = []
		for n in range(0, numberOfTables):
			ret.append(TokenizingTable(n))
		return tuple(ret)
	#



	# ////////////////////////////////////////////////////////////////
	# // Private Methods
	# ////////////////////////////////////////////////////////////////



	#
	# Processes the action.
	#
	# @return		Token						Either <c>None</c> or a token.
	# @param		TokenizerActionTuple a		The current action to perform.
	# @param		_TokenizationState state	The current state.
	# @param		int nextLineNo				The next line number.
	# @param		int nextCharPos				The next character position.
	#
	def __processAction(self, a, state, nextLineNo, nextCharPos, debugMessageWriter = None):
		if a.actionID == EnumAction.ERROR:
			if debugMessageWriter != None:
				debugMessageWriter("\t\tPerforming action :: ERROR: " + str(a))

			sourceCodeLocation = SourceCodeLocation(state.sourceID, state.lineNo, state.charPos, state.lineNo, state.charPos)
			stateName = self.__tables[state.stateID].tableName
			textClip = state.textData[state.i:]
			if len(textClip) > 20:
				textClip = textClip[:20] + "..."
			raise ParserErrorException(sourceCodeLocation, a.data, stateName, textClip)

		elif a.actionID == EnumAction.ADVANCE:
			if debugMessageWriter != None:
				debugMessageWriter("\t\tPerforming action :: ADVANCE: " + str(a))

			state.i = state.spanEndI
			state.lineNo = nextLineNo
			state.charPos = nextCharPos
			return None

		elif a.actionID == EnumAction.SWITCHSTATE:
			if debugMessageWriter != None:
				debugMessageWriter("\t\tPerforming action :: SWITCHSTATE: " + str(a) + " -- " + self.__tables[int(a.data)].tableName)

			state.stateID = int(a.data)
			return None

		elif a.actionID == EnumAction.EMITGENERATE:
			if debugMessageWriter != None:
				debugMessageWriter("\t\tPerforming action :: EMITGENERATE: " + str(a))

			return Token(a.data, "", state.sourceID, state.lineNo, state.charPos, nextLineNo, nextCharPos)

		elif a.actionID == EnumAction.EMITELEMENT:
			if debugMessageWriter != None:
				debugMessageWriter("\t\tPerforming action :: EMITELEMENT: " + str(a))

			if a.convertTextDelegate:
				s = a.convertTextDelegate(state.spanText)
			else:
				s = state.spanText
			return Token(a.data, s, state.sourceID, state.lineNo, state.charPos, nextLineNo, nextCharPos)

		elif a.actionID == EnumAction.CLEARBUFFER:
			if debugMessageWriter != None:
				debugMessageWriter("\t\tPerforming action :: CLEARBUFFER: " + str(a))

			state.buffer.clear(state.lineNo, state.charPos)
			return None

		elif a.actionID == EnumAction.APPENDELEMENTTOBUFFER:
			if debugMessageWriter != None:
				debugMessageWriter("\t\tPerforming action :: APPENDELEMENTTOBUFFER: " + str(a))

			if a.convertTextDelegate:
				s = a.convertTextDelegate(state.spanText)
			else:
				s = state.spanText
			state.buffer.append(s)
			return None

		elif a.actionID == EnumAction.EMITBUFFER:
			if debugMessageWriter != None:
				debugMessageWriter("\t\tPerforming action :: EMITBUFFER: " + str(a))

			s = str(state.buffer)
			#if s:								#### !!!SYNC!!! ####
			if a.convertTextDelegate:
				s = a.convertTextDelegate(s)
			state.buffer.clear(state.lineNo, state.charPos)
			return Token(a.data, s, state.sourceID, state.buffer.beginLineNo, state.buffer.beginCharNo, nextLineNo, nextCharPos)
			#return None

		elif a.actionID == EnumAction.EMITBUFFERIFNOTEMPTY:
			if debugMessageWriter != None:
				debugMessageWriter("\t\tPerforming action :: EMITBUFFERIFNOTEMPTY: " + str(a))

			s = str(state.buffer)
			#if s:								#### !!!SYNC!!! ####
			if a.convertTextDelegate:
				s = a.convertTextDelegate(s)
			state.buffer.clear(state.lineNo, state.charPos)
			if s:
				return Token(a.data, s, state.sourceID, state.buffer.beginLineNo, state.buffer.beginCharNo, nextLineNo, nextCharPos)
			else:
				return None

		elif a.actionID == EnumAction.APPENDTEXTTOBUFFER:
			if debugMessageWriter != None:
				debugMessageWriter("\t\tPerforming action :: APPENDTEXTTOBUFFER: " + str(a))

			state.buffer.append(a.data)
			return None

		else:
			raise Exception()
	#



	def __tryMatch(self, pattern, state):
		assert isinstance(pattern, _TokenizerPatternTuple)

		if pattern.patternID == EnumPattern.EXACTCHAR:
			if state.textData[state.i] == pattern.data:
				state.spanLength = 1
				state.spanEndI = state.i + 1
				state.spanText = str(state.textData[state.i])
				return True

		elif pattern.patternID == EnumPattern.ANYCHAR:
			if pattern.data.find(state.textData[state.i]) >= 0:
				state.spanLength = 1
				state.spanEndI = state.i + 1
				state.spanText = state.textData[state.i]
				return True

		elif pattern.patternID == EnumPattern.EXACTSTRING:
			if (pattern.dataLength <= len(state.textData) - pattern.dataLength) \
				and (pattern.data == state.textData[state.i:state.i + pattern.dataLength]):
				state.spanLength = pattern.dataLength
				state.spanEndI = state.i + pattern.dataLength
				state.spanText = pattern.data
				return True

		elif pattern.patternID == EnumPattern.REGEX:
			m = pattern.data.match(state.textData, state.i)
			if m:
				mEnd = m.end()
				mLen = mEnd - state.i
				state.spanEndI = mEnd
				state.spanText = state.textData[state.i:mEnd]
				state.spanLength = mLen
				return True

		else:
			raise Exception()
		
		return False
	#



	# ////////////////////////////////////////////////////////////////
	# // Methods
	# ////////////////////////////////////////////////////////////////



	def allTokenTypes(self):
		outSet = set()

		for t in self.__tables:
			t.collectAllTokenTypes(outSet)

		return sorted(list(outSet))
	#



	#
	# Tokenizes the specified string.
	#
	# The following token types are supported:
	# * "d" : Delimiter
	# * "i" : Integer
	# * "f" : Float
	# * "s" : String
	# * "w" : Word
	# * "eol" : New line
	# * "eos" : End of stream
	#
	# @param	str textData		The text data to tokenize.
	# @param	str sourceID		A file path or an URL that defines the origin of the source.
	# @return	iterator<Token>		Returns an iterator that provides tokens.
	#
	def tokenize(self, textData, sourceID = None, debugMessageWriter = None):
		maxi = len(textData)

		if debugMessageWriter != None:
			assert callable(debugMessageWriter)
			debugMessageWriter(":: Now tokenizing " + str(maxi) + " characters ...")

		state = TokenizerBase._TokenizationState(self.__tables, textData, sourceID)
		currentTable = None

		while state.i < maxi:
			if debugMessageWriter != None:
				debugMessageWriter("--------------------------------------------------------------------------------------------------------------------------------")

			if (state.stateID < 0) or (state.stateID >= len(self.__tables)):
				raise Exception("Requested tokenization table does not exist: " + str(state.stateID))

			if debugMessageWriter != None:
				debugMessageWriter(":: " + self.__tables[state.stateID].tableName + " :: Next character: " + repr(state.textData[state.i]))

			currentTable = self.__tables[state.stateID]
			selectedActions = None

			bMatch = False
			for pr in currentTable.rows:
				# can we match a specific pattern?
				bMatch = self.__tryMatch(pr.pattern, state)
				if bMatch:
					# yes, we can
					if debugMessageWriter != None:
						debugMessageWriter(":: " + self.__tables[state.stateID].tableName + " :: -- found pattern: " + str(pr.pattern.patternType) + " -- " + str(pr.pattern))
					selectedActions = pr.actions
					break
				else:
					if debugMessageWriter != None:
						debugMessageWriter(":: " + self.__tables[state.stateID].tableName + " :: -- pattern attempt failed: " + str(pr.pattern.patternType))

			if not bMatch:
				# as we didn't have a match with a specific pattern we proceed with "other"
				if debugMessageWriter != None:
					debugMessageWriter(self.__tables[state.stateID].tableName + " :: no rule match => default character processing")
				state.spanLength = 1
				state.spanEndI = state.i + 1
				state.spanText = state.textData[state.i]
				selectedActions = currentTable.onOtherActions

			nextLineNo = state.lineNo
			nextCharPos = state.charPos
			for c in state.spanText:
				if c == '\n':
					nextLineNo += 1
					nextCharPos = 0
				else:
					nextCharPos += 1

			if debugMessageWriter != None:
				state.dump(debugMessageWriter)

			for a in selectedActions:
				token = self.__processAction(a, state, nextLineNo, nextCharPos, debugMessageWriter)
				if token:
					yield token

		# we've arrived at the end of the data stream

		currentTable2 = self.__tables[state.stateID]
		for a in currentTable2.onEOSActions:
			token = self.__processAction(a, state, state.lineNo, state.charPos, debugMessageWriter)
			if token:
				yield token

		if debugMessageWriter != None:
			debugMessageWriter(":: Tokenizing completed.")

	#

#








