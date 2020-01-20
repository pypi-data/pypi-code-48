# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_google_optimize']

package_data = \
{'': ['*']}

install_requires = \
['pylint-django>=2.0.13,<3.0.0', 'pylint>=2.4.4,<3.0.0']

setup_kwargs = {
    'name': 'django-google-optimize',
    'version': '0.1.7',
    'description': 'Django-google-optimize is a reusable Django application designed to make running server side Google Optimize A/B test easy.',
    'long_description': '# Django-google-optimize\n\n![Lint](https://github.com/adinhodovic/django-google-optimize/workflows/Test/badge.svg)\n![Test](https://github.com/adinhodovic/django-google-optimize/workflows/Lint/badge.svg)\n[![Coverage](https://codecov.io/gh/adinhodovic/django-google-optimize/branch/master/graphs/badge.svg)](https://codecov.io/gh/adinhodovic/django-google-optimize/branch/master)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/django-google-optimize.svg)](https://pypi.org/project/django-google-optimize/)\n[![PyPI Version](https://img.shields.io/pypi/v/django-google-optimize.svg?style=flat)](https://pypi.org/project/django-google-optimize/)\n\nDjango-google-optimize is a reusable Django application designed to make running server side Google Optimize A/B test easy.\n\n## Installation\n\nInstall django-google-optimize with pip:\n\n`pip install django-google-optimize`\n\nAdd the application to installed django applications:\n\n```py\nDJANGO_APPS = [\n    ...\n    "django_google_optimize",\n    ...\n]\n```\n\nAdd the context processor:\n\n```py\n"context_processors": [\n    ...\n    "django_google_optimize.context_processors.google_experiment",\n    ...\n]\n```\n\n## Getting started\n\nAdd settings for the experiments:\n\n- id: Experiment ID required to identify variants for the experiment in templates\n- alias: Alias for the experiment ID, optional useful for clarity in templates when accessing experiment variants by key\n- variant_aliases: Aliases for each variant, each index represents a Optmize Experiment variant\n\n```py\n# django-google-optimize\nGOOGLE_OPTIMIZE_EXPERIMENTS = [\n    {\n        "id": "utSuKi3PRbmxeG08en8VNw",\n        "alias": "redesign",\n        "variant_aliases": {0: "old_design", 1: "new_design"},\n    }\n]\n```\n\nNow you can access the experiment in templates:\n\n```django\n{% if google_optimize.redesign == "new_design" %}\n{% include "jobs/jobposting_list_new.html" %}\n{% else %}\n{% include "jobs/jobposting_list_old.html" %}\n{% endif %}\n```\n\nOr use it inline:\n\n```django\n<nav class="navbar navbar-expand-lg navbar-dark\n{% if google_optimize.redesign == "new_design" %} navbar-redesign{% endif %}">\n```\n\nFull documentation [can be found here.](https://django-google-optimize.readthedocs.io/en/latest/)\n\n## Documentation and Support\n\nMore documentation can be found in the docs directory or read [online](https://django-google-optimize.readthedocs.io/en/latest/). Open a Github issue for support.\n',
    'author': 'Adin Hodovic',
    'author_email': 'hodovicadin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adinhodovic/django-google-optimize',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
