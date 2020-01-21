import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="randomframe",
    version="0.3",
    author="Jonathan de Jong",
    author_email="jonathan@automatia.nl",
    description="Random Frame backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.automatia.nl/ShadowJonathan/randomframe",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "flask", "base58"],
    setup_requires=["wheel"],
    extras_require={"dev": ["ipython", "twine", "bump2version", "black"]},
)
