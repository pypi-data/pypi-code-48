from setuptools import setup, find_packages


setup(
    name="namestudio",
    version="1.0",
    author="Michael Whalen",
    author_email="michael@whalesalad.com",
    url="https://github.com/whalesalad/verisign-namestudio",
    packages=find_packages(),
    install_requires=[
        "requests==2.22.0",
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "pytest==5.3.4",
    ],
    python_requires='>=3.7',
)
