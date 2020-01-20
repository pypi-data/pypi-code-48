import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
	name="epdnorway",
	version="0.1",
	description="Extract and organize datapoints from Epd Norway DataSet",
    long_description=README,
    long_description_content_type="text/markdown",
	url="https://bitbucket.com/knakk/epdnorway",
	author="Knakk AS",
	author_email="benjamin@knakk.no",
	license="MIT",
    packages=["epdnorway"],
	classifiers=[
		"Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
	],
	install_requires=["xmltodict"],
    python_requires='>=3.7',
	zip_safe=False
)
