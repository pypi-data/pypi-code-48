import setuptools

with open('ReadMe.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="NGDataPortal", 
    version="0.0.1",
    author="Ayrton Bourn",
    author_email="AyrtonBourn@Outlook.com",
    description="Package for accessing the NG ESO data portal API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AyrtonB/National-Grid-Data-Portal",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)