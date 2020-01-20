import setuptools
import importlib

with open("README.md", "r") as fh:
    long_description = fh.read()



def check_dependencies(package_names):
    """Check if packages can be imported, if not throw a message."""
    not_met = []
    for n in package_names:
        try:
            _ = importlib.import_module(n)
        except ImportError:
            not_met.append(n)
    if len(not_met) != 0:
        errmsg = "Warning: the following packages could not be found: "
        print(errmsg + ', '.join(not_met))


req_packages = ['numpy',
                'pandas',
                'six',
                'pandas',
                'python-dateutil',
                'pytz',
                'xarray',
                ]

check_dependencies(req_packages)

setuptools.setup(
    name="imdlib",
    version="0.0.2",
    author="Saswata Nandi",
    author_email="iamsaswata@yahoo.com",
    description="A tool for handling IMD gridded data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamsaswata/imdlib",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
) 