# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mdh']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.0', 'numpy>=1.9', 'scipy>=1.0']

setup_kwargs = {
    'name': 'mdh',
    'version': '0.1.0',
    'description': 'modified dh',
    'long_description': '# Modified DH\n\n\n\n## Inspiration\n\nYou should probably use one of these, they inspired me to write a simpler\nmodule for my needs:\n\n- [pybotics](https://github.com/nnadeau/pybotics)\n- [pytransform3d](https://github.com/rock-learning/pytransform3d)\n',
    'author': 'walchko',
    'author_email': 'walchko@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/MomsFriendlyRobotCompany/mdh',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
