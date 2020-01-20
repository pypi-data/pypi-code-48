

import jk_logging

from .AsyncioLogWrapper import AsyncioLogWrapper




class AsyncioMulticastLogger(AsyncioLogWrapper):

	@staticmethod
	def create(*argv):
		loggers = []
		for l in argv:
			if isinstance(l, AsyncioLogWrapper):
				loggers.append(l._l)
			else:
				assert isinstance(l, jk_logging.AbstractLogger)
				loggers.append(l)
		return AsyncioMulticastLogger(jk_logging.MulticastLogger.create(*loggers))
	#

	def addLogger(self, logger):
		if isinstance(logger, AsyncioLogWrapper):
			logger = logger._l
		assert isinstance(logger, jk_logging.AbstractLogger)
		self._l.addLogger(logger)
	#

	def removeLogger(self, logger):
		if isinstance(logger, AsyncioLogWrapper):
			logger = logger._l
		assert isinstance(logger, jk_logging.AbstractLogger)
		self._l.removeLogger(logger)
	#

	def removeAllLoggers(self):
		self._l.removeAllLoggers()
	#

#







