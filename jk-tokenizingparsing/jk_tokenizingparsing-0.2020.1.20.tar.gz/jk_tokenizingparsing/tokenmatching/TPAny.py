

from jk_testing import Assert
import typing

from ..TokenStream import TokenStream
from .AbstractTokenPattern import AbstractTokenPattern, _Triplet
from .TPOptional import TPOptional



class TPAny(AbstractTokenPattern):

	def __init__(self, *args, emitName:str = None, emitValue = None):
		assert len(args) > 0
		for a in args:
			Assert.isInstance(a, AbstractTokenPattern)
			if isinstance(a, TPOptional):
				raise Exception("An TPOptional element should not be part of a TPAny element as this breaks matching!")
		if emitName is not None:
			Assert.isInstance(emitName, str)
		self.__tokenPatterns = args
		if emitName is not None:
			assert isinstance(emitName, str)
		self.emitName = emitName
		self.emitValue = emitValue
	#

	def doMatch(self, ts:TokenStream):
		assert isinstance(ts, TokenStream)

		mark = ts.mark()

		mDs = []
		allTPs = list(self.__tokenPatterns)

		while allTPs:

			bFound = False
			for tp in allTPs:
				m, mD = tp.doMatch(ts)
				if m:
					mDs.append(mD)
					allTPs.remove(tp)
					bFound = True
					break
			if not bFound:
				break

		return True, _Triplet(self.emitName, self.emitValue, mDs)
	#

#






