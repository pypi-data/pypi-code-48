import os
import subprocess
from setuptools import setup
from distutils.command.upload import upload as _upload
from os import path


def get_version():
    with open(path.join(path.dirname(__file__), 'version.txt')) as f:
        return f.read().strip()


__version__ = get_version()
__git_tag__ = 'v' + __version__


def get_requirements():
    with open(path.join(path.dirname(__file__), 'requirements.txt')) as f:
        return [l for l in f.read().strip().split('\n')
                if not l.startswith('-')]


def list_git_tags():
    print('Pulling git tags...')
    p = subprocess.Popen(['git', 'pull', '--tags'])
    if p.wait() != 0:
        raise Exception('Error pulling git tags.')
    print('Listing git tags...')
    p = subprocess.Popen(['git', 'tag'], stdout=subprocess.PIPE)
    out, _ = p.communicate()
    if p.returncode != 0:
        raise Exception('Error getting git tags.')
    return out.decode('utf-8').strip().split(os.linesep)


def check_git_tag():
    return __git_tag__ in list_git_tags()


def update_git_tag():
    print(f'Checking if git tag {__git_tag__} exists...')
    if check_git_tag():
        raise Exception('Git tag already exists. Please increment the version '
                        'and try again.')
    print(f'Creating git tag {__git_tag__}...')
    p = subprocess.Popen(['git', 'tag', __git_tag__])
    if p.wait() != 0:
        raise Exception('Error creating git tag.')
    print(f'Pushing git tag {__git_tag__}...')
    p = subprocess.Popen(['git', 'push', '--tags'])
    if p.wait() != 0:
        raise Exception('Error pushing git tag.')


def deploy():

    class upload(_upload):
        def run(self):
            super(upload, self).run()
            self.execute(update_git_tag, 'Updating git tag')

    setup(
        name='cf_api',
        version=__version__,
        description='Python Interface for Cloud Foundry APIs',
        long_description=open('README.md').read(),
        long_description_content_type="text/markdown",
        license='Apache License Version 2.0',
        author='Adam Jaso',
        author_email='ajaso@hsdp.io',
        packages=['cf_api'],
        package_dir={
            'cf_api': 'cf_api',
        },
        install_requires=get_requirements(),
        url='https://github.com/hsdp/python-cf-api',
        cmdclass={'upload': upload},
    )


if __name__ == '__main__':
    deploy()
