import setuptools
import importlib

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imdlib",
    version="0.0.3",
    author="Saswata Nandi",
    author_email="iamsaswata@yahoo.com",
    description="A tool for handling IMD gridded data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamsaswata/imdlib",
    packages=setuptools.find_packages(),
    install_requires=['numpy',
                'pandas',
                'six',
                'pandas',
                'python-dateutil',
                'pytz',
                'xarray',],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
) 