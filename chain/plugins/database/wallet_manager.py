import os
from datetime import datetime

from peewee import fn

import psutil

from redis import Redis

from chain.common.config import config
from chain.crypto.address import address_from_public_key
from chain.crypto.constants import (
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_TRANSFER,
    TRANSACTION_TYPE_VOTE,
)
from chain.crypto.models.wallet import Wallet
from chain.crypto.utils import calculate_round, is_transaction_exception

from .models.block import Block
from .models.transaction import Transaction


def get_memory_precent():
    mem = psutil.virtual_memory()
    return mem.percent


class WalletManager(object):
    def __init__(self):
        super().__init__()
        self.redis = Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=os.environ.get("REDIS_PORT", 6379),
            db=os.environ.get("REDIS_DB", 0),
        )

        Wallet._redis = self.redis

        # Clear wallets from redis
        keys = self.redis.keys(Wallet._key.format("*"))
        if keys:
            self.redis.delete(*keys)
        username_keys = self.redis.keys(Wallet._username_key.format("*"))
        if username_keys:
            self.redis.delete(*username_keys)

        self._genesis_addresses = set()
        for transaction in config.genesis_block["transactions"]:
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
            wallet.save()

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
            wallet.save()

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
                print(
                    "Negative wallet balance: {} {}".format(
                        wallet.address, wallet.balance
                    )
                )
            wallet.save()

    def _build_second_signatures(self):
        transactions = Transaction.select(
            Transaction.sender_public_key, Transaction.asset
        ).where(Transaction.type == TRANSACTION_TYPE_SECOND_SIGNATURE)
        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            wallet.sender_public_key = transaction.asset["signature"]["publicKey"]
            wallet.save()

    def _build_votes(self):
        # TODO: try to optimize this query. We only need the last vote that happened
        # per sender_public_key
        transactions = (
            Transaction.select(Transaction.sender_public_key, Transaction.asset)
            .where(Transaction.type == TRANSACTION_TYPE_VOTE)
            .order_by(Transaction.timestamp.desc(), Transaction.sequence.asc())
        )
        # TODO: This already_processed_wallets overhead is here so we always just
        # process the last vote transaction per sender_public_key. If we optimize
        # the SQL query to only return last record per sender_public_key, this overhead
        # can go away
        already_processed_wallets = set()
        voters = []
        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            if wallet.address not in already_processed_wallets:
                vote = transaction.asset["votes"][0]
                # wallet.vote is only set if the wallet voted for someone. If wallet
                # unvoted or haven't woted at all, wallet.vote needs to be set to
                # None
                if vote.startswith("+"):
                    wallet.vote = vote[1:]
                    voters.append(wallet.address)
                already_processed_wallets.add(wallet.address)
                wallet.save()

        # Calculate vote balances
        for voter_address in voters:
            voter = self.find_by_address(voter_address)
            delegate = self.find_by_public_key(voter.vote)
            delegate.vote_balance += voter.balance
            delegate.save()

    def _build_delegates(self):
        transactions = Transaction.select(
            Transaction.sender_public_key, Transaction.asset
        ).where(Transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION)

        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            wallet.username = transaction.asset["delegate"]["username"]
            wallet.save()
            self.redis.set(wallet.username_key, wallet.address)

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
            wallet.save()

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
            Transaction.select(Transaction.sender_public_key, Transaction.asset)
            .where(Transaction.type == TRANSACTION_TYPE_MULTI_SIGNATURE)
            .order_by((Transaction.timestamp + Transaction.sequence).desc())
        )
        for transaction in transactions:
            wallet = self.find_by_public_key(transaction.sender_public_key)
            if not wallet.multisignature:
                wallet.multisignature = transaction.asset["multisignature"]
                wallet.save()

    def build(self):
        # Execution order of functions below is very important!
        start = datetime.now()
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 1 of 8: Received Transactions")
        self._build_received_transactions()
        print(datetime.now() - start)
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 2 of 8: Block Rewards")
        self._build_block_rewards()
        print(datetime.now() - start)
        # TODO: This step seems useless
        # print('Building wallets Step 3 of 8: Last Forged Blocks')
        # self._build_last_forged_blocks()
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 4 of 8: Sent Transactions")
        self._build_sent_transactions()
        print(datetime.now() - start)
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 5 of 8: Second Signatures")
        self._build_second_signatures()
        print(datetime.now() - start)
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 6 of 8: Votes")
        self._build_votes()
        print(datetime.now() - start)
        print("Memory percent:", get_memory_precent())
        print("Building wallets Step 7 of 8: Delegates")
        self._build_delegates()
        print(datetime.now() - start)

        print("Building wallets Step 8 of 8: Multi Signatures")
        self._build_multi_signatures()
        print(datetime.now() - start)

        # TODO: Verify that no wallet has negative balance!

    def find_by_address(self, address):
        if not isinstance(address, str):
            raise ValueError("address must be str")
        assert isinstance(address, str)
        wallet = Wallet.get(address)
        if wallet:
            return wallet
        return Wallet({"address": address})

    def find_by_public_key(self, public_key):
        address = address_from_public_key(public_key)
        wallet = self.find_by_address(address)
        if wallet.public_key is None:
            wallet.public_key = public_key
            wallet.save()
        return wallet

    def is_genesis_address(self, address):
        return address in self._genesis_addresses

    def exists(self, public_key):
        address = address_from_public_key(public_key)
        if self.redis.exists(Wallet._key.format(address)) == 1:
            return True
        return False

    def delegate_exists(self, username):
        if not username:
            return False
        if self.redis.exists(Wallet._username_key.format(username.lower())) == 1:
            return True
        return False

    def is_delegate(self, public_key):
        """Checks if a given publick_key is a registered delegate
        """
        wallet = self.find_by_public_key(public_key)
        return self.delegate_exists(wallet.username)

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
            delegate.save()

        else:
            # Update vote balance of the sender's delegate
            if sender.vote:
                delegate = self.find_by_public_key(sender.vote)
                total = transaction.amount + transaction.fee
                if revert:
                    delegate.vote_balance += total
                else:
                    delegate.vote_balance -= total
                delegate.save()

            # Update vote balance of recipient's delegate
            if recipient and recipient.vote:
                delegate = self.find_by_public_key(recipient.vote)
                if revert:
                    delegate.vote_balance -= transaction.amount
                else:
                    delegate.vote_balance += transaction.amount
                delegate.save()

    def apply_transaction(self, transaction, block):
        if (
            transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION
            and self.delegate_exists(transaction.asset["delegate"]["username"])
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
        sender.save()

        # If transaction is a delegate registration, add sender wallet to the
        # _username_map
        if transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            print("Registering delegate")
            self.redis.set(sender.username_key, sender.address)

        recipient = None
        if transaction.recipient_id:
            recipient = self.find_by_address(transaction.recipient_id)

            if transaction.type == TRANSACTION_TYPE_TRANSFER:
                recipient.apply_transaction_to_recipient(transaction)
                recipient.save()

        self._update_vote_balances(sender, recipient, transaction)

    # TODO: find a better name for this function
    def apply_block(self, block):
        # If it's not a genesis block and can't find a delegate, raise an exception
        if block.height != 1 and not self.exists(block.generator_public_key):
            # TODO: exception
            raise Exception(
                "Could not find a delegate with public key: {}".format(
                    block.generator_public_key
                )
            )

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

        delegate = self.find_by_public_key(block.generator_public_key)
        delegate.apply_block(block)
        delegate.save()
        # If delegate votes for somewone, we need to update vote balance for the
        # voted delegate
        if delegate.vote:
            voted_delegate = self.find_by_public_key(delegate.vote)
            voted_delegate.vote_balance += block.reward + block.total_fee
            voted_delegate.save()

    def load_active_delegate_wallets(self, height):
        current_round, _, max_delegates = calculate_round(height)
        if height > 1 and height % max_delegates != 1:
            # TODO: exception
            raise Exception("Trying to build delegates outside of round change")

        delegate_wallets = []

        keys = self.redis.keys(Wallet._username_key.format("*"))
        addresses = self.redis.mget(keys)
        for address in addresses:
            wallet = self.find_by_address(address.decode())
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
        sender.save()

        # Removing the wallet from the delegates index
        if transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            self.redis.delete(
                Wallet._username_key.format(
                    transaction.asset["delegate"]["username"].lower()
                )
            )

        recipient = self.find_by_address(transaction.recipient_id)
        if transaction.type == TRANSACTION_TYPE_TRANSFER:
            recipient.revert_transaction_for_recipient(transaction)
            recipient.save()

        self._update_vote_balances(sender, recipient, transaction, revert=True)

    def revert_block(self, block):
        delegate = self.find_by_public_key(block.generator_public_key)

        # Revert transactions from last to first
        for transaction in reversed(block.transactions):
            self.revert_transaction(transaction)

        delegate.revert_block()
        delegate.save()

        # If delegate votes for somewone, we need to update vote balance for the
        # voted delegate
        if delegate.vote:
            voted_delegate = self.find_by_public_key(delegate.vote)
            voted_delegate.vote_balance -= block.reward + block.total_fee
            voted_delegate.save()
