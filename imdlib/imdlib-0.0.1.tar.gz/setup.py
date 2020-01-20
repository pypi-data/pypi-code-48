import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imdlib",
    version="0.0.1",
    author="Saswata Nandi",
    author_email="iamsaswata@yahoo.com",
    description="A tool for handling IMD gridded data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamsaswata/imdlib",
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas==0.25.3',
        'python-dateutil-2.8.1',
        'pytz==2019.3',
        'numpy==1.18.1',
        'six==1.14.0',
        'xarray==0.14.1',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
) 