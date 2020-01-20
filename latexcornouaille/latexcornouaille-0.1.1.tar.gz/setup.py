# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['latexcornouaille']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['latexcornouaille = latexcornouaille.cli:main']}

setup_kwargs = {
    'name': 'latexcornouaille',
    'version': '0.1.1',
    'description': 'custom python package for latex',
    'long_description': None,
    'author': 'David Couronné',
    'author_email': 'couronne.david@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
