

import jk_logging

from .AsyncioLogWrapper import AsyncioLogWrapper
from .AsyncioBufferLogger import AsyncioBufferLogger
from .AsyncioConsoleLogger import AsyncioConsoleLogger
from .AsyncioFileLogger import AsyncioFileLogger
from .AsyncioFilterLogger import AsyncioFilterLogger
from .AsyncioMulticastLogger import AsyncioMulticastLogger
from .AsyncioNamedMulticastLogger import AsyncioNamedMulticastLogger
from .AsyncioNullLogger import AsyncioNullLogger
from .AsyncioStringListLogger import AsyncioStringListLogger





def instantiate(cfg) -> AsyncioLogWrapper:
	l = jk_logging.instantiate(cfg)

	if isinstance(l, jk_logging.BufferLogger):
		return AsyncioBufferLogger(l)
	elif isinstance(l, jk_logging.ConsoleLogger):
		return AsyncioConsoleLogger(l)
	elif isinstance(l, jk_logging.FileLogger):
		return AsyncioFileLogger(l)
	elif isinstance(l, jk_logging.FilterLogger):
		return AsyncioFilterLogger(l)
	elif isinstance(l, jk_logging.MulticastLogger):
		return AsyncioMulticastLogger(l)
	elif isinstance(l, jk_logging.NamedMulticastLogger):
		return AsyncioNamedMulticastLogger(l)
	elif isinstance(l, jk_logging.NullLogger):
		return AsyncioNullLogger(l)
	elif isinstance(l, jk_logging.StringListLogger):
		return AsyncioStringListLogger(l)
	else:
		return AsyncioLogWrapper(l)
#









