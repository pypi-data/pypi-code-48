# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['android_arsenal_notifier']

package_data = \
{'': ['*']}

install_requires = \
['py-terminal-notifier==0.1.0', 'requests>2.2-', 'selectolax>0.2.0']

entry_points = \
{'console_scripts': ['android-arsenal = '
                     'android_arsenal_notifier.android_arsenal:main']}

setup_kwargs = {
    'name': 'android-arsenal-notifier',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'flomk',
    'author_email': 'sudogitrekt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
