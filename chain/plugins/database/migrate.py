import click

from peewee import PostgresqlDatabase

from peewee_migrate import Router

# TODO: update this to work as it should
@click.command()
def migrate():

    database = PostgresqlDatabase(
        database='postgres',
        user='postgres',
        host='127.0.0.1',
        port='5432',
        # password='.password'
    )
    router = Router(database)

    router.run()


if __name__ == '__main__':
    migrate()
