# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hashversion']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'gitpython>=3.0.5,<4.0.0', 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['hashver = hashversion.cli:cli']}

setup_kwargs = {
    'name': 'hashversion',
    'version': '0.2.1',
    'description': 'Automate versioning and related requirements when using hashver',
    'long_description': '# Hash Version\n\n![PyPI](https://img.shields.io/pypi/v/hashversion)\n![License](https://img.shields.io/github/license/miniscruff/hashversion-python.svg)\n![Issues](https://img.shields.io/github/issues/miniscruff/hashversion-python.svg)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![codecov](https://codecov.io/gh/miniscruff/hashversion-python/branch/master/graph/badge.svg)](https://codecov.io/gh/miniscruff/hashversion-python)\n\nPython CLI for automating hash versioning and related requirements.\nTo help automate versioning, changelog management and other pieces of continuous\ndeployments.\n\n## Documentation\nComing soon to a read the docs near you.\n\n## Bugs\nThis project is getting upgrades in my free time if there is a problem please create a bug report in the issues section.\n',
    'author': 'Ronnie Smith',
    'author_email': 'halfpint1170@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/miniscruff/hashversion-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
