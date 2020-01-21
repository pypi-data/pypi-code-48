from setuptools import find_packages, setup
from baseapi import __version__

setup(
    name='base-api',
    version=__version__,
    author='Luke Hodkinson',
    author_email='furious.luke@gmail.com',
    maintainer='Luke Hodkinson',
    maintainer_email='furious.luke@gmail.com',
    description='Easily create maintainable API clients.',
    long_description='',
    url='https://github.com/furious-luke/baseapi',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License'
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    package_data={'': ['*.txt', '*.js', '*.html', '*.*']},
    install_requires=[
        'requests'
    ],
    extras_require={
    },
    entry_points={
    },
    zip_safe=True
)
