

import jk_logging

from .AsyncioLogWrapper import AsyncioLogWrapper




class AsyncioNullLogger(AsyncioLogWrapper):

	@staticmethod
	def create():
		return AsyncioNullLogger(jk_logging.NullLogger.create())
	#

#







