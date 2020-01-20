

from jk_testing import Assert
import typing

from ..TokenStream import TokenStream, Token
from .AbstractTokenPattern import AbstractTokenPattern, _Triplet



class TP(AbstractTokenPattern):

	def __init__(self, type_:str, text_:str = None, bIgnoreCase:bool = False, emitName:str = None, emitValue = None):
		self.type = type_
		if text_ is None:
			self.text = None
			self.bIgnoreCase = False
		else:
			self.text = text_.lower() if bIgnoreCase else text_
			self.bIgnoreCase = bIgnoreCase
		if emitName is not None:
			Assert.isInstance(emitName, str)
		self.emitName = emitName
		self.emitValue = emitValue
	#

	def doMatch(self, ts:TokenStream):
		assert isinstance(ts, TokenStream)

		t = ts.peek()
		if self.bIgnoreCase:
			if (
					((self.type) and (t.type != self.type))
					or
					((self.text is not None) and (t.text.lower() != self.text))
				):
				return False, None
		else:
			if (
					((self.type) and (t.type != self.type))
					or
					((self.text is not None) and (t.text != self.text))
				):
				return False, None
		ts.skip()
		return True, _Triplet( self.emitName, self.emitValue, t )
	#

#






