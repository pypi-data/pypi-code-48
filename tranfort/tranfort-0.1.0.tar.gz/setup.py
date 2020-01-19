# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tranfort']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.1.2,<4.0.0',
 'numpy>=1.18.1,<2.0.0',
 'pandas>=0.25.3,<0.26.0',
 'scikit-learn>=0.22.1,<0.23.0',
 'torch>=1.4.0,<2.0.0',
 'transformers>=2.3.0,<3.0.0']

setup_kwargs = {
    'name': 'tranfort',
    'version': '0.1.0',
    'description': 'Transformer for Tabular Data Learning',
    'long_description': None,
    'author': 'yajiez',
    'author_email': 'yajiez.me@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
