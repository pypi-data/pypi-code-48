import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="101703301-Project1-TOPSIS", # Replace with your own username
    version="0.0.2",
    author="Kushagra-Thakral",
    author_email="kushagra.thakral@gmail.com",
    description="Implementation of TOPSIS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
