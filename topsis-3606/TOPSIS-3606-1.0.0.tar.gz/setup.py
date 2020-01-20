from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="TOPSIS-3606",
    version="1.0.0",
    description="A Python package for TOPSIS analysis of a Multiple Criteria Decision Making Problem.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    #url="https://github.com/nikhilkumarsingh/weather-reporter",
    author="Varinda Rani",
    author_email="varindavg@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["Top_3606"],
    include_package_data=True,
    install_requires=["pandas","numpy"],
    entry_points={
        "console_scripts": [
            "Top-3606 = Top_3606.topsis3606:main",
        ]
    },
)