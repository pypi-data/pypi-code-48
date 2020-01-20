################################################################################
################################################################################
###
###  This file is automatically generated. Do not change this file! Changes
###  will get overwritten! Change the source file for "setup.py" instead.
###  This is either 'packageinfo.json' or 'packageinfo.jsonc'
###
################################################################################
################################################################################


from setuptools import setup

def readme():
	with open("README.md", "r", encoding="UTF-8-sig") as f:
		return f.read()

setup(
	author = "Jürgen Knauth",
	author_email = "pubsrc@binary-overflow.de",
	classifiers = [
		"Development Status :: 4 - Beta",
		"License :: OSI Approved :: Apache Software License",
	],
	description = "This python module provides basic classes for tokenizing and parsing.",
	download_url = "https://github.com/jkpubsrc/python-module-jk-tokenizingparsing/tarball/0.2020.1.20",
	include_package_data = False,
	install_requires = [
	],
	keywords = [
		"tokenizing",
		"parsing",
	],
	license = "Apache 2.0",
	name = "jk_tokenizingparsing",
	packages = [
		"jk_tokenizingparsing",
		"jk_tokenizingparsing.tokenmatching",
	],
	url = "https://github.com/jkpubsrc/python-module-jk-tokenizingparsing",
	version = "0.2020.1.20",
	zip_safe = False,
	long_description = readme(),
	long_description_content_type="text/markdown",
)
