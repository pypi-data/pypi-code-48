

import jk_asyncio_syncasync
import jk_logging

from .AsyncioLogWrapper import AsyncioLogWrapper




class AsyncioFileLogger(AsyncioLogWrapper):

	@staticmethod
	def create(filePath, rollOver, bAppendToExistingFile = True, bFlushAfterEveryLogMessage = True, fileMode = None, logMsgFormatter = None):
		return AsyncioFileLogger(jk_logging.FileLogger.create(filePath, rollOver, bAppendToExistingFile, bFlushAfterEveryLogMessage, fileMode, logMsgFormatter))
	#

	async def closed(self) -> bool:
		return await jk_asyncio_syncasync.call_sync(self._l.closed)
	#

	async def isClosed(self) -> bool:
		return await jk_asyncio_syncasync.call_sync(self._l.isClosed)
	#

#







