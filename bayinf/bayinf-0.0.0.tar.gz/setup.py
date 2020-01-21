#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import find_packages, setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bayinf'))
from version import __version__ as version

setup(
    name='bayinf',
    version=version,
    description='Bayesian Inference',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/bayinf/bayinf/',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Science/Research',
    ],
)
