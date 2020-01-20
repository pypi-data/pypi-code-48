# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 16:35:33 2020

@author: DELL
"""

from setuptools import setup
def readme():
     with open('README.md') as f:
        README = f.read()
     return README

setup(
    name="topsis_101753002-Ashish", # Replace with your own username
    version="1.0",
    author="Ashish Garg",
    author_email="ashishgarg5013@gmail.com",
    long_description=readme(),
    long_description_content_type="text/markdown",
    description="It is a self created package for TOPSIS",
    packages=["topsis_main"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['scipy',
                      'tabulate',
                      'numpy',
                      'pandas'
     ],
    entry_points={
        "console_scripts": [
            "topsis=topsis_main.topsis:main",
        ]
    },
)
