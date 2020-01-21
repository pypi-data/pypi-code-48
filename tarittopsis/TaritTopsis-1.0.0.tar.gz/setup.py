import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TaritTopsis", 
    version="1.0.0",
    author="Tarit Kandpal",
    author_email="taritkandpal@gmail.com",
    description="TOPSIS for MCDM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/taritkandpal/TOPSIS-for-MCDM",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)