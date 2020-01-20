import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="intechinvestments",
    version="0.0.3",
    description="Intech Investments Branding materials",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://www.intechinvestments.com/contact",
    author="microprediction",
    author_email="info@3za.org",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["intechinvestments"],
    test_suite='pytest',
    tests_require=['pytest'],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "intechinvestments=intechinvestments.__main__:main",
        ]
     },
     )
