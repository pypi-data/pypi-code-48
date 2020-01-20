import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="parteek_topsis",
    version="0.0.1",
    author="prateek_satija",
    author_email="psatija_be17@thapar.edu",
    description="A small example package",
    long_description=long_description,
    packages=setuptools.find_packages(),
)
