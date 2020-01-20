"""Setup inaccel package."""

from __future__ import absolute_import

import setuptools

setuptools.setup(
    name = 'inaccel-vitis',
    packages = setuptools.find_namespace_packages(include=["inaccel.*"]),
    namespace_packages=['inaccel'],
    version = '0.1',
    license = 'Apache-2.0',
    description = 'InAccel Vitis Libraries',
    author = 'InAccel',
    author_email='info@inaccel.com',
    url = 'https://docs.inaccel.com',
    keywords = ['InAccel', 'Vitis', 'Coral', 'FPGA'],
    install_requires = [
        'coral-api',
		'opencv-python'
    ],
    zip_safe = True,
    include_package_data = False,
    classifiers = [
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.4',
)
