# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:25:44 2020

@author: Rakshit
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis3431", 
    version="1.0.0",
    author="Rakshit Rajesh Jain",
    author_email="rakshitj.1899@gmail.com",
    description="TOPSIS package for MCDM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=['Topsis3431'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)