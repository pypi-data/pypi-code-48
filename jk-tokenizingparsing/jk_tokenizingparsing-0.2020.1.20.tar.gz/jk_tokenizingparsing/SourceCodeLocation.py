

from .Token import *






#
# This object represents a location in a source code file.
#
class SourceCodeLocation(object):

	def __init__(self, sourceID, lineNo, charPos, endLineNo, endCharPos):
		self.sourceID = sourceID
		self.lineNo = lineNo
		self.charPos = charPos
		self.endLineNo = endLineNo
		self.endCharPos = endCharPos
	#

	def clone(self):
		return SourceCodeLocation(self.sourceID, self.lineNo, self.charPos, self.endLineNo, self.endCharPos)
	#

	def __str__(self):
		if self.sourceID != None:
			return self.sourceID + "(" + str(self.lineNo + 1) + ":" + str(self.charPos + 1) + ")"
		else:
			return "(" + str(self.lineNo + 1) + ":" + str(self.charPos + 1) + ")"
	#

	def __repr__(self):
		if self.sourceID != None:
			return self.sourceID + "(" + str(self.lineNo + 1) + ":" + str(self.charPos + 1) + ")"
		else:
			return "(" + str(self.lineNo + 1) + ":" + str(self.charPos + 1) + ")"
	#

	@staticmethod
	def create(sourceID:str = None, lineNo:int = 0, charPos:int = 0, endLineNo:int = 0, endCharPos:int = 0):
		return SourceCodeLocation(sourceID, lineNo, charPos, endLineNo, endCharPos)
	#

	#
	# Generate a new source code location object representing the specified set of consecuting tokens.
	#
	@staticmethod
	def fromTokens(tokenA:Token, tokenB:Token):
		assert isinstance(tokenA, Token)
		assert isinstance(tokenB, Token)

		return SourceCodeLocation(tokenA.sourceID, tokenA.lineNo, tokenA.charPos, tokenB.endLineNo, tokenB.endCharPos)
	#

	#
	# Generate a new source code location object representing the specified token.
	#
	@staticmethod
	def fromToken(token:Token):
		assert isinstance(token, Token)

		return SourceCodeLocation(token.sourceID, token.lineNo, token.charPos, token.endLineNo, token.endCharPos)
	#

	#
	# Generate a new source code location object spanning from the position stored in the current object to the end of the position stord in the specified object.
	#
	def spanTo(self, sourceCodeLocation):
		assert isinstance(sourceCodeLocation, SourceCodeLocation)

		return SourceCodeLocation(self.sourceID, self.lineNo, self.charPos, sourceCodeLocation.endLineNo, sourceCodeLocation.endCharPos)
	#

#







