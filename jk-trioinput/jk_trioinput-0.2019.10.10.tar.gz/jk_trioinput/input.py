#!/usr/bin/python3



import re
import sys
import os
import json
import trio

import jk_json
import jk_console

from .TextBufferWithCursor import TextBufferWithCursor
from .TextRenderer import TextRenderer
from .ConsoleInputHistory import ConsoleInputHistory





#
# This method reads user input outputting at the current position. This way it works quite similar to <c>input()</c>.
#
async def readConsoleInput(outputText:str = None, cx:int = None, cy:int = None, syntaxHighlighter = None,
	arrowColor:str = jk_console.Console.ForeGround.STD_YELLOW,
	defaultTextColor:str = jk_console.Console.ForeGround.STD_WHITE,
	history = None) -> str:

	cx2, cy2 = jk_console.Console.getCursorPosition()
	if cx is None:
		cx = cx2
	if cy is None:
		cy = cy2

	if outputText:
		jk_console.Console.printAt(cx, cy, outputText, True)
		cx += len(outputText)

	width, height = jk_console.Console.getSize()
	#textRenderer = TextRenderer(cx, cy, width - 1, syntaxHighlighter)
	textRenderer = TextRenderer(cx, cy, syntaxHighlighter=syntaxHighlighter, arrowColor=arrowColor, defaultTextColor=defaultTextColor)

	if history is not None:
		history.resetCursor()

	buf = TextBufferWithCursor()
	textRenderer.render(buf.__str__(), buf.cursorPos)

	temp = ""

	while True:
		bChanged = False

		key = None
		#with trio.move_on_after(2):
		key = await trio.to_thread.run_sync(jk_console.Console.Input.readKey)
		if key is None:
			# timeout
			continue

		if key == jk_console.Console.Input.KEY_CURSOR_UP:
			if history is not None:
				s = history.prev()
				if s is not None:
					buf.initialize(s)
					textRenderer.render(str(buf), buf.cursorPos)
		elif key == jk_console.Console.Input.KEY_CURSOR_DOWN:
			if history is not None:
				s = history.next()
				if s is not None:
					buf.initialize(s)
					textRenderer.render(str(buf), buf.cursorPos)
				else:
					buf.initialize(temp)
					history.resetCursor()
		elif key == jk_console.Console.Input.KEY_CURSOR_LEFT:
			buf.moveCursorLeft()
		elif key == jk_console.Console.Input.KEY_CURSOR_RIGHT:
			buf.moveCursorRight()
		elif key == jk_console.Console.Input.KEY_CTRL_CURSOR_RIGHT:
			buf.jumpCursorRight()
		elif key == jk_console.Console.Input.KEY_CTRL_CURSOR_LEFT:
			buf.jumpCursorLeft()
		elif key == jk_console.Console.Input.KEY_DELETE:
			if buf.deleteUnderCursor():
				bChanged = True
		elif key == jk_console.Console.Input.KEY_BACKSPACE:
			if buf.moveCursorLeft():
				if buf.deleteUnderCursor():
					bChanged = True
		elif key == jk_console.Console.Input.KEY_TAB:
			buf.insertAtCursor(" ")
			bChanged = True
		elif key == jk_console.Console.Input.KEY_HOME:
			buf.moveCursorToStart()
		elif key == jk_console.Console.Input.KEY_HOME_NUMPAD:
			buf.moveCursorToStart()
		elif key == jk_console.Console.Input.KEY_END:
			buf.moveCursorToEnd()
		elif key == jk_console.Console.Input.KEY_END_NUMPAD:
			buf.moveCursorToEnd()
		elif key == jk_console.Console.Input.KEY_ENTER:
			print()
			break
		elif key == jk_console.Console.Input.KEY_CTRL_C:
			raise KeyboardInterrupt()
		else:
			if len(key) == 1:
				buf.insertAtCursor(key)
				bChanged = True

		if bChanged:
			temp = str(buf)

		textRenderer.render(str(buf), buf.cursorPos)

	s = str(buf)
	if history is not None:
		history.append(s)

	return s
#



