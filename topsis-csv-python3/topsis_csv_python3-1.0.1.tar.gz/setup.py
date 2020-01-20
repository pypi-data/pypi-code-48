import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="topsis_csv_python3", 
    version="1.0.1",
    author="Prateek Kr Singh",
    author_email="prateekkumarsingh3@gmail.com",
    description="Implementation of Topsis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NoOne03/topsis.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
