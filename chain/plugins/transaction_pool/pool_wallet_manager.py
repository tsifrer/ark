import json
import os

from peewee import fn

from redis import Redis

from chain.common.config import config
from chain.common.plugins import load_plugin
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
from chain.crypto.utils import is_transaction_exception

class PoolWalletManager(object):
    wallet_key = 'pool_wallet:{}'

    def __init__(self):
        super().__init__()

        self.database = load_plugin("chain.plugins.database")

        self.redis = Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=os.environ.get("REDIS_PORT", 6379),
            db=os.environ.get("REDIS_DB", 0),
        )

        self._public_key_map = {}
        # self._username_map = {}

        # self._genesis_addresses = set()
        # for transaction in config.genesis_block["transactions"]:
        #     self._genesis_addresses.add(transaction["senderId"])

    def find_by_address(self, address):
        """Finds a wallet by a given address. If wallet is not found, it is copied from
        blockchain wallet manager.

        :param string address: wallet address
        :returns Wallet: wallet object
        """
        key = self.wallet_key.format(address)
        if not self.redis.exists(key):
            self.redis.set(key, self.database.wallets.find_by_address(address))
        wallet = json.loads(self.redis.get(key))
        return Wallet(wallet)

    def find_by_public_key(self, public_key):
        """Finds a wallet by public key.

        It calculates the address from public key and uses the `find_by_address`
        function, which if wallet is not found for this address, it copies it from
        blockchain wallet manager.

        :param string public_key: wallet's public key
        :returns Wallet: wallet object
        """
        address = address_from_public_key(public_key)
        return self.find_by_address(address)

    def delete_by_public_key(self, public_key):
        """Deletes a wallet by public key

        :param string public_key: wallets' public key
        """
        address = address_from_public_key(public_key)
        key = self.wallet_key.format(address)
        self.redis.delete(key)

    def can_apply(self, transaction):
        """Checks if transaction can be applied

        :param Transaction transaction: Crypto transaction object
        :returns tuple: Tuple consisting of bool can_appy and list of errors
                        (can_apply, errors)
        """
        errors = []

        # If sender is not yet known or has no balance, they can't apply
        # The check is performed against the database wallet manager and not pool
        # wallet manager
        if self.database.wallets.exists(transaction.sender_public_key):
            db_wallet = self.database.wallets.find_by_public_key(transaction.sender_public_key)
            if db_wallet.balance == 0:
                return False
        
        sender = self.find_by_public_key(transaction.sender_public_key)


        is_transaction_exception








        
















    # def is_delegate(self, public_key):
    #     """Checks if a given publick_key is a registered delegate
    #     """
    #     wallet = self.find_by_public_key(public_key)
    #     is_delegate = self._username_map.get(wallet.username)
    #     return True if is_delegate else False

    # def _update_vote_balances(self, sender, recipient, transaction, revert=False):
    #     # TODO: refactor this to make more sense
    #     if transaction.type == TRANSACTION_TYPE_VOTE:
    #         vote = transaction.asset["votes"][0]
    #         delegate = self.find_by_public_key(vote[1:])
    #         if vote.startswith("+"):
    #             if revert:
    #                 delegate.vote_balance -= sender.balance - transaction.fee
    #             else:
    #                 delegate.vote_balance += sender.balance
    #         else:
    #             if revert:
    #                 delegate.vote_balance += sender.balance
    #             else:
    #                 delegate.vote_balance -= sender.balance + transaction.fee

    #     else:
    #         # Update vote balance of the sender's delegate
    #         if sender.vote:
    #             delegate = self.find_by_public_key(sender.vote)
    #             total = transaction.amount + transaction.fee
    #             if revert:
    #                 delegate.vote_balance += total
    #             else:
    #                 delegate.vote_balance -= total

    #         # Update vote balance of recipient's delegate
    #         if recipient.vote:
    #             delegate = self.find_by_public_key(recipient.vote)
    #             if revert:
    #                 delegate.vote_balance -= transaction.amount
    #             else:
    #                 delegate.vote_balance += transaction.amount

    # def apply_transaction(self, transaction, block):
    #     if (
    #         transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION
    #         and transaction.asset["delegate"]["username"] in self._username_map
    #     ):
    #         # TODO: exception
    #         raise Exception(
    #             "Can't apply transaction {}: delegate name {} already taken".format(
    #                 transaction.id, transaction.asset["delegate"]["username"]
    #             )
    #         )

    #     elif transaction.type == TRANSACTION_TYPE_VOTE and not self.is_delegate(
    #         transaction.asset["votes"][0][1:]
    #     ):
    #         # TODO: exception
    #         raise Exception(
    #             "Can't apply transaction {}: delegate {} does not exist".format(
    #                 transaction.id, transaction.asset["votes"][0][1:]
    #             )
    #         )
    #     elif transaction.type == TRANSACTION_TYPE_SECOND_SIGNATURE:
    #         # TODO: no idea why we need to do this. It seems like a flaw, as if
    #         # there was something in here, the serialized transaction will not match
    #         # with the newly serialized one.
    #         transaction.recipient_id = None

    #     sender = self.find_by_public_key(transaction.sender_public_key)
    #     # Handle transaction exceptions and verify that we can apply the transaction
    #     # to the sender
    #     if is_transaction_exception(transaction):
    #         print(
    #             "Transaction {} forcibly applied because it has been added as an "
    #             "exception.".format(self.id)
    #         )
    #     else:
    #         can_apply, errors = sender.can_apply(transaction, block)
    #         if not can_apply:
    #             print(
    #                 "Can't apply transaction {} from sender due to {}".format(
    #                     transaction.id, sender.address, errors
    #                 )
    #             )

    #     sender.apply_transaction_to_sender(transaction)

    #     # If transaction is a delegate registration, add sender wallet to the
    #     # _username_map
    #     if transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
    #         self._username_map[sender.username] = sender.address

    #     recipient = self.find_by_address(transaction.recipient_id)
    #     if transaction.type == TRANSACTION_TYPE_TRANSFER:
    #         recipient.apply_transaction_to_recipient(transaction)

    #     self._update_vote_balances(sender, recipient, transaction)

    # # TODO: find a better name for this function
    # def apply_block(self, block):
    #     # If it's not a genesis block and can't find a delegate, raise an exception
    #     if block.height != 1 and block.generator_public_key not in self._public_key_map:
    #         # TODO: exception
    #         raise Exception(
    #             "Could not find a delegate with public key: {}".format(
    #                 block.generator_public_key
    #             )
    #         )

    #     delegate = self.find_by_public_key(block.generator_public_key)

    #     # TODO: Wrap the code below in try except and do a reverse action
    #     # Be careful to do it correctly as the Ark Core code doesn't do it correctly
    #     # at the moment (read the comments in the Ark Core catch block)
    #     applied_transactions = []
    #     try:
    #         for transaction in block.transactions:
    #             self.apply_transaction(transaction, block)
    #             applied_transactions.append(transaction)
    #     except Exception as e:  # TODO: better exception handling, not so broad
    #         print(
    #             "Failed to apply all transactions in block - reverting previous "
    #             "transactions"
    #         )
    #         for transaction in reversed(applied_transactions):
    #             self.revert_transaction(transaction)
    #         raise e

    #     delegate.apply_block(block)
    #     # If delegate votes for somewone, we need to update vote balance for the
    #     # voted delegate
    #     if delegate.vote:
    #         voted_delegate = self.find_by_public_key(delegate.vote)
    #         voted_delegate.vote_balance += block.reward + block.total_fee

    # def load_active_delegate_wallets(self, height):
    #     current_round, _, max_delegates = calculate_round(height)
    #     if height > 1 and height % max_delegates != 1:
    #         # TODO: exception
    #         raise Exception("Trying to build delegates outside of round change")

    #     delegate_wallets = []
    #     for address in self._username_map.values():
    #         wallet = self.find_by_address(address)
    #         delegate_wallets.append(wallet)

    #     if len(delegate_wallets) < max_delegates:
    #         raise Exception(
    #             "Expected to find {} delegates but only found {}.".format(
    #                 max_delegates, len(delegate_wallets)
    #             )
    #         )
    #     # Sort delegate wallets by balance and use public key as a tiebreaker
    #     # Sort wallets by balance descending and by public key ascending. Because
    #     # vote_balance is a number, use a negative number to sort it descending
    #     # and public_key to sort it ascending.
    #     delegate_wallets.sort(key=lambda x: (-x.vote_balance, x.public_key))

    #     # for wallet in delegate_wallets[:60]:
    #     #     print(wallet.username, wallet.public_key, wallet.balance)

    #     delegate_wallets = delegate_wallets[:max_delegates]
    #     print("Loaded {} active delegates".format(len(delegate_wallets)))
    #     return delegate_wallets

    # def revert_transaction(self, transaction):
    #     sender = self.find_by_public_key(transaction.sender_public_key)

    #     sender.revert_transaction_for_sender(transaction)

    #     # Removing the wallet from the delegates index
    #     if transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
    #         del self._username_map[transaction.asset["delegate"]["username"]]

    #     recipient = self.find_by_address(transaction.recipient_id)
    #     if transaction.type == TRANSACTION_TYPE_TRANSFER:
    #         recipient.revert_transaction_for_recipient(transaction)

    #     self._update_vote_balances(sender, recipient, transaction, revert=True)

    # def revert_block(self, block):
    #     delegate = self.find_by_public_key(block.generator_public_key)

    #     # Revert transactions from last to first
    #     for transaction in reversed(block.transactions):
    #         self.revert_transaction(transaction)

    #     delegate.revert_block()

    #     # If delegate votes for somewone, we need to update vote balance for the
    #     # voted delegate
    #     if delegate.vote:
    #         voted_delegate = self.find_by_public_key(delegate.vote)
    #         voted_delegate.vote_balance -= block.reward + block.total_fee
