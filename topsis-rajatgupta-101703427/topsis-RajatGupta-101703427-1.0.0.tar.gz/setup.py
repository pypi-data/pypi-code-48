# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 21:21:02 2020

@author: Rajat Gupta
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="topsis-RajatGupta-101703427", 
    version="1.0.0",
    author="Rajat Gupta",
    author_email="rgupta2_be17@thapar.edu",
    description="A python package to identify the best model out of different models using TOPSIS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    License="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    packages=["Topsis"],
    include_package_data=True,
    install_requires=["requests"],
    entry_points={"console_scripts":["topsis=Topsis.Rajat:main"]},    
)
