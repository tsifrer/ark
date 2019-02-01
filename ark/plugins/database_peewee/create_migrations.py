import click

from peewee import PostgresqlDatabase

from peewee_migrate import Router

# TODO: update this to work as it should
@click.command()
@click.option(
    '--name', prompt='Migration name', help='Name of the migration after timestamp.'
)
def create_migrations(name):

    database = PostgresqlDatabase(
        database='postgres',
        user='postgres',
        host='127.0.0.1',
        port='5432',
        # password='.password'
    )
    router = Router(database)

    # Create migration
    router.create(name, auto='models')


if __name__ == '__main__':
    create_migrations()
