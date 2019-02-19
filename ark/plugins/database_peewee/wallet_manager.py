from peewee import fn

from ark.config import Config
from ark.crypto.address import address_from_public_key
from ark.crypto.constants import (
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_TRANSFER,
    TRANSACTION_TYPE_VOTE,
)
from ark.crypto.models.transaction import Transaction as CryptoTransaction

from .models.block import Block
from .models.transaction import Transaction


# Wallets are stored in memory, as they're rebuilt every time you startup the relay
# so for now there's no valid need to store them in DB.
class Wallet(object):
    # TODO: improve this
    def __init__(self, data):
        fields = [
            ('address', None),
            ('public_key', None),
            ('second_public_key', None),
            ('multisignature', None),
            ('vote', None),
            ('username', None),
            ('balance', 0),
            ('vote_balance', 0),
            ('produced_blocks', 0),
            ('missed_blocks', 0),
            ('forged_fees', 0),
            ('forged_rewards', 0),
        ]
        for field, default in fields:
            setattr(self, field, data.get(field, default))


# TODO: Extensive tests
class WalletManager(object):

    def __init__(self, database):
        super().__init__()
        self.db = database

        # TODO: Terrible names
        self._wallets = {}
        self._public_key_map = {}
        # self._by_public_key = {}
        # self._by_username = {}

        config = Config()
        self._genesis_addresses = set()
        for transaction in config['genesis_block']['transactions']:
            self._genesis_addresses.add(transaction['senderId'])

    def _build_received_transactions(self):
        """Load and apply received transactions to wallets.
        """
        transactions = (
            Transaction
            .select(
                Transaction.recipient_id,
                fn.SUM(Transaction.amount).alias('amount')
            )
            .where(Transaction.type == TRANSACTION_TYPE_TRANSFER)
            .group_by(Transaction.recipient_id)
        )

        for transaction in transactions:
            # TODO: make this nicer. It feels like a hack to do it this way
            wallet = self.find_by_address(transaction.recipient_id)
            wallet.balance = int(transaction.amount)

    def _build_block_rewards(self):
        """Load and apply block rewards to wallets.
        """
        blocks = (
            Block
            .select(
                Block.generator_public_key,
                fn.SUM(Block.reward + Block.total_fee).alias('reward')
            )
            .group_by(Block.generator_public_key)
        )

        for block in blocks:
            wallet = self.find_by_public_key(block.generator_public_key)
            wallet.balance += int(block.reward)

    # def _build_last_forged_blocks(self):
    #     """Load and apply last forged blocks to wallets.
    #     """
    #     last_block_query = (
    #         Block
    #         .select(fn.MAX(Block.height).alias('last_block_height'))
    #         .group_by(Block.generator_public_key)
    #     )
    #     blocks = (
    #         Block
    #         .select(
    #             Block.id,
    #             Block.height,
    #             Block.generator_public_key,
    #             Block.timestamp,
    #         )
    #         .where(Block.height.in_(last_block_query))
    #         .order_by(Block.timestamp.desc())
    #     )

    #     for block in blocks:
    #         wallet = self.find_by_public_key(block.generator_public_key)
    #         wallet.last_block = block

    def _build_sent_transactions(self):
        transactions = (
            Transaction
            .select(
                Transaction.sender_public_key,
                fn.SUM(Transaction.amount).alias('amount'),
                fn.SUM(Transaction.fee).alias('fee'),
            )
            .group_by(Transaction.sender_public_key)
        )

        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            wallet.balance -= int(transaction.amount)
            wallet.balance -= int(transaction.fee)

            if wallet.balance < 0 and not self.is_genesis_address(wallet.address):
                print('Negative wallet balance: {}'.format(wallet.address))

    def _build_second_signatures(self):
        transactions = (
            Transaction
            .select(Transaction.sender_public_key, Transaction.serialized)
            .where(Transaction.type == TRANSACTION_TYPE_SECOND_SIGNATURE)
        )
        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            crypto_transaction = CryptoTransaction(wallet.serialized)
            wallet.sender_public_key = crypto_transaction.asset['signature']['publicKey']

    def _build_votes(self):
        # TODO: try to optimize this query. We only need the last vote that happened
        # per sender_public_key
        transactions = (
            Transaction
            .select(Transaction.sender_public_key, Transaction.serialized)
            .where(Transaction.type == TRANSACTION_TYPE_VOTE)
            .order_by(Transaction.timestamp.desc(), Transaction.sequence.asc())
        )
        # TODO: This already_processed_wallets overhead is here so we always just
        # process the last vote transaction per sender_public_key. If we optimize
        # the SQL query to only return last record per sender_public_key, this overhead
        # can go away
        already_processed_wallets = set()
        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            if wallet.address not in already_processed_wallets:
                crypto_transaction = CryptoTransaction(wallet.serialized)
                vote = crypto_transaction.asset['votes'][0]
                # wallet.vote is only set if the wallet voted for someone. If wallet
                # did unvoted or haven't woted at all, wallet.vote needs to be set to
                # None
                if vote.startswith('+'):
                    wallet.vote = vote[1:]
                already_processed_wallets.add(wallet.address)

        # Calculate vote balances
        for voter in self._wallets.values():
            if voter.vote:
                delegate = self.find_by_public_key(wallet.vote)
                delegate.vote_balance += voter.balance

    def _build_delegates(self):
        transactions = (
            Transaction
            .select(Transaction.sender_public_key, Transaction.serialized)
            .where(Transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION)
        )

        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            crypto_transaction = CryptoTransaction(transaction.serialized)
            wallet.username = crypto_transaction.asset['delegate']['username']

        # Calculate forged blocks
        forged_blocks = (
            Block
            .select(
                Block.generator_public_key,
                fn.SUM(Block.total_fee).alias('total_fee'),
                fn.SUM(Block.reward).alias('reward'),
                fn.COUNT(Block.total_amount).alias('total_produced')
            )
            .group_by(Block.generator_public_key)
        )
        for block in forged_blocks:
            wallet = self.find_by_public_key(block.generator_public_key)
            wallet.forged_fees += int(block.total_fee)
            wallet.forged_rewards += int(block.reward)
            wallet.produced_blocks += int(block.total_produced)

        # TODO: this part
        # Calculate missed blocks
        # TODO: what does this comment mean and why is it NOT RELIABLE??????
        # // NOTE: This is highly NOT reliable, however the number of missed blocks
        # // is NOT used for the consensus
        # const delegates = await this.query.manyOrNone(queries.spv.delegatesRanks);
        # delegates.forEach((delegate, i) => {
        #     const wallet = this.walletManager.findByPublicKey(delegate.publicKey);
        #     wallet.missedBlocks = +delegate.missedBlocks;
        #     // TODO: unknown property 'rate' being access on Wallet class
        #     (wallet as any).rate = i + 1;
        #     this.walletManager.reindex(wallet);
        # });

    def _build_multi_signatures(self):
        transactions = (
            Transaction
            .select(Transaction.sender_public_key, Transaction.serialized)
            .where(Transaction.type == TRANSACTION_TYPE_MULTI_SIGNATURE)
            .order_by((Transaction.timestamp + Transaction.sequence).desc())
        )
        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            if not wallet.multisignature:
                crypto_transaction = CryptoTransaction(wallet.serialized)
                wallet.multisignature = crypto_transaction.asset['multisignature']

    def build(self):
        print('Building wallets Step 1 of 8: Received Transactions')
        self._build_received_transactions()

        print('Building wallets Step 2 of 8: Block Rewards')
        self._build_block_rewards()

        # TODO: This step seems useless
        # print('Building wallets Step 3 of 8: Last Forged Blocks')
        # self._build_last_forged_blocks()

        print('Building wallets Step 4 of 8: Sent Transactions')
        self._build_sent_transactions()

        print('Building wallets Step 5 of 8: Second Signatures')
        self._build_second_signatures()

        print('Building wallets Step 6 of 8: Votes')
        self._build_votes()

        print('Building wallets Step 7 of 8: Delegates')
        self._build_delegates()

        print('Building wallets Step 8 of 8: Multi Signatures')
        self._build_multi_signatures()

    def find_by_address(self, address):
        if address not in self._wallets:
            self._wallets[address] = Wallet({'address': address})
        return self._wallets[address]

    def find_by_public_key(self, public_key):
        if public_key not in self._public_key_map:
            address = address_from_public_key(public_key)
            wallet = self.find_by_address(address)
            wallet.public_key = public_key
            self._public_key_map[public_key] = address
            return wallet

        address = self._public_key_map[public_key]
        return self.find_by_address(address)

    def is_genesis_address(self, address):
        return address in self._genesis_addresses
