# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clearcache', 'clearcache.management', 'clearcache.management.commands']

package_data = \
{'': ['*'], 'clearcache': ['templates/admin/*', 'templates/clearcache/admin/*']}

install_requires = \
['django>=2.2,<3.0']

setup_kwargs = {
    'name': 'django-clearcache',
    'version': '1.0',
    'description': 'Allows you to clear Django cache via admin UI or manage.py command',
    'long_description': None,
    'author': 'Tim Kamanin',
    'author_email': 'tim@timonweb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://timonweb.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
