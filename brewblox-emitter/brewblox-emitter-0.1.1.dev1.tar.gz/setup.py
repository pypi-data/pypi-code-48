from setuptools import find_packages, setup

setup(
    name='brewblox-emitter',
    use_scm_version={'local_scheme': lambda v: ''},
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BrewBlox/brewblox-emitter',
    author='BrewPi',
    author_email='development@brewpi.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: End Users/Desktop',
        'Topic :: System :: Hardware',
    ],
    keywords='brewing brewpi brewblox embedded plugin service',
    packages=find_packages(exclude=['test', 'docker']),
    install_requires=[
        'brewblox-service',
        'aiohttp-sse',
        'schema',
        'pytimeparse',
    ],
    python_requires='>=3.7',
    setup_requires=['setuptools_scm'],
)
