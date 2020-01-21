#!/usr/bin/env python
from setuptools import setup

setup(
    version="0.0.5",
    install_requires=[
        'pytest<5;python_version<"3.5"',
        'pytest;python_version>="3.4"',
        "pytest-bdd",
    ],
    tests_require=["mock"],
    python_requires=">=2.7",
    py_modules=["pytest_bdd_wrappers"],
    entry_points={
        "pytest11": [
            "pytest_bdd_wrappers = pytest_bdd_wrappers",
        ]
    },
)
