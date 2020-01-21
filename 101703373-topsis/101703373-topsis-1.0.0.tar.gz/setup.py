
from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="101703373-topsis",
    version="1.0.0",
    description="A Python package to get optimal solutiion.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Nikhil Vyas",
    author_email="vyasnikhil30@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=["sys","os","pandas","math","numpy"],
    entry_points={
        "console_scripts": [
            "101703373-topsis=topsis.101703373_topsis:main",
        ]
    },
)
