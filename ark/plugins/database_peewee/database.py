import math
from hashlib import sha256

from peewee import PostgresqlDatabase

from ark.crypto.models.block import Block as CryptoBlock

from .models.block import Block
from .models.round import Round
from .models.transaction import Transaction
from .wallet_manager import WalletManager


# TODO: inherit from interface
class Database(object):

    restored_database_integrity = False
    forging_delegates = []

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.db = PostgresqlDatabase(
            database='postgres',
            user='postgres',
            host='127.0.0.1',
            port='5432',
            # password='password'
        )

        # database.set_allow_sync(False)
        # TODO: figure this out
        Block._meta.database = self.db
        Transaction._meta.database = self.db
        Round._meta.database = self.db

        self.wallets = WalletManager(self.db)


    def get_last_block(self):
        """Get the last block
        Returns None if block can't be found.
        """
        try:
            block = Block.select().order_by(Block.height.desc()).get()
        except Block.DoesNotExist:
            return None
        else:
            return CryptoBlock(block)

    def save_block(self, block):
        if not isinstance(block, CryptoBlock):
            raise Exception(
                'Block must be a type of crypto.models.Block'
            )  # TODO: better exception

        with self.db.atomic() as db_txn:
            try:
                db_block = Block.from_crypto(block)
                db_block.save(force_insert=True)
            except Exception as e:  # TODO: Make this not so broad!
                print('Got an exception while saving a block')
                db_txn.rollback()
                print(e)  # TODO: replace with logger.error
                return

        with self.db.atomic() as db_txn:
            try:
                for transaction in block.transactions:
                    db_transaction = Transaction.from_crypto(transaction)
                    db_transaction.save(force_insert=True)
            except Exception as e:  # TODO: Make this not so broad!
                print('Got an exception while saving transactions')
                db_txn.rollback()
                db_block.delete_instance()
                print(e)  # TODO: replace with logger.error
                return


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
                (
                    'Number of transactions: {}, '
                    'number of transactions included in blocks: {}'
                ).format(
                    transaction_stats['transactions_count'],
                    block_stats['transactions_count'],
                )
            )

        # Sum of all transaction fees must equal to the sum of Block.total_fee
        if block_stats['total_fee'] != transaction_stats['total_fee']:
            errors.append(
                (
                    'Total transaction fees: {}, '
                    'total transaction fees included in blocks: {}'
                ).format(transaction_stats['total_fee'], block_stats['total_fee'])
            )

        # Sum of all transaction amounts must equal to the sum of Block.total_amount
        if block_stats['total_amount'] != transaction_stats['total_amount']:
            errors.append(
                (
                    'Total transaction amounts: {}, '
                    'total transaction amount included in blocks: {}'
                ).format(transaction_stats['total_amount'], block_stats['total_amount'])
            )

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_active_delegates(self, height, delegates=None):
        """Get the top 51 delegates

        TODO: this function is potentially very broken and returns all rounds?
        """
        max_delegates = self.app.config.get_milestone(height)['activeDelegates']
        delegate_round = math.floor((height - 1) / max_delegates) + 1

        if (
            len(self.forging_delegates) > 0
            and self.forging_delegates[0].round == delegate_round
        ):
            return self.forging_delegates

        if not delegates or len(delegates) == 0:
            # TODO: Does this return only the first 51 delegates???
            delegates = (
                Round.select()
                .where(Round.round == delegate_round)
                .order_by(Round.balance.desc(), Round.public_key.asc())
            )

        seed = sha256(str(delegate_round).encode('utf-8')).digest()
        # TODO: Look into why we don't reorder every 5th element (the second index += 1
        # skips it). Also why do we create another seed, that is always the same after
        # the first run?
        index = 0
        while index < len(delegates):
            for x in range(min(4, len(delegates) - index)):
                new_index = seed[x] % len(delegates)
                # Swap delegate on index with the delegate on new_index
                delegates[new_index], delegates[index] = (
                    delegates[index],
                    delegates[new_index],
                )
                index += 1
            index += 1
            seed = sha256(seed).digest()

        self.forging_delegates = delegates
        return self.forging_delegates

    def get_recent_block_ids(self):
        """Get 10 most recent block ids
        """
        blocks = (
            Block
            .select(Block.id)
            .order_by(Block.timestamp.desc())
            .limit(10)
            .tuples()
        )
        return [x[0] for x in blocks]

    def get_block_by_id(self, block_id):
        try:
            block = Block.get(Block.id == block_id)
        except Block.DoesNotExist:
            return None
        else:
            return CryptoBlock(block)

    def get_forged_transaction_ids(self, transaction_ids):
        transactions = (
            Transaction
            .select(Transaction.id)
            .where(Transaction.id.in_(transaction_ids))
        )
        return [transaction.id for transaction in transactions]
