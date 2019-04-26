import click

from chain.common.plugins import load_plugin


@click.command()
@click.option("--round", prompt="Round", help="Round number you want to rollback to")
def rollback_to_round(round):
    database = load_plugin("chain.plugins.database")
    database.rollback_to_round(int(round))


if __name__ == "__main__":
    rollback_to_round()
