from peewee_async import PostgresqlDatabase, Manager

from .models.block import Block

# TODO: inherit from interface
class Database(object):

    def __init__(self, loop):
        super().__init__()
        self.loop = loop

    def connect(self):
        database = PostgresqlDatabase(
            database='postgres',
            user='postgres',
            host='127.0.0.1',
            port='5432',
            # password='password'
        )

        database.set_allow_sync(False)
        Block._meta.database = database
        self.objects = Manager(database=database, loop=self.loop)
        return self.objects

    async def get_last_block(self):
        return await self.objects.count(Block.select())
