import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis_Arsh", # Replace with your own username
    version="0.0.2",
    author="ARSHPREET SINGH",
    author_email="arshpreet15.99@gmail.com",
    description="Topsis package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BhullarArsh/Topsis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)