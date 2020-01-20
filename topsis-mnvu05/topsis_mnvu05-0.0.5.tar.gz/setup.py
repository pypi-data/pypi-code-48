import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="topsis_mnvu05", # Replace with your own username
    version="0.0.5",
    author="Manav Upadhyay",
    author_email="manavupadhyay5@gmail.com",
    description="TOPSIS Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mnvu/topsis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)