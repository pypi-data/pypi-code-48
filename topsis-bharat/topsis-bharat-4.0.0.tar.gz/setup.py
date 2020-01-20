from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="topsis-bharat",
    version="4.0.0",
    description="A TOPSIS Python package.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="",
    author="Bharat Chauhan",
    author_email="bharatchauhan752000@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis_bharat132"],
    include_package_data=True,
    install_requires=["pandas"],
    entry_points={
        "console_scripts": [
            "topsis-bharat=topsis_bharat132.package_101703139:main",
        ]
    },
)