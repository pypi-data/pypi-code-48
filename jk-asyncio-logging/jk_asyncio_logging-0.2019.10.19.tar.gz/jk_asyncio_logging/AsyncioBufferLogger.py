

import jk_asyncio_syncasync
import jk_logging

from .AsyncioLogWrapper import AsyncioLogWrapper




class AsyncioBufferLogger(AsyncioLogWrapper):

	@staticmethod
	def create(jsonRawData = None):
		return AsyncioBufferLogger(jk_logging.BufferLogger.create(jsonRawData = None))
	#

	async def hasData(self) -> bool:
		return await jk_asyncio_syncasync.call_sync(self._l.hasData)
	#

	async def forwardTo(self, logger, bClear:bool = False):
		ldest = logger._l if isinstance(logger, AsyncioLogWrapper) else logger
		assert isinstance(ldest, jk_logging.AbstractLogger)

		await jk_asyncio_syncasync.call_sync(self._l.forwardTo, ldest, bClear)
	#

	async def forwardToDescended(self, logger, text:str, bClear:bool = False):
		ldest = logger._l if isinstance(logger, AsyncioLogWrapper) else logger
		assert isinstance(ldest, jk_logging.AbstractLogger)

		await jk_asyncio_syncasync.call_sync(self._l.forwardToDescended, ldest, text, bClear)
	#

	async def getDataAsJSON(self) -> list:
		return await jk_asyncio_syncasync.call_sync(self._l.getDataAsJSON)
	#

	async def getDataAsPrettyJSON(self) -> list:
		return await jk_asyncio_syncasync.call_sync(self._l.getDataAsPrettyJSON)
	#

#







