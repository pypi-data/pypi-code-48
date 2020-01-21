"""
Emit logs when imports take to much time
Usefull for debugging
"""

import builtins
import inspect
import logging
import re
import time
from typing import Set

logger = logging.getLogger(__name__)

_import = __import__
visited: Set[str] = set()

SUB_LOG_PREFIX = "├╴"

concealed_module_matchers = [
    r"<frozen importlib\._bootstrap>",
    r"<frozen importlib\._bootstrap_external>",
    r"import_logger[\\\/]import_logger.py$",
    r"lib[\\\/]python[0-9\.]+[\\\/]runpy\.py$",
]


def register(threshold: float) -> None:
    def _logged_import(name, *args, **kwargs):
        if name not in visited:
            visited.add(name)
            start = time.time()
            module = _import(name, *args, **kwargs)
            end = time.time()
            delta = end - start

            if delta >= threshold:
                stack = inspect.stack()
                _, *outer_frames = stack
                log = f"{name} ({round(delta, 3)}s)\n"
                subs = []
                for outer_frame in outer_frames:
                    if any(
                        re.search(module_matcher, outer_frame.filename)
                        for module_matcher in concealed_module_matchers
                    ):
                        continue
                    subs.append(outer_frame.filename)
                for index, sub in enumerate(subs):
                    if index < len(subs) - 1:
                        log += f"├╴{sub}\n"
                    else:
                        log += f"└╴{sub}\n"
                logger.debug(log)
                del outer_frame
                del outer_frames
                del stack

            return module

        return _import(name, *args, **kwargs)

    builtins.__import__ = _logged_import
