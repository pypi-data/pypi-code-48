#!/usr/bin/env python
#-*- coding:utf-8 -*-


from setuptools import setup, find_packages

setup(
    name = "PLC_IDE",
    version = "0.0.1",
    keywords = ("pip", "pathtool","timetool", "magetool", "mage"),
    description = "PLC PRG EDITOR tool",
    long_description = "PLC PRG EDITOR tool",
    license = "MIT Licence",

    # url = "https://github.com/fengmm521/pipProject",
    author = "ren1987yi",
    author_email = "ren1987yi@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)
