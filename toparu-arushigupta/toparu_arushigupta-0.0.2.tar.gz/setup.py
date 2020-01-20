# from distutils.core import setup
import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="toparu_arushigupta", # Replace with your own username
    version="0.0.2",
    author="Arushi Gupta",
    author_email="agupta11_be17@thapar.edu",
    description="A small package that showcases topsis approach",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/user/reponame/archive/v_01.tar.gz',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)