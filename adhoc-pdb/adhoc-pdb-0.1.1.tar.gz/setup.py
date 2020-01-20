# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['adhoc_pdb']

package_data = \
{'': ['*']}

install_requires = \
['remote-pdb>=2.0,<3.0']

setup_kwargs = {
    'name': 'adhoc-pdb',
    'version': '0.1.1',
    'description': 'A simple tool that allows you to debug your system whenever you want, with no overhead, even in production!',
    'long_description': '# adhoc-pdb\n[![Build Status](https://travis-ci.org/yehonatanz/adhoc-pdb.svg?branch=master)](https://travis-ci.org/yehonatanz/adhoc-pdb)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPI version](https://badge.fury.io/py/adhoc-pdb.svg)](https://pypi.org/project/adhoc-pdb/)\n\nA simple tool that allows you to debug your system whenever you want, with no overhead, even in production!\n',
    'author': 'Yehonatan Zecharia',
    'author_email': 'yonti95@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yehonatanz/adhoc-pdb',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
