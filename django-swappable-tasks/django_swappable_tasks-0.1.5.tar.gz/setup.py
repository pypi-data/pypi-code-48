from distutils.core import setup

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name='django_swappable_tasks',  # How you named your package folder (MyLib)
    packages=['django_swappable_tasks',],  # Chose the same as "name"
    version='0.1.5',  # Start with a small number and increase it with every change you make
    license='gpl-3.0',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Switch between asynchronous task handlers in your django without in seconds.',
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    # Give a short description about your library
    author='Jerry Shikanga',  # Type in your name
    author_email='jerryshikanga@gmail.com',  # Type in your E-Mail
    url='https://github.com/jerryshikanga/django_swappable_tasks',
    # Provide either the link to your github or to your website
    download_url='https://github.com/jerryshikanga/django_swappable_tasks/archive/v0.1.5.tar.gz',  # I explain this later on
    keywords=['Django', 'Tasks', 'Asynchronous', 'Handlers', 'Swap', 'Google Cloud Tasks'],
    # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'google-cloud-tasks',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
