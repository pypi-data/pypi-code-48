# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 16:06:07 2020

@author: Kunal Jindal
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="topsis-kjindal-101703299", 
    version="1.0.0",
    author="Kunal Jindal",
    author_email="kjindal_be17@thapar.edu",
    description="A python package to identify the best model out of various mobile phone models using TOPSIS",
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
    packages=["topsis_python"],
    include_package_data=True,
    install_requires=["requests"],
    entry_points={"console_scripts":["topsis=topsis_python.topsis:main"]},    
)