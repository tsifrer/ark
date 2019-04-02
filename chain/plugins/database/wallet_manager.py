from peewee import fn

import psutil

from chain.config import Config
from chain.crypto.address import address_from_public_key
from chain.crypto.constants import (
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_TRANSFER,
    TRANSACTION_TYPE_VOTE,
)
from chain.crypto.models.wallet import Wallet
from chain.crypto.objects.transaction import Transaction as CryptoTransaction
from chain.crypto.utils import calculate_round, is_transaction_exception

from .models.block import Block
from .models.transaction import Transaction


def get_memory_precent():
    mem = psutil.virtual_memory()
    return mem.percent


# Wallets are stored in memory, as they're rebuilt every time you startup the relay.
# For now there's no valid need to store them in DB yet.

# TODO: Extensive tests
class WalletManager(object):
    def __init__(self, database):
        super().__init__()
        self.db = database

        # TODO: Terrible names
        self._wallets = {}
        self._public_key_map = {}
        self._username_map = {}

        config = Config()
        self._genesis_addresses = set()
        for transaction in config["genesis_block"]["transactions"]:
            self._genesis_addresses.add(transaction["senderId"])

    def _build_received_transactions(self):
        """Load and apply received transactions to wallets.
        """
        transactions = (
            Transaction.select(
                Transaction.recipient_id, fn.SUM(Transaction.amount).alias("amount")
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
        blocks = Block.select(
            Block.generator_public_key,
            fn.SUM(Block.reward + Block.total_fee).alias("reward"),
        ).group_by(Block.generator_public_key)

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
        transactions = Transaction.select(
            Transaction.sender_public_key,
            fn.SUM(Transaction.amount).alias("amount"),
            fn.SUM(Transaction.fee).alias("fee"),
        ).group_by(Transaction.sender_public_key)

        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            wallet.balance -= int(transaction.amount)
            wallet.balance -= int(transaction.fee)

            if wallet.balance < 0 and not self.is_genesis_address(wallet.address):
                total = int(transaction.amount) + int(transaction.fee)
                print(
                    "Negative wallet balance: {} {}".format(
                        wallet.address, wallet.balance
                    )
                )
                print(total)
                print(wallet.__dict__)

    def _build_second_signatures(self):
        transactions = Transaction.select(
            Transaction.sender_public_key, Transaction.serialized
        ).where(Transaction.type == TRANSACTION_TYPE_SECOND_SIGNATURE)
        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            crypto_transaction = CryptoTransaction.from_serialized(
                transaction.serialized
            )
            wallet.sender_public_key = crypto_transaction.asset["signature"][
                "publicKey"
            ]

    def _build_votes(self):
        # TODO: try to optimize this query. We only need the last vote that happened
        # per sender_public_key
        transactions = (
            Transaction.select(Transaction.sender_public_key, Transaction.serialized)
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
                crypto_transaction = CryptoTransaction.from_serialized(
                    transaction.serialized
                )
                vote = crypto_transaction.asset["votes"][0]
                # wallet.vote is only set if the wallet voted for someone. If wallet
                # did unvoted or haven't woted at all, wallet.vote needs to be set to
                # None
                if vote.startswith("+"):
                    wallet.vote = vote[1:]
                already_processed_wallets.add(wallet.address)

        # Calculate vote balances
        for voter in self._wallets.values():
            if voter.vote:
                delegate = self.find_by_public_key(voter.vote)
                delegate.vote_balance += voter.balance

    def _build_delegates(self):
        transactions = Transaction.select(
            Transaction.sender_public_key, Transaction.serialized
        ).where(Transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION)

        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            crypto_transaction = CryptoTransaction.from_serialized(
                transaction.serialized
            )
            wallet.username = crypto_transaction.asset["delegate"]["username"]
            self._username_map[wallet.username.lower()] = wallet.address

        # Calculate forged blocks
        forged_blocks = Block.select(
            Block.generator_public_key,
            fn.SUM(Block.total_fee).alias("total_fee"),
            fn.SUM(Block.reward).alias("reward"),
            fn.COUNT(Block.total_amount).alias("total_produced"),
        ).group_by(Block.generator_public_key)
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
            Transaction.select(Transaction.sender_public_key, Transaction.serialized)
            .where(Transaction.type == TRANSACTION_TYPE_MULTI_SIGNATURE)
            .order_by((Transaction.timestamp + Transaction.sequence).desc())
        )
        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            if not wallet.multisignature:
                crypto_transaction = CryptoTransaction.from_serialized(
                    transaction.serialized
                )
                wallet.multisignature = crypto_transaction.asset["multisignature"]

    def build(self):
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 1 of 8: Received Transactions")
        self._build_received_transactions()
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 2 of 8: Block Rewards")
        self._build_block_rewards()

        # TODO: This step seems useless
        # print('Building wallets Step 3 of 8: Last Forged Blocks')
        # self._build_last_forged_blocks()
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 4 of 8: Sent Transactions")
        self._build_sent_transactions()
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 5 of 8: Second Signatures")
        self._build_second_signatures()
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 6 of 8: Votes")
        self._build_votes()
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 7 of 8: Delegates")
        self._build_delegates()

        print("Building wallets Step 8 of 8: Multi Signatures")
        self._build_multi_signatures()

        # TODO: Verify that no wallet has negative balance!

    def find_by_address(self, address):
        if address not in self._wallets:
            self._wallets[address] = Wallet({"address": address})
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

    def is_delegate(self, public_key):
        """Checks if a given publick_key is a registered delegate
        """
        wallet = self.find_by_public_key(public_key)
        is_delegate = self._username_map.get(wallet.username)
        return True if is_delegate else False

    def _update_vote_balances(self, sender, recipient, transaction, revert=False):
        # TODO: refactor this to make more sense
        if transaction.type == TRANSACTION_TYPE_VOTE:
            vote = transaction.asset["votes"][0]
            delegate = self.find_by_public_key(vote[1:])
            if vote.startswith("+"):
                if revert:
                    delegate.vote_balance -= sender.balance - transaction.fee
                else:
                    delegate.vote_balance += sender.balance
            else:
                if revert:
                    delegate.vote_balance += sender.balance
                else:
                    delegate.vote_balance -= sender.balance + transaction.fee

        else:
            # Update vote balance of the sender's delegate
            if sender.vote:
                delegate = self.find_by_public_key(sender.vote)
                total = transaction.amount + transaction.fee
                if revert:
                    delegate.vote_balance += total
                else:
                    delegate.vote_balance -= total

            # Update vote balance of recipient's delegate
            if recipient.vote:
                delegate = self.find_by_public_key(recipient.vote)
                if revert:
                    delegate.vote_balance -= transaction.amount
                else:
                    delegate.vote_balance += transaction.amount

    def apply_transaction(self, transaction, block):
        if (
            transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION
            and transaction.asset["delegate"]["username"] in self._username_map
        ):
            # TODO: exception
            raise Exception(
                "Can't apply transaction {}: delegate name {} already taken".format(
                    transaction.id, transaction.asset["delegate"]["username"]
                )
            )

        elif transaction.type == TRANSACTION_TYPE_VOTE and not self.is_delegate(
            transaction.asset["votes"][0][1:]
        ):
            # TODO: exception
            raise Exception(
                "Can't apply transaction {}: delegate {} does not exist".format(
                    transaction.id, transaction.asset["votes"][0][1:]
                )
            )
        elif transaction.type == TRANSACTION_TYPE_SECOND_SIGNATURE:
            # TODO: no idea why we need to do this. It seems like a flaw, as if
            # there was something in here, the serialized transaction will not match
            # with the newly serialized one.
            transaction.recipient_id = None

        sender = self.find_by_public_key(transaction.sender_public_key)
        # Handle transaction exceptions and verify that we can apply the transaction
        # to the sender
        if is_transaction_exception(transaction):
            print(
                "Transaction {} forcibly applied because it has been added as an "
                "exception.".format(self.id)
            )
        else:
            can_apply, errors = sender.can_apply(transaction, block)
            if not can_apply:
                print(
                    "Can't apply transaction {} from sender due to {}".format(
                        transaction.id, sender.address, errors
                    )
                )

        sender.apply_transaction_to_sender(transaction)

        # If transaction is a delegate registration, add sender wallet to the
        # _username_map
        if transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            self._username_map[sender.username] = sender.address

        recipient = self.find_by_address(transaction.recipient_id)
        if transaction.type == TRANSACTION_TYPE_TRANSFER:
            recipient.apply_transaction_to_recipient(transaction)

        self._update_vote_balances(sender, recipient, transaction)

    # TODO: find a better name for this function
    def apply_block(self, block):
        # If it's not a genesis block and can't find a delegate, raise an exception
        if block.height != 1 and block.generator_public_key not in self._public_key_map:
            # TODO: exception
            raise Exception(
                "Could not find a delegate with public key: {}".format(
                    block.generator_public_key
                )
            )

        delegate = self.find_by_public_key(block.generator_public_key)

        # TODO: Wrap the code below in try except and do a reverse action
        # Be careful to do it correctly as the Ark Core code doesn't do it correctly
        # at the moment (read the comments in the Ark Core catch block)
        applied_transactions = []
        try:
            for transaction in block.transactions:
                self.apply_transaction(transaction, block)
                applied_transactions.append(transaction)
        except Exception as e:  # TODO: better exception handling, not so broad
            print(
                "Failed to apply all transactions in block - reverting previous "
                "transactions"
            )
            for transaction in reversed(applied_transactions):
                self.revert_transaction(transaction)
            raise e

        delegate.apply_block(block)
        # If delegate votes for somewone, we need to update vote balance for the
        # voted delegate
        if delegate.vote:
            voted_delegate = self.find_by_public_key(delegate.vote)
            voted_delegate.vote_balance += block.reward + block.total_fee

    def load_active_delegate_wallets(self, height):
        current_round, _, max_delegates = calculate_round(height)
        if height > 1 and height % max_delegates != 1:
            # TODO: exception
            raise Exception("Trying to build delegates outside of round change")

        delegate_wallets = []
        for address in self._username_map.values():
            wallet = self.find_by_address(address)
            delegate_wallets.append(wallet)

        if len(delegate_wallets) < max_delegates:
            raise Exception(
                "Expected to find {} delegates but only found {}.".format(
                    max_delegates, len(delegate_wallets)
                )
            )
        # Sort delegate wallets by balance and use public key as a tiebreaker
        # Sort wallets by balance descending and by public key ascending. Because
        # vote_balance is a number, use a negative number to sort it descending
        # and public_key to sort it ascending.
        delegate_wallets.sort(key=lambda x: (-x.vote_balance, x.public_key))

        # for wallet in delegate_wallets[:60]:
        #     print(wallet.username, wallet.public_key, wallet.balance)

        delegate_wallets = delegate_wallets[:max_delegates]
        print("Loaded {} active delegates".format(len(delegate_wallets)))
        return delegate_wallets

    def revert_transaction(self, transaction):
        sender = self.find_by_public_key(transaction.sender_public_key)

        sender.revert_transaction_for_sender(transaction)

        # Removing the wallet from the delegates index
        if transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            del self._username_map[transaction.asset["delegate"]["username"]]

        recipient = self.find_by_address(transaction.recipient_id)
        if transaction.type == TRANSACTION_TYPE_TRANSFER:
            recipient.revert_transaction_for_recipient(transaction)

        self._update_vote_balances(sender, recipient, transaction, revert=True)

    def revert_block(self, block):
        delegate = self.find_by_public_key(block.generator_public_key)

        # Revert transactions from last to first
        for transaction in reversed(block.transactions):
            self.revert_transaction(transaction)

        delegate.revert_block()

        # If delegate votes for somewone, we need to update vote balance for the
        # voted delegate
        if delegate.vote:
            voted_delegate = self.find_by_public_key(delegate.vote)
            voted_delegate.vote_balance -= block.reward + block.total_fee
