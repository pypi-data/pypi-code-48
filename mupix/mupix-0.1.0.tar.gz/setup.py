# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mupix']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0',
 'click>=7.0,<8.0',
 'lxml>=4.3,<5.0',
 'matplotlib>=3.1,<4.0',
 'music21>=5.5,<6.0',
 'scipy>=1.3,<2.0']

entry_points = \
{'console_scripts': ['gandalf = gandalf:commands.cli']}

setup_kwargs = {
    'name': 'mupix',
    'version': '0.1.0',
    'description': 'MusicXML Evaluation Tool',
    'long_description': '# GANDALF\n![Travis (.com)](https://img.shields.io/travis/com/deepio/gandalf)\n![GitHub tag (latest by date)](https://img.shields.io/github/tag-date/deepio/gandalf)\n![GitHub last commit](https://img.shields.io/github/last-commit/deepio/gandalf)\n![GitHub repo size](https://img.shields.io/github/repo-size/deepio/gandalf)\n\nThe Symbolic Music File Evaluation Tool.\n- Written with the newer format strings `python 3.6+`.\n- Will not support `python 2.x`.\n- Read the LICENSE.\n\n### Installation\nFrom a bash terminal, run these commands\n```bash\n# Install python poetry\npip3 install --user poetry\n# Create a virtual environment, in this example it is named env\npython3 -m venv env\n# Enter the virtual environment\n. ./env/bin/activate\n# Install gandalf (from the project root)\npoetry install\n```\n\n\n### Usage\n- For up-to-date usage information, run `gandalf` or `gandalf --help`',
    'author': 'Deepio',
    'author_email': 'global2alex@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
