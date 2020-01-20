import os
from support.version import (
    major_version, minor_version, main_version
)
from support.classifiers import classifiers

from setuptools import setup

import support
support.use("system")
from support.setup_codes import setup_commands

name = 'amuse-phantom'
micro_version = 3
patch_version = ""
version = "%i.%i.%i%s" % (major_version, minor_version, micro_version,
                           patch_version)
author = 'The AMUSE team'
author_email = 'info@amusecode.org'
license_ = "Apache License 2.0"
url = 'http://www.amusecode.org/'
install_requires = [
    'wheel>=0.32',
    'docutils>=0.6',
    'numpy>=1.2.2',
    'nose>=0.11.1',
    'mpi4py>=1.1.0',
    'h5py>=1.1.0',
    'amuse-framework>=%s' % (main_version),
]
description = 'The Astrophysical Multipurpose Software Environment - Phantom'
with open("README.md", "r") as fh:
    long_description = fh.read()
long_description_content_type = "text/markdown"
os.environ["DOWNLOAD_ONLY"] = "1"

extensions = []

all_data_files = []

packages = ['amuse.community.phantom']

package_data = {
}

mapping_from_command_name_to_command_class = setup_commands()

setup(
    name=name,
    version=version,
    classifiers=classifiers,
    url=url,
    author_email=author_email,
    author=author,
    license=license_,
    description=description,
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    install_requires=install_requires,
    cmdclass=mapping_from_command_name_to_command_class,
    ext_modules=extensions,
    package_dir={'amuse.community.phantom': 'src/amuse/community/phantom'},
    packages=packages,
    package_data=package_data,
    data_files=all_data_files,
)
