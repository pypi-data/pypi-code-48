import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tanayagarwal", # Replace with your own username
    version="1.0.0",
    author="Tanay Agarwal",
    author_email="tanaygupta1234@gmail.com",
    description="topsis approach for mcdm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=" ",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)