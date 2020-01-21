#!/usr/bin/env python
# coding: utf-8

# In[ ]:

"""Setup for the ScrobblIES package."""

import setuptools

setuptools.setup(
    author="Petr Pham & Matěj Kovář",    
    name='ScrobblIES',
    license='unlicense',
    description='Offers a set of tools for scraping from Last.fm',
    version='v0.0.1',    
    url='https://github.com/petrpham/ScrobblIES',
    packages=setuptools.find_packages()    
)