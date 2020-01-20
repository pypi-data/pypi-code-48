#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import os
import setuptools


def get_version_from_init():
    init_file = os.path.join(
        os.path.dirname(__file__), 'cmmnbuild_dep_manager', '__init__.py'
    )
    with open(init_file, 'r') as fd:
        for line in fd:
            if line.startswith('__version__'):
                return ast.literal_eval(line.split('=', 1)[1].strip())

setuptools.setup(
    name='cmmnbuild-dep-manager',
    version=get_version_from_init(),
    description='Manages CERN\'s Java dependencies across multiple Python '
                'packages',
    author='CERN MD Scripting Tools Community',
    author_email='MD-scripting-tools@cern.ch',
    license='MIT',
    url='https://gitlab.cern.ch/scripting-tools/cmmnbuild-dep-manager',
    packages=[
        'cmmnbuild_dep_manager',
        'cmmnbuild_dep_manager.resolver'
    ],
    install_requires=[
        'JPype1>=0.6.1',
        'requests',
        'six'
    ],
    package_data={'cmmnbuild_dep_manager.resolver': ['gradle-wrapper.zip']},
    include_package_data=True,
    zip_safe=False
)
