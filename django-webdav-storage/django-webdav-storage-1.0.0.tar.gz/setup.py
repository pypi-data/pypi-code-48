# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_webdav_storage',
 'django_webdav_storage.management',
 'django_webdav_storage.management.commands']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'django-webdav-storage',
    'version': '1.0.0',
    'description': 'A Django storage backend allowing you to easily save user-generated and static files into your own WebDAV storage rather than a local filesystem, as Django does by default.',
    'long_description': 'django-webdav-storage\n=====================\n\n.. image:: https://badge.fury.io/py/django-webdav-storage.svg\n    :target: https://badge.fury.io/py/django-webdav-storage\n\n.. image:: https://img.shields.io/pypi/l/django-webdav-storage\n    :target: https://raw.githubusercontent.com/marazmiki/django-webdav-storage/master/LICENSE\n    :alt: The project license\n\n.. image:: https://travis-ci.org/marazmiki/django-webdav-storage.svg?branch=master\n    :target: https://travis-ci.org/marazmiki/django-webdav-storage\n    :alt: Travis CI build status\n\n.. image:: https://coveralls.io/repos/marazmiki/django-webdav-storage/badge.svg?branch=master\n    :target: https://coveralls.io/r/marazmiki/django-webdav-storage?branch=master\n    :alt: Code coverage percentage\n\n.. image:: https://pypip.in/wheel/django-webdav-storage/badge.svg\n     :target: https://pypi.python.org/pypi/django-webdav-storage/\n     :alt: Wheel Status\n\n.. image:: https://img.shields.io/pypi/pyversions/django-webdav-storage.svg\n     :target: https://img.shields.io/pypi/pyversions/django-webdav-storage.svg\n     :alt: Supported Python versions\n\n.. image:: https://img.shields.io/pypi/djversions/django-webdav-storage.svg\n     :target: https://pypi.org/project/django-webdav-storage/\n     :alt: Supported Django versions\n\n.. image:: https://readthedocs.org/projects/django-webdav-storage/badge/?version=latest\n     :target: https://django-ulogin.readthedocs.io/ru/latest/?badge=latest\n     :alt: Documentation Status\n\n.. image:: https://api.codacy.com/project/badge/Grade/8eb2817e37cf4c2e98edc3dcbf886e6d\n   :alt: Codacy Badge\n   :target: https://app.codacy.com/manual/marazmiki/django-webdav-storage?utm_source=github.com&utm_medium=referral&utm_content=marazmiki/django-webdav-storage&utm_campaign=Badge_Grade_Dashboard\n\n\nDescription\n-----------\n\nThis application allows you easily save media and static files into webdav storage.\n\nDocumentation\n-------------\nPlease see full documentation at `Read the Docs <http://django-webdav-storage.readthedocs.io/en/latest/>`_\n\n',
    'author': 'Mikhail Porokhovnichenko',
    'author_email': 'marazmiki@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/marazmiki/django-webdav-storage',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7,<4',
}


setup(**setup_kwargs)
