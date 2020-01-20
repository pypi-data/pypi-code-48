# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymedphys',
 'pymedphys._app',
 'pymedphys._base',
 'pymedphys._bundle',
 'pymedphys._data',
 'pymedphys._dev',
 'pymedphys._dicom',
 'pymedphys._dicom.constants',
 'pymedphys._dicom.ct',
 'pymedphys._dicom.delivery',
 'pymedphys._dicom.rtplan',
 'pymedphys._dicom.utilities',
 'pymedphys._electronfactors',
 'pymedphys._gamma',
 'pymedphys._gamma.api',
 'pymedphys._gamma.implementation',
 'pymedphys._gamma.utilities',
 'pymedphys._icom',
 'pymedphys._imports',
 'pymedphys._losslessjpeg',
 'pymedphys._mocks',
 'pymedphys._mosaiq',
 'pymedphys._mudensity',
 'pymedphys._mudensity.delivery',
 'pymedphys._mudensity.plt',
 'pymedphys._trf',
 'pymedphys._utilities',
 'pymedphys._utilities.algorithms',
 'pymedphys._utilities.constants',
 'pymedphys._utilities.filehash',
 'pymedphys._utilities.transforms',
 'pymedphys._vendor.apipkg',
 'pymedphys._vendor.pylinac',
 'pymedphys._vendor.pylinac.core',
 'pymedphys._vendor.tensorflow',
 'pymedphys._wlutz',
 'pymedphys.cli',
 'pymedphys.cli.labs',
 'pymedphys.labs',
 'pymedphys.labs.fileformats',
 'pymedphys.labs.fileformats.mapcheck',
 'pymedphys.labs.fileformats.mephysto',
 'pymedphys.labs.fileformats.profiler',
 'pymedphys.labs.film',
 'pymedphys.labs.managelogfiles',
 'pymedphys.labs.paulking',
 'pymedphys.labs.pedromartinez',
 'pymedphys.labs.pedromartinez.oncentra',
 'pymedphys.labs.pedromartinez.utils',
 'pymedphys.labs.pinnacle',
 'pymedphys.labs.serviceplans',
 'pymedphys.labs.tpscompare']

package_data = \
{'': ['*'],
 'pymedphys': ['_jupyterlab/*', '_jupyterlab/templates/*', '_monaco/*'],
 'pymedphys._app': ['templates/*', 'working_directory/*'],
 'pymedphys._bundle': ['src/main/*', 'src/renderer/*'],
 'pymedphys.labs': ['serviceplans/templates/*']}

install_requires = \
['Pillow',
 'PyYAML',
 'attrs',
 'cython',
 'dbfread',
 'imageio',
 'keyring',
 'matplotlib',
 'numpy>=1.12,<2.0',
 'packaging',
 'pandas',
 'pydicom',
 'pymssql<3.0.0',
 'pynetdicom',
 'python_dateutil',
 'requests',
 'scikit-image',
 'scipy',
 'tqdm',
 'watchdog']

extras_require = \
{':python_version >= "3.6.0" and python_version < "3.7.0"': ['dataclasses'],
 'difficult': ['shapely'],
 'docs': ['sphinx>=1.4,<1.8',
          'sphinx-rtd-theme>=0.4.3,<0.5.0',
          'sphinx-autobuild',
          'sphinxcontrib-napoleon',
          'sphinx-argparse',
          'nbsphinx',
          'jupyter_client',
          'ipython',
          'ipykernel',
          'm2r'],
 'gui': ['jupyterlab_server'],
 'jupyter': ['jupyterlab'],
 'jupyter:sys_platform == "win32"': ['pywin32==224'],
 'ml': ['tensorflow==2.1.0-rc2', 'absl-py'],
 'pylint': ['pylint', 'pytest-pylint'],
 'pytest': ['pytest', 'pytest-sugar', 'hypothesis']}

entry_points = \
{'console_scripts': ['pymedphys = pymedphys.cli.main:pymedphys_cli']}

