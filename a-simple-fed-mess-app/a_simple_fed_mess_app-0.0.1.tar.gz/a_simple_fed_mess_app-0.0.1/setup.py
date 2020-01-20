import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="a_simple_fed_mess_app",
    version="0.0.1",
    author="Shadowblade",
    author_email="freemanirabaruta@gmail.com",
    description="A small messaging app with fedora-messaging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juju-e/Simple-fedora-messaging-app/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
