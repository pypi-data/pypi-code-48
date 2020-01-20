

from jk_testing import Assert
import typing

from ..TokenStream import TokenStream
from ._Triplet import _Triplet
from .AbstractTokenPattern import AbstractTokenPattern
from .TPOptional import TPOptional



class TPAlt(AbstractTokenPattern):

	def __init__(self, *args, emitName:str = None, emitValue = None):
		assert len(args) > 0
		for a in args:
			Assert.isInstance(a, AbstractTokenPattern)
			if isinstance(a, TPOptional):
				raise Exception("An TPOptional element should not be part of a TPAlt element as this breaks matching!")
		self.__tokenPatterns = args
		self.emitName = emitName
		self.emitValue = emitValue
	#

	def doMatch(self, ts:TokenStream):
		assert isinstance(ts, TokenStream)

		for tp in self.__tokenPatterns:
			m, mD = tp.doMatch(ts)
			if m:
				if self.emitName:
					return m, _Triplet(self.emitName, self.emitValue, mD)
				else:	# optimization
					return m, mD
		return False, None
	#

#







