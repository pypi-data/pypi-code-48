# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['netizenship']
install_requires = \
['beautifulsoup4>=4.8.2,<5.0.0',
 'pyfiglet>=0.8.post1,<0.9',
 'requests>=2.22.0,<3.0.0',
 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['netizenship = netizenship:main']}

setup_kwargs = {
    'name': 'netizenship',
    'version': '0.2.2',
    'description': 'Tool to check the username with popular websites for membership',
    'long_description': '# Netizenship![license](https://img.shields.io/github/license/rahulrajpl/netizenship) \n\n![tweet](https://img.shields.io/twitter/url?url=https%3A%2F%2Fgithub.com%2Frahulrajpl%2Fnetizenship)\n![stars](https://img.shields.io/github/stars/rahulrajpl/netizenship?style=social)\n![forks](https://img.shields.io/github/forks/rahulrajpl/netizenship?style=social)\n\n\nThis is a commandline tool to find the online presence of a username in popular social media websites like Facebook, Instagram, Twitter, etc.\n\n![sneakpeak](./sneak.gif)\n\n## Installation\n\nInstall this tool via following command\n\n~~~\nsudo pip3 install netizenship\n~~~\n\n## Usage\n\nOnce the tool is installed, run it by executing the command \n\n~~~\nnetizenship\n~~~\n\n\nand then enter the username to search for\n\n## Contribute\n\nThis tool is presently at infant stage. I highly appreciate improvements and suggestions.\n\n## License\n\nMIT License \n\nCopyright (c) 2020 Rahul Raj\n\nRead full license [here](./LICENSE)\n',
    'author': 'Rahul Raj',
    'author_email': 'rahulrajpl@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rahulrajpl/netizenship',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
