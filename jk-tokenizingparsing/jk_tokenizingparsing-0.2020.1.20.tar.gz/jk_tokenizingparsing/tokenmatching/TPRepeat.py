

from jk_testing import Assert
import typing

from ..TokenStream import TokenStream
from ._Triplet import _Triplet
from .AbstractTokenPattern import AbstractTokenPattern



class TPRepeat(AbstractTokenPattern):

	def __init__(self, tp:AbstractTokenPattern, delimiterPattern:AbstractTokenPattern, emitName:str = None, emitValue = None):
		assert isinstance(tp, AbstractTokenPattern)
		if delimiterPattern:
			assert isinstance(delimiterPattern, AbstractTokenPattern)
		if emitName is not None:
			Assert.isInstance(emitName, str)
		self.__tokenPattern = tp
		self.__delimiterPattern = delimiterPattern
		self.emitName = emitName
		self.emitValue = emitValue
	#

	def doMatch(self, ts:TokenStream):
		assert isinstance(ts, TokenStream)

		sequenceMatched = []

		while True:
			m, mD = self.__tokenPattern.doMatch(ts)
			if m:
				sequenceMatched.append(mD)
			else:
				break

			if self.__delimiterPattern:
				m, mD = self.__delimiterPattern.doMatch(ts)
				if m:
					continue
				else:
					break

		if sequenceMatched:
			return True, _Triplet(self.emitName, self.emitValue, sequenceMatched)
		else:
			return False, None
	#

#







