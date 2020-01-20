import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="topsis-101703382", 
    version="0.0.2",
    author="Paras Arora",
    author_email="parora_be17@thapar.edu",
    description="Automatic topsis for decision making",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Paras1598/Topsis",
    py_modules=["topsis-101703382","run"],
    packages=setuptools.find_packages(),
    
    keywords = ['command-line', 'topsis-python', 'TOPSIS'],  
    install_requires=[            
          'numpy',
          'pandas',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=["bin/topsis-101703382_cli"],
    python_requires='>=3.6',
)
