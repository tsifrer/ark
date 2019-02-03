from peewee import PostgresqlDatabase

from playhouse.shortcuts import model_to_dict

from ark.crypto.models.block import Block as CryptoBlock

from .models.block import Block
from .models.transaction import Transaction


# TODO: inherit from interface
class Database(object):

    restored_database_integrity = False

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
        Transaction._meta.database = self.db

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
            raise Exception('Block must be a type of crypto.models.Block')  # TODO: better exception

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

    def verify_blockchain(self):
        """ Verify that the blockchain stored in the db is not corrupted

        This makes simple checks:
        - is last block available
        - is last block height equalt to the number of stored blocks
        - is the number of stored transactions equal to the number of sum of
        Block.number_of_transactions in the database
        - is the sum of all transaction fees equal to the sum of Block.total_fee
        - is the sum of all transaction amounts equal to the sum of Block.total_amount

        Returns a tuple (is_valid, errors)
        """
        errors = []

        last_block = self.get_last_block()

        block_stats = Block.statistics()
        transaction_stats = Transaction.statistics()

        if not last_block:
            errors.append('Last block is not available')
        else:
            if last_block.height != block_stats['blocks_count']:
                errors.append(
                    'Last block height: {}, number of stored blocks: {}'.format(
                        last_block.height, block_stats['blocks_count']
                    )
                )

        # Number of stored transactions must be equal to the sum of
        # Block.number_of_transactions in the database
        if block_stats['transactions_count'] != transaction_stats['transactions_count']:
            errors.append(
                ('Number of transactions: {}, '
                 'number of transactions included in blocks: {}').format(
                    transaction_stats['transactions_count'],
                    block_stats['transactions_count'],
                )
            )

        # Sum of all transaction fees must equal to the sum of Block.total_fee
        if block_stats['total_fee'] != transaction_stats['total_fee']:
            errors.append(
                (
                    'Total transaction fees: {}, '
                    'total transaction fees included in blocks: {}').format(
                    transaction_stats['total_fee'],
                    block_stats['total_fee'],
                )
            )

        # Sum of all transaction amounts must equal to the sum of Block.total_amount
        if block_stats['total_amount'] != transaction_stats['total_amount']:
            errors.append(
                (
                    'Total transaction amounts: {}, '
                    'total transaction amount included in blocks: {}').format(
                    transaction_stats['total_amount'],
                    block_stats['total_amount'],
                )
            )

        is_valid = len(errors) == 0
        return is_valid, errors


























