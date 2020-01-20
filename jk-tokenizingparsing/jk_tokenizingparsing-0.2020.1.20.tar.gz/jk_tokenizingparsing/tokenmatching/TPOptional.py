

from jk_testing import Assert
import typing

from ..TokenStream import TokenStream
from ._Triplet import _Triplet
from .AbstractTokenPattern import AbstractTokenPattern



class TPOptional(AbstractTokenPattern):

	def __init__(self, tp:AbstractTokenPattern, emitName:str = None, emitValue = None):
		Assert.isInstance(tp, AbstractTokenPattern)
		if emitName is not None:
			Assert.isInstance(emitName, str)
		self.__tp = tp
		self.emitName = emitName
		self.emitValue = emitValue
	#

	def doMatch(self, ts:TokenStream):
		assert isinstance(ts, TokenStream)

		m, mD = self.__tp.doMatch(ts)
		if m:
			if self.emitName:
				return True, _Triplet(self.emitName, self.emitValue, mD)
			else:	# optimization
				return True, mD
		else:
			return True, _Triplet(None, None, [])
	#

#






