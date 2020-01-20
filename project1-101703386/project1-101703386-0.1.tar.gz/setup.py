# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 19:22:16 2020

@author: PARUL BANSAL
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="project1-101703386", # Replace with your own username
    version="0.1",
    author="Parul Bansal",
    author_email="pbansal1_be17@thapar.edu",
    description="TOPSIS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
