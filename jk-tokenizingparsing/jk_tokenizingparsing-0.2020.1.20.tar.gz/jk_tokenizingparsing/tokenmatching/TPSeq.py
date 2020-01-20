

from jk_testing import Assert
import typing

from ..TokenStream import TokenStream
from .AbstractTokenPattern import AbstractTokenPattern, _Triplet



class TPSeq(AbstractTokenPattern):

	def __init__(self, *args, emitName:str = None, emitValue = None):
		assert len(args) > 0
		for a in args:
			Assert.isInstance(a, AbstractTokenPattern)
		self.__tokenPatterns = args
		if emitName is not None:
			Assert.isInstance(emitName, str)
		self.emitName = emitName
		self.emitValue = emitValue
	#

	def doMatch(self, ts:TokenStream):
		assert isinstance(ts, TokenStream)

		mark = ts.mark()
		mDs = []
		for tp in self.__tokenPatterns:
			m, mD = tp.doMatch(ts)
			if m:
				mDs.append(mD)
			else:
				mark.resetToMark()
				return False, None
		return True, _Triplet(self.emitName, self.emitValue, mDs)
	#

#






