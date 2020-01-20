# -*- coding: utf-8 -*-
"""Version utility"""
import logging

from hdx.utilities.path import script_dir_plus_file

logger = logging.getLogger(__name__)


def get_geonode_version():
    version_file = open(script_dir_plus_file('version.txt', get_geonode_version))
    return version_file.read().strip()
