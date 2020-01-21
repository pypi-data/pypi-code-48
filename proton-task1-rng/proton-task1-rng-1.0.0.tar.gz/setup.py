import pathlib
from setuptools import setup

# The directory of this file
HERE = pathlib.Path(__file__).parent

# The README file
README = (HERE / "README.md").read_text()

# The setup
setup(
    name="proton-task1-rng",
    version="1.0.0",
    description="Generate a random number from a discrete distribution",
    long_description=README,
    long_description_content_type="text/markdown",
    #url="https://github.com/realpython/reader",
    author="Cyril van Schreven",
    author_email="cyril.schreven@gmail.com",
    #license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["task1_rng"],
    include_package_data=True,
    #install_requires=["feedparser", "html2text"],
    entry_points={
        "console_scripts": [
            "proton-task1=reader.__main__:main",
        ]
    },
)
