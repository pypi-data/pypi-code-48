# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['keios_dynabuffers_sol', 'keios_dynabuffers_sol.optical_character_recognition']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'keios-dynabuffers-sol',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'fridayy',
    'author_email': 'benjamin.krenn@leftshift.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
