

import jk_asyncio_syncasync
import jk_logging

from .AsyncioLogWrapper import AsyncioLogWrapper




class AsyncioStringListLogger(AsyncioLogWrapper):

	@staticmethod
	def create(logMsgFormatter = None):
		return AsyncioStringListLogger(jk_logging.StringListLogger.create(logMsgFormatter))
	#

	async def hasData(self):
		await jk_asyncio_syncasync.call_sync(self._l.hasData())
	#

	async def toList(self):
		await jk_asyncio_syncasync.call_sync(self._l.toList())
	#

#







