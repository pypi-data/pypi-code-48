from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="python_topsis",
    version="1.0.1",
    description="TOPSIS Algorithm in Python(UCS633).",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Ayushgupta03",
    author="Ayush Gupta",
    author_email="guptayush0022@gmail.com",
    packages=["python_topsis"],
    include_package_data=True,
    install_requires=["requests"],
    
)