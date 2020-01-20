

import sys
import typing
#import jk_json
import pprint

from ..TokenStream import TokenStream, Token
from .MatchResult import MatchResult
from ._Triplet import _Triplet



class AbstractTokenPattern(object):

	"""
	def __replace(self, listData):
		if listData is None:
			return None

		ret = []
		for v in listData:
			if isinstance(v, Token):
				ret.append(str(v))
			elif isinstance(v, (tuple, list)):
				ret.append([ self.__replace(x) for x in v ])
			else:
				ret.append(v)
		return ret
	#
	"""

	def doMatch(self, ts:TokenStream):
		raise NotImplementedError()
	#

	def match(self, ts:TokenStream) -> MatchResult:
		assert isinstance(ts, TokenStream)

		m, mD = self.doMatch(ts)
		#print("---->")
		#pprint.pprint(mD, indent=4, width=10000)
		#print("<----")
		#sys.exit(0)

		if m:
			return MatchResult(True, mD)
		else:
			return MatchResult(False, None)
	#

#






