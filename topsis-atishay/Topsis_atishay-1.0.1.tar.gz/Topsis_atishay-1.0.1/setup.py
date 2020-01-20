
import setuptools
with open("README.md", "r") as fh:
    README = fh.read()

setuptools.setup(
    name="Topsis_atishay", # Replace with your own username
    version="1.0.1",
    author="Atishay",
    author_email="Atishay21@gmail.com",
    description="A Python package to implement topsis function",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages()
)