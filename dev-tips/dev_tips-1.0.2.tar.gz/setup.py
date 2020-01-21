import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dev_tips",
    version="1.0.2",
    author="Ígor Yamamoto",
    author_email="hello@igoryamamoto.com",
    description="CLI version of 97 Things Every Programmer Should Know",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/igoryamamoto/dev-tips",
    packages=setuptools.find_packages(),
    package_data={
        "dev_tips": ["*.md"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)