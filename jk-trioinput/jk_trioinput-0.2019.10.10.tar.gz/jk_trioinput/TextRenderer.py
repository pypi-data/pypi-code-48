

import jk_console



class TextRenderer(object):

	def __init__(self, cx:int, cy:int, width:int = -1, syntaxHighlighter = None,
		arrowColor:str = jk_console.Console.ForeGround.STD_YELLOW,
		defaultTextColor:str = jk_console.Console.ForeGround.STD_WHITE,
		backgroundColor:str = jk_console.Console.BackGround.STD_BLACK):

		assert isinstance(cx, int)
		assert cx >= 0
		assert isinstance(cy, int)
		assert cy >= 0
		assert isinstance(width, int)
		if syntaxHighlighter:
			assert callable(syntaxHighlighter)
		assert isinstance(arrowColor, str)
		assert isinstance(defaultTextColor, str)
		assert isinstance(backgroundColor, str)

		self.__backgroundColor = backgroundColor
		self.__arrowColor = arrowColor
		self.__defaultTextColor = defaultTextColor
		self.__cx = cx
		self.__cy = cy
		if width < 0:
			width = jk_console.Console.width() - cx
		else:
			width = max(width, jk_console.Console.width - cx)
		width -= 1									# Reduce width by 1 to allow room for the cursor
		self.__width = width						# The total width of the viewport
		self.__middleX = width // 2					# The center of the viewport
		self.__nLeftChars = width // 2				# Number of characters we can display to left of center without scrolling
		self.__nRightChars = width - self.__middleX	# Number of characters we can display to right of center without scrolling
		self.__syntaxHighlighter = syntaxHighlighter
		self.__scrollOfsX = 0
	#

	def render(self, text:str, cursorPos:int):
		debugText = ""

		# Define default color map:
		#	0 = scroll arrows
		#	1 = used as default, if syntax highlighter does not exist

		colorMap = {
			0: self.__arrowColor,
			1: self.__defaultTextColor,
		}
		colorMapR = {
			self.__arrowColor: 0,
			self.__defaultTextColor: 1,
		}
		nColorIndex = 2

		# Result:
		# * Initial data in <c>colorMap</c> and <c>colorMapR</c>

		# ----------------------------------------------------------------

		# Add more colors depending on highlighter.
		# Split the text into characters.

		bufColor = []
		bufText = []
		if self.__syntaxHighlighter:
			for color, chunk in self.__syntaxHighlighter(text):
				if color in colorMapR:
					nColor = colorMapR[color]
				else:
					nColor = nColorIndex
					colorMapR[color] = nColorIndex
					colorMap[nColorIndex] = color
					nColorIndex += 1
				for c in chunk:
					bufColor.append(nColor)
					bufText.append(c)
		else:
			for c in text:
				bufColor.append(1)
				bufText.append(c)

		# Result:
		# * Modification of <c>colorMap</c> and <c>colorMapR</c>
		# * <c>bufColor</c> receives all color indices
		# * <c>bufText</c> receives all characters

		# ----------------------------------------------------------------

		# If buffer is longer than view, try to scroll to center.

		if len(bufText) > self.__width:
			scrollOfsX = cursorPos - self.__middleX
			if scrollOfsX >= len(bufText) - self.__width:
				scrollOfsX = len(bufText) - self.__width
			if scrollOfsX < 0:
				scrollOfsX = 0
		else:
			scrollOfsX = 0

		bIsClippedLeft = scrollOfsX > 0
		bIsClippedRight = len(bufText) - scrollOfsX > self.__width

		# Result:
		# * <c>scrollOfsX</c> number of characters scrolled horizontally

		# ----------------------------------------------------------------

		# Extract data for rendering

		screenText = bufText
		screenColors = bufColor
		if scrollOfsX > 0:
			if bIsClippedLeft:
				screenText = [ "«" ] + screenText[scrollOfsX + 1:]
				screenColors = [ 0 ] + screenColors[scrollOfsX + 1:]
			else:
				screenText = screenText[scrollOfsX:]
				screenColors = screenColors[scrollOfsX:]
		if len(screenText) > self.__width:
			if bIsClippedRight:
				screenText = screenText[:self.__width - 1] + [ "»" ]
				screenColors = screenColors[:self.__width - 1] + [ 0 ]
			else:
				screenText = screenText[:self.__width]
				screenColors = screenColors[:self.__width]

		# Result:
		# * <c>screenText</c> receives the text to render
		# * <c>screenColors</c> receives the colors for the text to render

		# ----------------------------------------------------------------

		# Compile output string (integrating all colors)

		nLastColor = None
		buf = []
		for nColor, c in zip(screenColors, screenText):
			if nColor != nLastColor:
				buf.append(colorMap[nColor] + c)
				nLastColor = nColor
			else:
				buf.append(c)
		s = "".join(buf)

		# Result:
		# * <c>s</c> receives the text to render

		# ----------------------------------------------------------------

		# Print debug information

		"""
		n = 0
		for name, value in [
			("scrollOfsX", scrollOfsX),
			("bIsClippedLeft", bIsClippedLeft),
			("bIsClippedRight", bIsClippedRight),
			("s", s),
			("debugText", debugText),
			]:
			jk_console.Console.printAt(0, n, jk_console.Console.ForeGround.STD_YELLOW + name + "=" + repr(value) + " " * 20, False)
			n += 1
		jk_console.Console.printAt(0, n, " " * 80, False)
		"""

		# ----------------------------------------------------------------

		# print output string

		while len(s) < self.__width:
			s += " "
		s = self.__backgroundColor + s + jk_console.Console.RESET
		jk_console.Console.printAt(self.__cx, self.__cy, s, True)
		jk_console.Console.moveCursorTo(self.__cx - scrollOfsX + cursorPos, self.__cy)
	#

	def renderCursorOnly(self, text:str, cursorPos:int):
		debugText = ""

		# Define default color map:
		#	0 = scroll arrows
		#	1 = used as default, if syntax highlighter does not exist

		colorMap = {
			0: self.__arrowColor,
			1: self.__defaultTextColor,
		}
		colorMapR = {
			self.__arrowColor: 0,
			self.__defaultTextColor: 1,
		}
		nColorIndex = 2

		# Result:
		# * Initial data in <c>colorMap</c> and <c>colorMapR</c>

		# ----------------------------------------------------------------

		# Add more colors depending on highlighter.
		# Split the text into characters.

		bufColor = []
		bufText = []
		if self.__syntaxHighlighter:
			for color, chunk in self.__syntaxHighlighter(text):
				if color in colorMapR:
					nColor = colorMapR[color]
				else:
					nColor = nColorIndex
					colorMapR[color] = nColorIndex
					colorMap[nColorIndex] = color
					nColorIndex += 1
				for c in chunk:
					bufColor.append(nColor)
					bufText.append(c)
		else:
			for c in text:
				bufColor.append(1)
				bufText.append(c)

		# Result:
		# * Modification of <c>colorMap</c> and <c>colorMapR</c>
		# * <c>bufColor</c> receives all color indices
		# * <c>bufText</c> receives all characters

		# ----------------------------------------------------------------

		# If buffer is longer than view, try to scroll to center.

		if len(bufText) > self.__width:
			scrollOfsX = cursorPos - self.__middleX
			if scrollOfsX >= len(bufText) - self.__width:
				scrollOfsX = len(bufText) - self.__width
			if scrollOfsX < 0:
				scrollOfsX = 0
		else:
			scrollOfsX = 0

		bIsClippedLeft = scrollOfsX > 0
		bIsClippedRight = len(bufText) - scrollOfsX > self.__width

		# Result:
		# * <c>scrollOfsX</c> number of characters scrolled horizontally

		# ----------------------------------------------------------------

		# move cursor

		jk_console.Console.moveCursorTo(self.__cx - scrollOfsX + cursorPos, self.__cy)
	#

#









