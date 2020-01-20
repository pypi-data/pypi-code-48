


import jk_logging

from .AsyncioLogWrapper import AsyncioLogWrapper




class AsyncioConsoleLogger(AsyncioLogWrapper):

	@staticmethod
	def create(printToStdErr = False, logMsgFormatter = None, printFunction = None):
		return AsyncioConsoleLogger(jk_logging.ConsoleLogger.create(printToStdErr, logMsgFormatter, printFunction))
	#

#







