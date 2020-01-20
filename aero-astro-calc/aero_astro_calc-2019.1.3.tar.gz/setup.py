import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aero_astro_calc",
    version="2019.1.3",
    author="Anson Biggs",
    author_email="anson@ansonbiggs.com",
    description="A small python library with functions to assist engineers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/MisterBiggs/aero-astro-calc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # python_requires=">=3.6",
)
