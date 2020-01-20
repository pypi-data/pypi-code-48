from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="TOPSIS_ANALYSIS_kriti",
    version="1.1.2",
    description="A Python package to evaluate ranks of a Multiple Criteria Decision Making Problem(MCDM) using Technique for Order of Preference by Similarity to Ideal Solution(TOPSIS)",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Kriti Pandey",
    author_email="kritip105@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["TOPO_101703292"],
    include_package_data=True,
    install_requires=["numpy","pandas"],
    entry_points={
        "console_scripts": [
            "TOPO-101703292=TOPO_101703292.3292:main",
        ]
    },
)