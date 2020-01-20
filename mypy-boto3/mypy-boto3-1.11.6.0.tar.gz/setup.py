from os.path import abspath, dirname

from setuptools import setup


LONG_DESCRIPTION = open(dirname(abspath(__file__)) + "/README.md", "r").read()


setup(
    name="mypy-boto3",
    version="1.11.6.0",
    packages=["mypy_boto3",],
    url="https://github.com/vemel/mypy_boto3",
    license="MIT License",
    author="Vlad Emelianov",
    author_email="vlad.emelianov.nz@gmail.com",
    description="Type annotations for boto3 1.11.6 master module.",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Typing :: Typed",
    ],
    keywords="boto3 type-annotations boto3-stubs mypy mypy-stubs typeshed autocomplete auto-generated",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    project_urls={
        "Documentation": "https://mypy-boto3.readthedocs.io/en/latest/",
        "Source": "https://github.com/vemel/mypy_boto3",
        "Tracker": "https://github.com/vemel/mypy_boto3/issues",
    },
    install_requires=["boto3", "typing_extensions; python_version < '3.8'",],
    package_data={"mypy_boto3": ["py.typed"]},
    zip_safe=False,
    entry_points={"console_scripts": ["mypy_boto3 = mypy_boto3.main:main"]},
)
