import os

from peewee_migrate import Router

from chain.common.plugins import load_plugin


def migrate():
    database = load_plugin('chain.plugins.database')

    migrate_dir = os.path.join(
        os.getcwd(), 'chain', 'plugins', 'database', 'migrations'
    )
    router = Router(database.db, migrate_dir=migrate_dir)

    router.run()


if __name__ == '__main__':
    migrate()
