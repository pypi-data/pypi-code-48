import codecs
import os
import re
import sys

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.M,
    )
    if version_match:
        return version_match.group(1)

    raise RuntimeError("# Unable to find version string.")


str_long_description = read('README.rst')

setup(
    name="colorpage",
    version=find_version("src", "colorpage", "__init__.py"),
    description="One aid used to colorful web page, books, etc.",
    long_description=str_long_description,

    license='MIT',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        #
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research ",
        #
        "License :: OSI Approved :: MIT License",
        #
        "Operating System :: OS Independent",
        #
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        #
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    
    url='https://github.com/colorpage/colorpage/wiki',
    keywords='colorpage rainbow photo webpage',

    author='Kang Shumin',
    author_email='kangshumin@163.com',

    package_dir={"": "src"},
    packages=find_packages(
        where="src",
        exclude=["contrib", "docs", "tests*", "tasks"],
    ),
    
    
    
    package_data={
        'colorpage': ['package_data.dat'],
        "colorpage._vendor.certifi": ["*.pem"],
    },
    data_files=[('my_data', ['data/data_file'])],  # Optional



    #To actually restrict what Python versions a project can be installed on
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',


    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # colorpage# does not have any direct dependencies.
    #install_requires=['peppercorn'],  # Optional

    # to install these using the "extras" syntax, for example:
    #   $ pip install colorpage[dev]
    extras_require={  # Optional
        "watchdog": ["watchdog"],
        "termcolor": ["termcolor"],
        "dev": [
            "pytest",
            "coverage",
            "tox",
            "sphinx",
            "pallets-sphinx-themes",
            "sphinx-issues",
        ],
    },
    
    

    entry_points={
        "console_scripts": [
            "shipwright=colorpage.shipwright:main",
            "shipwright%s=colorpage.shipwright:main" % sys.version_info[:1],
            "shipwright%s.%s=colorpage.shipwright:main" % sys.version_info[:2],
            "colorpage=colorpage:main",
        ],
    },


    zip_safe=False,
)
