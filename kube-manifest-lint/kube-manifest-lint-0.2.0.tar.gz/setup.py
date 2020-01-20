# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kube_manifest_lint']

package_data = \
{'': ['*'], 'kube_manifest_lint': ['schemas/v1.17.0/*']}

install_requires = \
['PyYAML>=5.3,<6.0', 'jsonschema>=3.2.0,<4.0.0']

entry_points = \
{'console_scripts': ['kube-manifest-lint = kube_manifest_lint:main.main']}

setup_kwargs = {
    'name': 'kube-manifest-lint',
    'version': '0.2.0',
    'description': 'Kubernetes manifest linter using JSON Schema',
    'long_description': '# Kubernetes Manifest Linter\n\n[![Build Status](https://travis-ci.com/hjacobs/kube-manifest-lint.svg?branch=master)](https://travis-ci.com/hjacobs/kube-manifest-lint)\n[![PyPI](https://img.shields.io/pypi/v/kube-manifest-lint)](https://pypi.org/project/kube-manifest-lint/)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kube-manifest-lint)\n![License](https://img.shields.io/github/license/hjacobs/kube-manifest-lint)\n\nValidate Kubernetes YAML manifests against JSON schema.\nIt will use the Kubernetes v1.17 schemas for validation by default.\n\nUsage:\n\n```\npip3 install kube-manifest-lint\nkube-manifest-lint my-deployment.yaml\n```\n\n## Pre Commit Hook\n\nYou can use this tool as a [pre-commit](https://pre-commit.com/) in your git repository. Example `.pre-commit-config.yaml`:\n\n```yaml\nrepos:\n  - repo: https://codeberg.org/hjacobs/kube-manifest-lint\n    rev: "0.2.0"\n    hooks:\n      - id: kube-manifest-lint\n```\n\n## Exit Codes\n\n* 1: file is not a Kubernetes manifests\n* 2: schema for apiVersion/kind was not found\n* 4: schema is deprecated (e.g. using "extensions/v1beta1" instead of "apps/v1")\n* 8: schema validation failed\n',
    'author': 'Henning Jacobs',
    'author_email': 'henning@jacobs1.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://codeberg.org/hjacobs/kube-manifest-lint',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
