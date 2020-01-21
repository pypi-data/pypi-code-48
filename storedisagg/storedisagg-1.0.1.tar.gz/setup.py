import fnmatch
from setuptools import find_packages, setup
from setuptools.command.build_py import build_py as build_py_orig

with open("description_pypi.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="storedisagg",
    version="1.0.1",
    author="storedisagg contributors listed in AUTHORS",
    author_email="m.c.soini@posteo.de",
    description=("Ex-post disaggregation of storage operation by time scales"),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/mcsoini/storedisagg",
    packages=find_packages(),
    install_requires=['scipy', 'pandas', 'matplotlib', 'wrapt', 'tqdm'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"],
)
