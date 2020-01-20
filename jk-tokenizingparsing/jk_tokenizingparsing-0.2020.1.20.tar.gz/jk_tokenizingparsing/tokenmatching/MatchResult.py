

import typing

from ..TokenStream import TokenStream, Token
from ._Triplet import _Triplet



class MatchResult(object):

	def __init__(self, result:bool = False, triplet:_Triplet = None):
		assert isinstance(result, bool)
		self.result = result
		if result:
			assert isinstance(triplet, (list, tuple, _Triplet))
			self.__triplet = triplet
		else:
			self.__triplet = None

		self.__valuesStrings = None
		self.__valuesTokens = None
	#

	def __getitem__(self, key):
		if self.__valuesStrings is None:
			ret = {}
			if self.result:
				self.__walkEmitStrings(self.__triplet, ret)
			self.__valuesStrings = ret
		return self.__valuesStrings.get(key)
	#

	#
	# Get a dictionary with values as strings.
	#
	def values(self) -> dict:
		if self.__valuesStrings is None:
			ret = {}
			if self.result:
				self.__walkEmitStrings(self.__triplet, ret)
			self.__valuesStrings = ret
		return self.__valuesStrings
	#

	#
	# Get a dictionary with values as tokens.
	#
	def valuesTokens(self) -> dict:
		if self.__valuesTokens is None:
			ret = {}
			if self.result:
				self.__walkEmitTokens(self.__triplet, ret)
			self.__valuesTokens = ret
		return self.__valuesTokens
	#

	def __walkEmitStrings(self, triplet:_Triplet, outDict:dict):
		assert isinstance(triplet, _Triplet)

		if isinstance(triplet.data, Token):
			if triplet.emitName:
				if triplet.emitValue is not None:
					outDict[triplet.emitName] = triplet.emitValue
				else:
					if triplet.emitName in outDict:
						outDict[triplet.emitName].append(triplet.data.text)
					else:
						outDict[triplet.emitName] = [ triplet.data.text ]

			return [ triplet.data.text ]

		elif isinstance(triplet.data, _Triplet):
			ret = self.__walkEmitStrings(triplet.data, outDict)

			if triplet.emitName:
				if triplet.emitValue is not None:
					outDict[triplet.emitName] = triplet.emitValue
				else:
					outDict[triplet.emitName] = ret

			return ret

		else:
			ret = []
			for item in triplet.data:
				ret2 = self.__walkEmitStrings(item, outDict)
				ret.extend(ret2)

			if triplet.emitName:
				if triplet.emitValue is not None:
					outDict[triplet.emitName] = triplet.emitValue
				else:
					outDict[triplet.emitName] = ret

			return ret
	#

	def __walkEmitTokens(self, triplet:_Triplet, outDict:dict):
		assert isinstance(triplet, _Triplet)

		if isinstance(triplet.data, Token):
			if triplet.emitName:
				if triplet.emitValue is not None:
					outDict[triplet.emitName] = triplet.emitValue
				else:
					if triplet.emitName in outDict:
						outDict[triplet.emitName].append(triplet.data)
					else:
						outDict[triplet.emitName] = triplet.data

			return [ triplet.data ]

		elif isinstance(triplet.data, _Triplet):
			ret = self.__walkEmitTokens(triplet.data, outDict)

			if triplet.emitName:
				if triplet.emitValue is not None:
					outDict[triplet.emitName] = triplet.emitValue
				else:
					outDict[triplet.emitName] = ret

			return ret

		else:
			ret = []
			for item in triplet.data:
				ret2 = self.__walkEmitTokens(item, outDict)
				ret.extend(ret2)

			if triplet.emitName:
				if triplet.emitValue is not None:
					outDict[triplet.emitName] = triplet.emitValue
				else:
					outDict[triplet.emitName] = ret

			return ret
	#

	def __bool__(self):
		return self.result
	#

	def __str__(self):
		return "MatchResult(" + str(self.result) + ")"
	#

	def __repr__(self):
		return "MatchResult(" + str(self.result) + ")"
	#

	def dump(self, prefix:str = "", printFunction = None):
		assert isinstance(prefix, str)
		if printFunction:
			assert callable(printFunction)
		else:
			printFunction = print

		printFunction(prefix + "MatchResult( " + str(self.result))
		for t in self.tokens:
			printFunction(prefix + str(t))
		printFunction(prefix + "\t)")
	#

#





