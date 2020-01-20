#!/usr/bin/env python3


import re
import collections






from .Token import *
from .ParserErrorException import *
from .TokenizingTable import TokenizingTable
from ._TokenizerActionTuple import _TokenizerActionTuple







#
# A tokenization action. Use the methods provided in `TokenizerAction` to provide actions.
#
class EnumAction(object):

	ERROR = 1
	ADVANCE = 2
	SWITCHSTATE = 3
	EMITELEMENT = 4
	CLEARBUFFER = 5
	APPENDELEMENTTOBUFFER = 6
	EMITBUFFER = 7
	# DROPBUFFER = 8		-- same as CLEARBUFFER; no longer in use
	APPENDTEXTTOBUFFER = 9
	TERMINATE = 10
	EMITGENERATE = 11
	EMITBUFFERIFNOTEMPTY = 12

#



#
# A tokenization action. Use the methods provided in `TokenizerAction` to provide actions.
#
class TokenizerAction(object):

	#
	# Emit a tokenization error.
	#
	# @param	str errorCode			An error code the error message should be prefixed with. This code does not necessarily
	#									need to be unique: Multiple tokenization problems might emit the same error. (Nevertheless
	#									you should use the same error code for the same error class.)
	# @param	str errorMessage		A user friendly error message.
	# @param	str errorIdentifier		An error identifier. This ID should be unique in order to allow tracking of the
	#									error back to the tokenization rule. This is ment for debugging only.
	#
	@staticmethod
	def error(errorCode, errorMessage, errorIdentifier):
		return _TokenizerActionTuple(EnumAction.ERROR, str(errorCode) + ": " + errorMessage + " (" + str(errorIdentifier) + ")")
	#

	#
	# Advance a single character in the stream = ignore the current character.
	#
	@staticmethod
	def advance():
		return _TokenizerActionTuple(EnumAction.ADVANCE, None, None)
	#

	#
	# Switch to a differnt parsing mode.
	#
	@staticmethod
	def switchState(tableOrTableID):
		if isinstance(tableOrTableID, TokenizingTable):
			return _TokenizerActionTuple(EnumAction.SWITCHSTATE, tableOrTableID.tableID, None)
		else:
			assert isinstance(tableOrTableID, int)
			return _TokenizerActionTuple(EnumAction.SWITCHSTATE, tableOrTableID, None)
	#

	#
	# Emit a token that is generated without relation to the text. The buffer will remain untouched.
	#
	@staticmethod
	def emitGenerate(tokenType):
		return _TokenizerActionTuple(EnumAction.EMITGENERATE, tokenType, None)
	#

	#
	# Emit a token. The buffer will remain untouched.
	#
	@staticmethod
	def emitElement(tokenType, convertTextDelegate = None):
		return _TokenizerActionTuple(EnumAction.EMITELEMENT, tokenType, convertTextDelegate)
	#

	#
	# Reset the buffer. The buffer will now be empty and new data can be written to it.
	#
	@staticmethod
	def clearBuffer():
		return _TokenizerActionTuple(EnumAction.CLEARBUFFER, None, None)
	#

	#
	# Append the current parsed item to the buffer. What exactly that is and how much data this element contains depends on the current parsing action.
	#
	@staticmethod
	def appendElementToBuffer(callbackFunction = None):
		return _TokenizerActionTuple(EnumAction.APPENDELEMENTTOBUFFER, None, callbackFunction)
	#

	#
	# Emit the buffer = create a token with the specified token type containing the current buffer's content.
	#
	@staticmethod
	def emitBuffer(tokenType):
		return _TokenizerActionTuple(EnumAction.EMITBUFFER, tokenType, None)
	#

	#
	# Append the specified text to the buffer.
	#
	@staticmethod
	def appendTextToBuffer(text):
		return _TokenizerActionTuple(EnumAction.APPENDTEXTTOBUFFER, text, None)
	#

#








