#!/usr/bin/env python3


from .TokenStream import *
from .ParserErrorException import *





def debugDecorator(func):

	def func_wrapper(self, ctx, ts):
		if ctx.bDebugging:
			ctx.indent += 1
			ctx._debugBegin(func.__name__, ts.peek())

		x = func(self, ctx, ts)

		if ctx.bDebugging:
			ctx._debugEnd(func.__name__, x[0])
			ctx.indent -= 1

		return x
	#

	return func_wrapper
#



class ParserBase(object):

	#
	# Parse the tokens. Construct an abstract syntax tree from the tokens provided by the tokenizer.
	#
	# @param	Tokenizer tokenizer		The tokenizer that provides the tokens.
	#
	def parse(self, tokenizer, bDebugging = False):
		raise Exception("Overwrite this method")
	#

#


