import setuptools 

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="topsis-sirish-ucs633", # Replace with your own username
    version="1.1.1",
    author="Sirish Bhuolia",
    author_email="sirishbhudolia88@gmail.com",
    description="A python package to implement topsis(MCDM)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sirishbhu/topsis",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    packages=["mypackage"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts":[
            "topsis-sirish-ucs633=mypackage.__init__:main",
        ]
    },
)