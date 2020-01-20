import setuptools

try:
    with open("README.md") as a:
        long_description = a.read()
except FileNotFoundError:
    long_description = ""

setuptools.setup(
    name="bootstrap-builder",
    version="0.0.3",
    author="Callum Bartlett",
    author_email="bartlett.c@outlook.com",
    description="A small small package I use to turn some objects into Bootstrap HTML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/4Kaylum/BootstrapHTMLBuilder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
