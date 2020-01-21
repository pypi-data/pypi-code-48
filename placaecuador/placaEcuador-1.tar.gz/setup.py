import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="placaEcuador", # Replace with your own username
    version="1",
    author="Alexandro Tapia",
    author_email="alexandrotapiaflores@gmail.com",
    description="A package with a tool to check if you can be on the  road of Quito - Ecuador",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexandro591/Pico-Placa",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)