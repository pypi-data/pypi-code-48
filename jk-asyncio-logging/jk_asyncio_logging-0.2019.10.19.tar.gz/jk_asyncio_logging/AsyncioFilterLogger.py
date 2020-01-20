


import jk_logging

from .AsyncioLogWrapper import AsyncioLogWrapper




class AsyncioFilterLogger(AsyncioLogWrapper):

	@staticmethod
	def create(logger:jk_logging.AbstractLogger, minLogLevel:jk_logging.EnumLogLevel = jk_logging.EnumLogLevel.WARNING):
		return AsyncioFilterLogger(jk_logging.FilterLogger.create(logger, minLogLevel))
	#

#







