import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="topsis-ppruthi-101883058", 
    version="1.0.0",
    author="Pritpal Singh Pruthi",
    author_email="ppruthi_be17@thapar.edu",
    description="A python package to identify the best model out of different mobile phones using TOPSIS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    License="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    packages=["topsis_python"],
    include_package_data=True,
    install_requires=["requests"],
    entry_points={"console_scripts":["topsis=topsis_python.topsis:main"]},    
)
