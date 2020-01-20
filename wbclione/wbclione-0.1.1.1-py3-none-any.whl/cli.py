import click

import requests

from click.utils import LazyFile
from click.exceptions import BadParameter, ClickException, Abort

class RunGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        # TODO: check if cmd_name is a file in the current dir and not require `run`?
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        return None


@click.command(cls=RunGroup, invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """WBclione.

    Run "wbclione docs" for full documentation.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@cli.command(help="Login to WBclione")
@click.argument("key", nargs=-1)
def login(key):
    
    key = key[0] if len(key) > 0 else None

    if key:
        # util.set_api_key(api, key)
        url = 'http://localhost:3000/users/1'
        headers = {
          "Authorization": "Token token=7IrIz5lmeKNUK7ZDNGrGWwtt",
          "Content-Type": "application/json; charset=utf-8"
        }
        r = requests.get(url, headers=headers)
        if r.status_code == requests.codes.ok:
          click.echo("this worked")
    else:
        click.echo("No key specified")
        
    if key:
        click.secho("Successfully logged in to WBClione!", fg="green")

    return key

@cli.command(help="List projects")
def projects(display=True):
    projects = [{"name":"Hello"}, {"name":"World"}]
    if len(projects) == 0:
        message = "No projects found"
    else:
        message = 'Latest projects'
    if display:
        click.echo(click.style(message, bold=True))
        for project in projects:
            click.echo(click.style(project['name'], fg="blue", bold=True))
    return projects