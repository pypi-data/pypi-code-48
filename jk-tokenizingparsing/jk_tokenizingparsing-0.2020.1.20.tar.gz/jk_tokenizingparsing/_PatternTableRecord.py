

import collections


from ._TokenizerPatternTuple import _TokenizerPatternTuple




class _PatternTableRecord(object):

	def __init__(self, pattern:_TokenizerPatternTuple, actions = None):
		assert isinstance(pattern, _TokenizerPatternTuple)
		if actions:
			assert isinstance(actions, (list, tuple))
		self.pattern = pattern
		self.actions = actions
	#

#


