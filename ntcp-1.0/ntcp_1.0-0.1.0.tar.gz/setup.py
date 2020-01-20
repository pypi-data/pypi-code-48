from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="ntcp_1.0",
    version="0.1.0",
    description="A Python package to calculate EUD based NTCP.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ThirumuruganE/ntcp",
    author="Thirumurugan Elango",
    author_email="thiru20@protonmail.com",
    license="GPLv3+",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["ntcp"],
    package_data={'home/thirumurugan/Documents/eud_ntcp/ntcp':["icon.gif","readme.png"]},
    include_package_data=True,
    install_requires=["numpy","Cython","pandas","xlrd","matplotlib","PrettyTable"],
    entry_points={
        "console_scripts": [
            "ntcp=ntcp.ntcp:main",
        ]
    },
)
