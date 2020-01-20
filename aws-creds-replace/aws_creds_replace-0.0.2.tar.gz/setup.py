# aws_creds_replace
from setuptools import find_packages
from setuptools import setup
from pip._internal.req import parse_requirements


# Pulls pip packages with versions from the requirements file
install_requires = parse_requirements("requirements.txt", session="aws_creds_replace")

setup(
    name="aws_creds_replace",
    version="0.0.2",
    author="Traey Hatch",
    author_email="thatch@newmathdata.com",
    url="https://github.com/trejas/aws_creds_replace.git",
    description="",
    long_description="AWS Creds Replace Library",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    setup_requires=[],
    python_requires=">=3.7",
    install_requires=[str(ir.req) for ir in install_requires],
    entry_points={"console_scripts": ["rollcred=aws_creds_replace.main:cli"]},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    dependency_links=[],
    include_package_data=False,
)
