#!/usr/bin/env python3


import re
import collections






from ._TokenizerActionTuple import _TokenizerActionTuple
from ._PatternTableRecord import _PatternTableRecord
from ._TokenizerPatternTuple import _TokenizerPatternTuple
from .Token import *
from .ParserErrorException import *
from .TokenizerAction import *
from .TokenizerPattern import *







#
# This class represents a table that is part of the initialization data of a tokenizer.
#
class TokenizingTable(object):

	def __init__(self, tableID):
		self.tableID = tableID
		self.tableName = None
		self.rows = []
		self.onOtherActions = None
		self.onEOSActions = None
	#

	def addPatternRow(self, pattern, actions):
		assert isinstance(pattern, _TokenizerPatternTuple)
		assert isinstance(actions, (tuple, list))
		for action in actions:
			assert isinstance(action, _TokenizerActionTuple)
		self.rows.append(_PatternTableRecord(pattern, tuple(actions)))
	#

	def setOther(self, actions):
		assert isinstance(actions, (tuple, list))
		for action in actions:
			assert isinstance(action, _TokenizerActionTuple)
		self.onOtherActions = actions
	#

	def setEOS(self, actions):
		assert isinstance(actions, (tuple, list))
		for action in actions:
			assert isinstance(action, _TokenizerActionTuple)
		self.onEOSActions = actions
	#

	def collectAllTokenTypes(self, outSet):
		for r in self.rows:
			for t in r.actions:
				if t.actionID in [ EnumAction.EMITBUFFER, EnumAction.EMITELEMENT, EnumAction.EMITGENERATE ]:
					outSet.add(t.data)

		if self.onOtherActions:
			for t in self.onOtherActions:
				if t.actionID in [ EnumAction.EMITBUFFER, EnumAction.EMITELEMENT, EnumAction.EMITGENERATE ]:
					outSet.add(t.data)

		if self.onEOSActions:
			for t in self.onEOSActions:
				if t.actionID in [ EnumAction.EMITBUFFER, EnumAction.EMITELEMENT, EnumAction.EMITGENERATE ]:
					outSet.add(t.data)
	#

#




