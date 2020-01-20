



from .Token import Token





class Serializer(object):

	def __init__(self):
		pass
	#

	@staticmethod
	def serializeToken(token:Token) -> dict:
		ret = {}
		for key in [ "type", "text", "sourceID", "lineNo", "charPos", "endLineNo", "endCharPos" ]:
			v = getattr(token, key)
			if v is not None:
				ret[key] = v
		return ret
	#

	@staticmethod
	def serializeTokens(tokens:list) -> list:
		return [
			Serializer.serializeToken(token) for token in tokens
		]
	#

	@staticmethod
	def deserializeToken(tokenDict:dict) -> Token:
		return Token(
			tokenDict.get("type", None),
			tokenDict.get("text", None),
			tokenDict.get("sourceID", None),
			tokenDict.get("lineNo", 0),
			tokenDict.get("charPos", 0),
			tokenDict.get("endLineNo", 0),
			tokenDict.get("endCharPos", 0)
		)
	#

	@staticmethod
	def deserializeTokens(tokenDicts:list) -> list:
		return [
			Serializer.deserializeToken(tokenDict) for tokenDict in tokenDicts
		]
	#

#










