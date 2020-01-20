import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name="filefield-cache",
    version="0.0.3",
    license='MIT License',
    packages=find_packages(),
    author="Anton Maistrenko",
    include_package_data=True,
    author_email="it2015maistrenko@gmail.com",
    description="Cache Files in Form for files retaining",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/MaistrenkoAnton/",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        'Framework :: Django :: 3.0',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
