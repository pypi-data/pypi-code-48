

import json
from typing import Union

from jk_testing import Assert




from .SourceCodeLocation import SourceCodeLocation
from .CompiledTokenizer import CompiledTokenizer
from .TextConverterManager import TextConverterManager
from .TokenizingTable import TokenizingTable
from ._PatternTableRecord import _PatternTableRecord
from ._TokenizerActionTuple import _TokenizerActionTuple
from .TokenizerPattern import TokenizerPattern, _TokenizerPatternTuple, EnumPattern



class JSONLoader(object):

	@staticmethod
	def fromJSON(textConverterMgr:TextConverterManager, jobj:dict) -> CompiledTokenizer:
		version = JSONLoader.__getE(jobj, "version", str)
		if version != "2018-05-07":
			raise Exception("Unknown version: " + version)

		jTokenTypes = JSONLoader.__getE(jobj, "tokenTypes", (list, tuple))
		jTables = JSONLoader.__getE(jobj, "tables", (list, tuple))

		tables = []
		for i in range(0, len(jTables)):
			tables.append(JSONLoader.__deserializeTable(textConverterMgr, JSONLoader.__getE(jTables, i, dict)))

		return CompiledTokenizer(tables)
	#

	@staticmethod
	def __deserializeActions(textConverterMgr:TextConverterManager, jlist:list) -> list:
		if jlist is None:
			return None

		ret = []
		for i in range(0, len(jlist)):
			ret.append(JSONLoader.__deserializeActionTuple(textConverterMgr, JSONLoader.__getE(jlist, i, dict)))

		return ret
	#

	@staticmethod
	def __deserializePatternTuple(jobj:dict) -> _TokenizerPatternTuple:
		patternID = JSONLoader.__getE(jobj, "id", int)
		if patternID == EnumPattern.ANYCHAR:
			strData = JSONLoader.__getAnyE(jobj, "s", "strData", str)
			return TokenizerPattern.anyOfTheseChars(strData)
		elif patternID == EnumPattern.EXACTCHAR:
			charData = JSONLoader.__getAnyE(jobj, "c", "charData", str)[0]
			return TokenizerPattern.exactChar(charData)
		elif patternID == EnumPattern.EXACTSTRING:
			strData = JSONLoader.__getAnyE(jobj, "s", "strData", str)
			return TokenizerPattern.exactSequence(strData)
		elif patternID == EnumPattern.REGEX:
			regex = JSONLoader.__getAnyE(jobj, "r", "regex", str)
			return TokenizerPattern.regEx(regex)
		else:
			raise Exception()
	#

	@staticmethod
	def __deserializeActionTuple(textConverterMgr:TextConverterManager, jobj:dict) -> _TokenizerActionTuple:
		actionID = JSONLoader.__getE(jobj, "id", int)
		data = JSONLoader.__getAny(jobj, "d", "data", (dict, list, str, int, bool, float))
		textConverterName = JSONLoader.__getAny(jobj, "f", "function", str)
		# TODO: some actions require a data and/or a text converter ensure that these exist as required according to specification!
		textConverter = None
		if textConverterName != None:
			textConverter = textConverterMgr.getConverterE(textConverterName)
		return _TokenizerActionTuple(actionID, data, textConverter)
	#

	@staticmethod
	def __deserializeTable(textConverterMgr:TextConverterManager, jobj:dict) -> TokenizingTable:
		Assert.isInstance(jobj, dict)

		jrows = JSONLoader.__getE(jobj, "on", (list, tuple))

		rows = []
		if jrows is not None:
			for i in range(0, len(jrows)):
				rows.append(JSONLoader.__deserializeRow(textConverterMgr, JSONLoader.__getE(jrows, i, dict)))

		tableID = JSONLoader.__getE(jobj, "tableID", int)
		tableName = JSONLoader.__getE(jobj, "tableName", str)

		table = TokenizingTable(tableID)
		table.tableName = tableName
		for r in rows:
			table.addPatternRow(r.pattern, r.actions)

		jtemp = JSONLoader.__getE(jobj, "onOther", (list, tuple))
		if jtemp is not None:
			table.setOther(JSONLoader.__deserializeActions(textConverterMgr, jtemp))

		jtemp = JSONLoader.__getE(jobj, "onEOS", (list, tuple))
		if jtemp is not None:
			table.setEOS(JSONLoader.__deserializeActions(textConverterMgr, jtemp))

		return table
	#

	@staticmethod
	def __getAny(d:dict, key1:str, key2:str, typeOrTypes):
		v = d.get(key1)
		if v is None:
			v = d.get(key2)
		if v is not None:
			Assert.isInstance(v, typeOrTypes)
		return v
	#

	@staticmethod
	def __get(d:Union[dict,list,tuple], key:Union[str,int], typeOrTypes):
		if isinstance(d, dict):
			v = d.get(key)
		else:
			v = d[key]
		if v is not None:
			Assert.isInstance(v, typeOrTypes)
		return v
	#

	@staticmethod
	def __getAnyE(d:dict, key1:str, key2:str, typeOrTypes):
		v = d.get(key1)
		if v is None:
			v = d.get(key2)
		if v is None:
			raise Exception("None of these keys exist: " + repr(key1) + ", " + repr(key2))
		if v is not None:
			Assert.isInstance(v, typeOrTypes)
		return v
	#

	@staticmethod
	def __getE(d:Union[dict,list,tuple], key:Union[str,int], typeOrTypes):
		if isinstance(d, dict):
			v = d.get(key)
		else:
			v = d[key]
		if v is None:
			raise Exception("No such key: " + repr(key))
		if v is not None:
			Assert.isInstance(v, typeOrTypes)
		return v
	#

	@staticmethod
	def __deserializeRow(textConverterMgr:TextConverterManager, jobj:dict) -> _PatternTableRecord:
		pattern = JSONLoader.__deserializePatternTuple(JSONLoader.__getAnyE(jobj, "p", "pattern", dict))
		actions = JSONLoader.__deserializeActions(textConverterMgr, JSONLoader.__getAnyE(jobj, "a", "actions", (tuple, list)))
		return _PatternTableRecord(pattern, actions)
	#

#










