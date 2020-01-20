import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis_Arpit", # Replace with your own username
    version="0.0.1",
    author="Arpit Singla",
    author_email="arpitsingla1999@gmail.com",
    download_url="https://github.com/ArpitSingla/TOPSIS-Python/archive/0.01.tar.gz",
    description="A small package that showcases Topsis approach",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArpitSingla/TOPSIS-Python.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)