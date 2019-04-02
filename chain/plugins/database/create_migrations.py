import click

from peewee_migrate import Router

from chain.common.plugins import load_plugin


# TODO: update this to work as it should
@click.command()
@click.option(
    "--name", prompt="Migration name", help="Name of the migration after timestamp."
)
def create_migrations(name):

    database = load_plugin("chain.plugins.database")
    router = Router(database.db)

    # Create migration
    router.create(name, auto="models")


if __name__ == "__main__":
    create_migrations()
