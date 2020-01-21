from setuptools import setup, find_packages
from distutils.core import Extension
import os
import re

DISTNAME = 'mhkit'
PACKAGES = find_packages()
EXTENSIONS = []
DESCRIPTION = 'Marine and Hydrokinetic Toolkit'
AUTHOR = 'MHKiT developers'
MAINTAINER_EMAIL = ''
LICENSE = 'Revised BSD'
URL = 'https://github.com/MHKiT-Code-Hub/mhkit-python'
CLASSIFIERS=[]
DEPENDENCIES = ['pandas', 
                'numpy', 
                'scipy',
                'matplotlib', 
                'requests', 
                'pecos>=0.1.8']

# use README file as the long description
file_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(file_dir, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

# get version from __init__.py
with open(os.path.join(file_dir, 'mhkit', '__init__.py')) as f:
    version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        VERSION = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")
        
setup(name=DISTNAME,
      version=VERSION,
      packages=PACKAGES,
      ext_modules=EXTENSIONS,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      maintainer_email=MAINTAINER_EMAIL,
      license=LICENSE,
      url=URL,
      classifiers=CLASSIFIERS,
      zip_safe=False,
      install_requires=DEPENDENCIES,
      scripts=[],
      include_package_data=True
  )
