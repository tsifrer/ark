import os
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
        database=os.environ.get('POSTGRES_DB_NAME', 'postgres'),
        user=os.environ.get('POSTGRES_DB_USER', 'postgres'),
        host=os.environ.get('POSTGRES_DB_HOST', '127.0.0.1'),
        port=os.environ.get('POSTGRES_DB_PORT', '5432'),
        # password='.password'
    )
    router = Router(database)

    # Create migration
    router.create(name, auto='models')


if __name__ == '__main__':
    create_migrations()
