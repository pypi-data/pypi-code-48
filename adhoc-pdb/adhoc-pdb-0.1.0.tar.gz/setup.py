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
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Yehonatan Zecharia',
    'author_email': 'yonti95@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
