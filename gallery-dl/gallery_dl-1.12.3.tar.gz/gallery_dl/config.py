# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Global configuration module"""

import sys
import json
import os.path
import logging
from . import util

log = logging.getLogger("config")


# --------------------------------------------------------------------
# internals

_config = {}

if os.name == "nt":
    _default_configs = [
        r"%USERPROFILE%\gallery-dl\config.json",
        r"%USERPROFILE%\gallery-dl.conf",
    ]
else:
    _default_configs = [
        "/etc/gallery-dl.conf",
        "${HOME}/.config/gallery-dl/config.json",
        "${HOME}/.gallery-dl.conf",
    ]


# --------------------------------------------------------------------
# public interface

def load(files=None, strict=False, fmt="json"):
    """Load JSON configuration files"""
    if fmt == "yaml":
        try:
            import yaml
            parsefunc = yaml.safe_load
        except ImportError:
            log.error("Could not import 'yaml' module")
            return
    else:
        parsefunc = json.load

    for path in files or _default_configs:
        path = util.expand_path(path)
        try:
            with open(path, encoding="utf-8") as file:
                confdict = parsefunc(file)
        except OSError as exc:
            if strict:
                log.error(exc)
                sys.exit(1)
        except Exception as exc:
            log.warning("Could not parse '%s': %s", path, exc)
            if strict:
                sys.exit(2)
        else:
            if not _config:
                _config.update(confdict)
            else:
                util.combine_dict(_config, confdict)


def clear():
    """Reset configuration to an empty state"""
    _config.clear()


def get(path, key, default=None, *, conf=_config):
    """Get the value of property 'key' or a default value"""
    try:
        for p in path:
            conf = conf[p]
        return conf[key]
    except Exception:
        return default


def interpolate(path, key, default=None, *, conf=_config):
    """Interpolate the value of 'key'"""
    if key in conf:
        return conf[key]
    try:
        for p in path:
            conf = conf[p]
            if key in conf:
                default = conf[key]
    except Exception:
        pass
    return default


def set(path, key, value, *, conf=_config):
    """Set the value of property 'key' for this session"""
    for p in path:
        try:
            conf = conf[p]
        except KeyError:
            conf[p] = conf = {}
    conf[key] = value


def setdefault(path, key, value, *, conf=_config):
    """Set the value of property 'key' if it doesn't exist"""
    for p in path:
        try:
            conf = conf[p]
        except KeyError:
            conf[p] = conf = {}
    return conf.setdefault(key, value)


def unset(path, key, *, conf=_config):
    """Unset the value of property 'key'"""
    try:
        for p in path:
            conf = conf[p]
        del conf[key]
    except Exception:
        pass


class apply():
    """Context Manager: apply a collection of key-value pairs"""
    _sentinel = object()

    def __init__(self, kvlist):
        self.original = []
        self.kvlist = kvlist

    def __enter__(self):
        for path, key, value in self.kvlist:
            self.original.append((path, key, get(path, key, self._sentinel)))
            set(path, key, value)

    def __exit__(self, etype, value, traceback):
        for path, key, value in self.original:
            if value is self._sentinel:
                unset(path, key)
            else:
                set(path, key, value)
