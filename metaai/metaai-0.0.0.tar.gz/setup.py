#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import find_packages, setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'metaai'))
from version import __version__ as version

setup(
    name='metaai',
    version=version,
    description='Library of Meta Learning',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://pypi.org/project/metaai',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Science/Research',
    ],
)
