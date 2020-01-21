import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="worldguess", # Replace with your own username
    version="0.0.1",
    author="FerdX",
    author_email="ferdinand.bhavsar@epita.fr",
    description="World Guess is a package to identify subject countries in documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pumafi/worldguess",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['pandas'],
)
