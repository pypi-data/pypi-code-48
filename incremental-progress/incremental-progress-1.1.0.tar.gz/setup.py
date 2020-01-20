import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    author="TAOS DevopsNow",
    name="incremental-progress",
    author_email="devopsnow@taos.com",
    description="Teaching tool for recording development steps",
    # license=open("LICENSE").read(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(
        exclude=["contrib", "docs", "tests", "htmlcov", "example"]),
    version="1.1.0",
    url="https://github.com/taosdevops/incremental-progress",
    install_requires=["watchgod==0.5"],
    entry_points="""
        [console_scripts]
        incremental=cli:main
        """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Your supported Python ranges
)
