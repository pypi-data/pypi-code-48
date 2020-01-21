# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['import_logger']
setup_kwargs = {
    'name': 'import-logger',
    'version': '1.0.0',
    'description': 'Emit logs when imports take to much time',
    'long_description': None,
    'author': 'Iddan Aaronsohn',
    'author_email': 'mail@aniddan.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