setup_kwargs = {
    'name': 'pymedphys',
    'version': '0.20.0',
    'description': 'Medical Physics library',
    'long_description': "|logo|\n\n.. |logo| image:: https://github.com/pymedphys/pymedphys/raw/master/docs/logos/pymedphys_title.png\n    :target: https://docs.pymedphys.com/\n\n.. START_OF_DOCS_IMPORT\n\n**A community effort to develop an open standard library for Medical Physics\nin Python. Building quality transparent software together via peer review\nand open source distribution. Open code is better science.**\n\n|build| |pypi| |python| |license|\n\n.. |build| image:: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fpymedphys%2Fpymedphys%2Fbadge&label=build&logo=none\n    :target: https://actions-badge.atrox.dev/pymedphys/pymedphys/goto\n\n.. |pypi| image:: https://img.shields.io/pypi/v/pymedphys\n    :target: https://pypi.org/project/pymedphys/\n\n.. |python| image:: https://img.shields.io/pypi/pyversions/pymedphys\n    :target: https://pypi.org/project/pymedphys/\n\n.. |license| image:: https://img.shields.io/pypi/l/pymedphys\n    :target: https://choosealicense.com/licenses/apache-2.0/\n\n\nDocs under construction\n-----------------------\n\nThis documentation is currently undergoing a major revamp. At this point in\ntime many of the below links will take you to empty pages. If you are able to\nhelp, drop me a line at `me@simonbiggs.net`_.\n\n.. _`me@simonbiggs.net`: mailto:me@simonbiggs.net\n\n\nFirst steps\n-----------\n\nAre you new to PyMedPhys or new to Python programming? Then these resources are\nfor you:\n\n* From scratch: `New to Python`_ | `Installation`_\n* Tutorials: `Part 1: Stretching a DICOM CT`_ |\n  `Part 2: Calculating fluence from DICOM plan`_\n\nHow the documentation is organised\n----------------------------------\n\nHere is a high level overview of how the documentation is organised to help\nyou to know where to look for things:\n\n* `Tutorials`_ take you by the hand through a series of steps to create a tool\n  built with PyMedPhys for use within a Medical Physics clinic. Start here if\n  you're new to PyMedPhys or Python programming.\n* `How-To guides`_ are recipes. They guide you through the steps involved in\n  addressing key problems and use-cases. They are more advanced than tutorials\n  and assume some knowledge of how to build tools with PyMedPhys.\n* `Reference Documents`_ is the technical reference for the public APIs exposed\n  by both the ``pymedphys`` library and the ``pymedphys`` command line tool.\n* `Explanatory documents`_ provide the higher level descriptions of the\n  implementation of the tools and provides justifications for development\n  decisions.\n\nThe above layout has been heavily inspired by both the `Django documentation`_\nand `Daniele Procida's writeup`_.\n\n.. figure:: https://github.com/pymedphys/pymedphys/raw/master/docs/img/docs-structure.png\n\n    A slide from `Daniele Procida's writeup`_ describing the documentation\n    layout.\n\n.. _`Daniele Procida's writeup`: https://www.divio.com/blog/documentation/\n.. _`Django documentation`: https://docs.djangoproject.com\n\nBeyond the user documentation there are two other sections, the\n`contributor documentation`_ aimed at those who wish to become a PyMedPhys\ncontributor, and the `labs documentation`_ which details code contributed by\nthe community that aims to one day be refined to become part of the primary\n``pymedphys`` library.\n\nWhat is PyMedPhys?\n------------------\n\nA place to share, review, improve, and transparently learn off of each\nother’s code. It is an open-source library of tools that we all have access\nto. It is inspired by the collaborative work of our physics peers in astronomy\nand their `Astropy Project`_. PyMedPhys is available on `PyPI`_, `GitHub`_ and\n`conda-forge`_.\n\n.. _`Astropy Project`: http://www.astropy.org/\n.. _`PyPI`: https://pypi.org/project/pymedphys/\n.. _`GitHub`: https://github.com/pymedphys/pymedphys\n.. _`conda-forge`: https://anaconda.org/conda-forge/pymedphys\n\nPyMedPhys is currently within the ``beta`` stage of its life-cycle. It will\nstay in this stage until the version number leaves ``0.x.x`` and enters\n``1.x.x``. While PyMedPhys is in ``beta`` stage, **no API is guaranteed to be\nstable from one release to the next.** In fact, it is very likely that the\nentire API will change multiple times before a ``1.0.0`` release. In practice,\nthis means that upgrading ``pymedphys`` to a new version will possibly break\nany code that was using the old version of pymedphys. We try to be abreast of\nthis by providing details of any breaking changes from one release to the next\nwithin the `Release Notes`_.\n\nOur Team\n--------\n\nPyMedPhys is what it is today due to its contributors.\nCore contributors and contributors who have been active in the last six months\nas well as their respective employers are presented below.\n\nCore contributors\n.................\n\n* `Simon Biggs`_\n    * `Riverina Cancer Care Centre`_, Australia\n\n.. _`Simon Biggs`: https://github.com/SimonBiggs\n\n\n* `Matthew Jennings`_\n    * `Royal Adelaide Hospital`_, Australia\n\n.. _`Matthew Jennings`: https://github.com/Matthew-Jennings\n\nActive contributors\n...................\n\n* `Jake Rembish`_\n    * `UT Health San Antonio`_, USA\n\n.. _`Jake Rembish`: https://github.com/rembishj\n\n* `Phillip Chlap`_\n    * `University of New South Wales`_, Australia\n    * `South Western Sydney Local Health District`_, Australia\n\n.. _`Phillip Chlap`: https://github.com/pchlap\n\n* `Pedro Martinez`_\n    * `University of Calgary`_, Canada\n    * `Tom Baker Cancer Centre`_, Canada\n\n.. _`Pedro Martinez`: https://github.com/peterg1t\n\n* `Jacob McAloney`_\n    * `Riverina Cancer Care Centre`_, Australia\n\n.. _`Jacob McAloney`: https://github.com/JacobMcAloney\n\n\n|rccc| |rah| |uth| |uoc|\n\nPast contributors\n.................\n\n* `Matthew Sobolewski <https://github.com/msobolewski>`_\n* `Paul King <https://github.com/kingrpaul>`_\n\n\n.. |rccc| image:: https://github.com/pymedphys/pymedphys/raw/master/docs/logos/rccc_200x200.png\n    :target: `Riverina Cancer Care Centre`_\n\n.. |rah| image:: https://github.com/pymedphys/pymedphys/raw/master/docs/logos/gosa_200x200.png\n    :target: `Royal Adelaide Hospital`_\n\n.. |jarmc| image:: https://github.com/pymedphys/pymedphys/raw/master/docs/logos/jarmc_200x200.png\n    :target: `Anderson Regional Cancer Center`_\n\n.. |nbcc| image:: https://github.com/pymedphys/pymedphys/raw/master/docs/logos/nbcc_200x200.png\n    :target: `Northern Beaches Cancer Care`_\n\n.. |uoc| image:: https://github.com/pymedphys/pymedphys/raw/master/docs/logos/uoc_200x200.png\n    :target: `University of Calgary`_\n\n.. |uth| image:: https://github.com/pymedphys/pymedphys/raw/master/docs/logos/UTHSA_logo.png\n    :target: `UT Health San Antonio`_\n\n.. _`Riverina Cancer Care Centre`: http://www.riverinacancercare.com.au/\n\n.. _`Royal Adelaide Hospital`: http://www.rah.sa.gov.au/\n\n.. _`University of New South Wales`: https://www.unsw.edu.au/\n\n.. _`South Western Sydney Local Health District`: https://www.swslhd.health.nsw.gov.au/\n\n.. _`Anderson Regional Cancer Center`: http://www.andersonregional.org/CancerCenter.aspx\n\n.. _`Northern Beaches Cancer Care`: http://www.northernbeachescancercare.com.au/\n\n.. _`University of Calgary`: http://www.ucalgary.ca/\n\n.. _`Tom Baker Cancer Centre`: https://www.ahs.ca/tbcc\n\n.. _`UT Health San Antonio`: https://www.uthscsa.edu/academics/biomedical-sciences/programs/radiological-sciences-phd\n\n\n.. END_OF_DOCS_IMPORT\n\n\n.. _`New to Python`: https://docs.pymedphys.com/tutes/python\n.. _`Installation`: https://docs.pymedphys.com/tutes/install\n.. _`Part 1: Stretching a DICOM CT`: https://docs.pymedphys.com/tutes/part-1\n.. _`Part 2: Calculating fluence from DICOM plan`: https://docs.pymedphys.com/tutes/part-2\n\n\n.. _`Tutorials`: https://docs.pymedphys.com/tutes\n.. _`How-To guides`: https://docs.pymedphys.com/howto\n.. _`Reference Documents`: https://docs.pymedphys.com/ref\n.. _`Explanatory documents`: https://docs.pymedphys.com/explain\n\n.. _`contributor documentation`: https://docs.pymedphys.com/contrib\n.. _`labs documentation`: https://docs.pymedphys.com/labs\n\n.. _`Release Notes`: http://docs.pymedphys.com/getting-started/changelog.html\n",
    'author': 'PyMedPhys Contributors',
    'author_email': 'developers@pymedphys.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pymedphys.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
