# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dd2nx']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.3,<20.0',
 'dd>=0.5.4,<0.6.0',
 'funcy>=1.13,<2.0',
 'networkx>=2.4,<3.0']

setup_kwargs = {
    'name': 'dd2nx',
    'version': '0.1.2',
    'description': "Python library for converting the dd package's BDD to Multigraph in networkx.",
    'long_description': "# dd2nx\nPython library for converting the dd package's BDD to Multigraph in networkx.\n",
    'author': 'Marcell Vazquez-Chanlatte',
    'author_email': 'mvc@linux.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mvcisback/dd2nx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
