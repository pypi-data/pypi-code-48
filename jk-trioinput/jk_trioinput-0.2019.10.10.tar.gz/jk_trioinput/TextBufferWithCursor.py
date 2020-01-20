


import jk_console






class TextBufferWithCursor(object):

	def __init__(self):
		self.__buffer = []
		self.__cpos = 0
	#

	def initialize(self, text:str):
		self.__buffer = list(text)
		self.__cpos = len(text)
	#

	@property
	def isEmpty(self):
		return len(self.__buffer) == 0
	#

	@property
	def cursorPos(self):
		return self.__cpos
	#

	def deleteUnderCursor(self):
		if self.__cpos < len(self.__buffer):
			del self.__buffer[self.__cpos]
	#

	def _classifyChar(self, c:str):
		if c in "!\"§$%&/()=?'²³{[]}\\`+*~#'-.:,;µ|<>@":
			return "d"
		elif c in " \t":
			return "_"
		else:
			return "w"
	#

	def _strToClassList(self, s:list):
		return [ self._classifyChar(c) for c in s ]
	#

	def _findNextStopRight(self, pos:int):
		s = self._strToClassList(self.__buffer)
		cref = s[pos]
		if cref == "d":
			cref == "x"

		while True:
			pos += 1
			if pos >= len(s):
				return len(s)

			if s[pos] != cref:
				if s[pos] == "_":
					# move through this space section
					cref = "_"
				else:
					return pos
	#

	def _findNextStopLeft(self, pos:int):
		s = self._strToClassList(reversed(self.__buffer))
		pos = len(s) - pos

		cref = s[pos]
		if cref == "d":
			cref == "x"

		while True:
			pos += 1

			if pos >= len(s):
				return 0

			if s[pos] != cref:
				if cref == "_":
					# move through this word section
					cref = s[pos]
				else:
					return len(s) - pos
	#

	def moveCursorLeft(self):
		if self.__cpos > 0:
			self.__cpos -= 1
			return True
		else:
			return False
	#

	def moveCursorRight(self):
		if self.__cpos < len(self.__buffer):
			self.__cpos += 1
			return True
		else:
			return False
	#

	def jumpCursorRight(self):
		if self.__cpos < len(self.__buffer):
			n = self._findNextStopRight(self.__cpos)
			if n < 0:
				return False
			self.__cpos = n
			return True
		else:
			return False
	#

	def jumpCursorLeft(self):
		if self.__cpos > 0:
			n = self._findNextStopLeft(self.__cpos)
			self.__cpos = n
			return True
		else:
			return False
	#

	def moveCursorToStart(self):
		self.__cpos = 0
	#

	def moveCursorToEnd(self):
		self.__cpos = len(self.__buffer)
	#

	def insertAtCursor(self, c:str, bMoveCursor:bool = True):
		self.__buffer.insert(self.__cpos, c)
		if bMoveCursor:
			self.__cpos += 1
	#

	def printToConsoleAt(self, cx:int, cy:int, width:int = -1, syntaxHighlighter = None):
		s = "".join(self.__buffer)

		if syntaxHighlighter:
			buf = []
			for color, chunk in syntaxHighlighter(s):
				buf.append(color)
				buf.append(chunk)
			s = "".join(buf)

		jk_console.Console.printAt(cx, cy, s + " ", True)
		jk_console.Console.moveCursorTo(cx + self.__cpos, cy)
	#

	def __str__(self):
		return "".join(self.__buffer)
	#

	def __repr__(self):
		return "".join(self.__buffer)
	#

	def __len__(self):
		return len(self.__buffer)
	#

	def reset(self):
		self.__buffer.clear()
		self.__cpos = 0
	#

#





