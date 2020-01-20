import re
import ast
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [
        ('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import coverage
        import pytest

        if self.pytest_args and len(self.pytest_args) > 0:
            self.test_args.extend(self.pytest_args.strip().split(' '))
            self.test_args.append('tests/')

        cov = coverage.Coverage()
        cov.start()
        errno = pytest.main(self.test_args)
        cov.stop()
        cov.report()
        cov.html_report()
        print("Wrote coverage report to htmlcov directory")
        sys.exit(errno)


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('rho_ml/__init__.py', 'rb') as f:
    __version__ = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='rho-ml',
    version=__version__,
    description="Standard framework for wrapping ML and other algorithms",
    long_description=open('README.md', 'r').read(),
    maintainer="Rho AI Corporation",
    license="Commercial",
    url="https://bitbucket.org/rhoai/rho-ml",
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        'attrs',
        'marshmallow'
    ],
    extras_require={
        'dev': [
            'honcho'
        ],
        'test': [
            'pytest',
            'tox',
            'coverage',
            'hypothesis'
        ]
    },
    cmdclass={'test': PyTest}
)
