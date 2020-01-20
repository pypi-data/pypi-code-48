





class ConsoleInputHistory(object):

	def __init__(self):
		self.__historyItems = []
		self.__cursor = None			# always points to the current item
	#

	def __len__(self):
		return len(self.__historyItems)
	#

	def hasChanged(self, text:str):
		if self.__cursor is None:
			return True
		if self.__cursor >= 0:
			return self.__historyItems[self.__cursor] != text
		else:
			return True
	#

	def append(self, text:str):
		if text:
			if not self.__historyItems:
				self.__historyItems.append(text)
			elif self.__historyItems[-1] != text:
				self.__historyItems.append(text)
			self.__cursor = len(self.__historyItems) - 1
	#

	def prev(self):
		if self.__cursor is None:
			self.__cursor = len(self.__historyItems) - 1
			if self.__cursor < 0:
				return None
			s = self.__historyItems[self.__cursor]
			return s

		if self.__cursor > 0:
			self.__cursor -= 1
			s = self.__historyItems[self.__cursor]
			return s
		else:
			return None
	#

	def next(self):
		if self.__cursor is None:
			return None

		if self.__cursor < len(self.__historyItems) - 1:
			self.__cursor += 1
			s = self.__historyItems[self.__cursor]
			return s
		else:
			return None
	#

	def resetCursor(self):
		self.__cursor = None
	#

#









