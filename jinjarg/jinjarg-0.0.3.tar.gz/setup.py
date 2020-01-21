# coding: utf-8
from setuptools import setup
import os

"""CLI-template renderer like m4 but based on jinja and argparse"""


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='jinjarg',
    version='0.0.3',
    url='https://github.com/strizhechenko/jinjarg',
    license='MIT',
    author='Oleg Strizhechenko',
    author_email='oleg.strizhechenko@gmail.com',
    description="CLI-template renderer like m4 but based on jinja and argparse",
    long_description=(read('README.md')),
    py_modules=['jinjarg'],
    platforms='any',
    install_requires=['jinja2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
