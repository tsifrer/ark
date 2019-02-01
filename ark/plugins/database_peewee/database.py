from peewee import PostgresqlDatabase

from .models.block import Block

# TODO: inherit from interface
class Database(object):
    def __init__(self):
        super().__init__()
        # self.loop = loop

    def connect(self):
        self.db = PostgresqlDatabase(
            database='postgres',
            user='postgres',
            host='127.0.0.1',
            port='5432',
            # password='password'
        )

        # database.set_allow_sync(False)
        Block._meta.database = self.db

    def get_last_block(self):
        """Get the last block
        Returns None if block can't be found.
        """
        try:
            return Block.select().order_by(Block.height.desc()).get()
        except Block.DoesNotExist:
            return None
