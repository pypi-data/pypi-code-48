from .deployer import Deployer
import click


@click.command()
@click.option("--dir", default="./", help="The directory to deploy as a BLD project.")
@click.option(
    "--docker", is_flag=True, default=False, help="Run the SAM build in Docker."
)
def deploy(dir, docker):
    deployer = Deployer(dir, docker=docker)
    deployer.deploy()


if __name__ == "__main__":
    deploy()
