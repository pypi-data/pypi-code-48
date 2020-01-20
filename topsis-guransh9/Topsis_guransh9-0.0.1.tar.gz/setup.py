import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis_guransh9", # Replace with your own username
    version="0.0.1",
    author="Jyot Guransh Singh Dua",
    author_email="dua.guransh18@gmail.com",
    description="A python package to implement Topsis approach",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/Topsis",
    packages=["Topsis_pack"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    install_requires=["requests"],
    entry_points={"console_scripts":["topsis=Topsis_pack.topsis.main",]},
)# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

