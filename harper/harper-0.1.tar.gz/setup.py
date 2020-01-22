from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="harper",
    version="0.1",
    description="Audio and music tools for python",
    license="MIT",
    author="Jim Ulbright",
    url="http://www.github.com/julbright/harper/",
    packages=["harper"],  # same as name
    install_requires=[
        "numpy",
        "seaborn",
        "pyalsaaudio",
    ],  # external packages as dependencies
)
