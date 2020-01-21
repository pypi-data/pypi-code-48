from setuptools import find_packages, setup


setup(
    packages=find_packages(),
    name="usc-auto-mechop",
    version="1.0.5",
    author="Michael Leslie",
    author_email="michael.128.leslie@gmail.com",
    description="Grading distribution package for USC's AME 341",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True
)