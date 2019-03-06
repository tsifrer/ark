import os
import click

from peewee import PostgresqlDatabase

from peewee_migrate import Router

# TODO: update this to work as it should
@click.command()
def migrate():

    database = PostgresqlDatabase(
        database=os.environ.get('POSTGRES_DB_NAME', 'postgres'),
        user=os.environ.get('POSTGRES_DB_USER', 'postgres'),
        host=os.environ.get('POSTGRES_DB_HOST', '127.0.0.1'),
        port=os.environ.get('POSTGRES_DB_PORT', '5432'),
        # password='.password'
    )
    router = Router(database)

    router.run()


if __name__ == '__main__':
    migrate()
