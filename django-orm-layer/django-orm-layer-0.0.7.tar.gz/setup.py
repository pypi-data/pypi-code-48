from setuptools import find_packages, setup

setup(
    name='django-orm-layer',
    version='0.0.7',
    python_requires='>=3.6, <4',
    description='django orm layer',
    long_description='use django orm standalone',
    author='Illyasviel',
    url='',
    classifiers=[
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['django>=1.11', 'click>=6.0'],
    entry_points={'console_scripts': 'django-orm = django_orm_layer:main'},
)
