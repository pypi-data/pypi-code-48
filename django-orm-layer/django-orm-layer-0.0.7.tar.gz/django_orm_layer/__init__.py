import os
import subprocess
from pathlib import Path

import click
import shutil

from .utils import add_app

ROOT_PATH = Path(__file__).absolute().parent
PWD = os.getcwd()


@click.group()
def cli():
    pass


@cli.command()
def create():
    shutil.copytree(ROOT_PATH.joinpath('orm'), Path(PWD).joinpath('orm'))


@cli.command()
@click.argument('app_name', nargs=1)
@click.argument('template', nargs=1)
def addapp(app_name, template):
    ormpath = Path(PWD).joinpath('orm')
    templatepath = ROOT_PATH.joinpath('templates')
    destfile = ormpath.joinpath('settings.py')
    add_app(app_name, str(destfile))
    template_name = 'template_1' if template == '1' else 'template_2'
    shutil.copytree(templatepath.joinpath(template_name), ormpath.joinpath(app_name))


@cli.command()
def makemigrations():
    subprocess.run('python3 -m orm.manage makemigrations'.split())


@cli.command()
def migrate():
    subprocess.run('python3 -m orm.manage migrate'.split())


def main():
    cli()


if __name__ == '__main__':
    main()
