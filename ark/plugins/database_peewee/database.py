from peewee import PostgresqlDatabase

from playhouse.shortcuts import model_to_dict

from ark.crypto.models.block import Block as CryptoBlock

from .models.block import Block
from .models.transaction import Transaction


# TODO: inherit from interface
class Database(object):

    restoredDatabaseIntegrity = False

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
            block = Block.select().order_by(Block.height.desc()).get()
        except Block.DoesNotExist:
            return None
        else:
            return CryptoBlock(model_to_dict(block))

    def save_block(self, block):
        if not isinstance(block, CryptoBlock):
            raise Exception(
                'Block must be a type of crypto.models.Block'
            )  # TODO: better exception

        with self.db.atomic() as db_txn:
            try:
                db_block = Block.from_crypto(block)
                # db_block.save()

                for transaction in block.transactions:
                    db_transaction = Transaction.from_crypto(transaction)
                    # db_transaction.save()
            except Exception as e:  # TODO: Make this not so broad!
                print('Got an exception yo')
                db_txn.rollback()
                print(e)  # TODO: replace with logger.error

        print(db_block)
        print(db_transaction)
