import json
import os

from redis import Redis

from chain.common.plugins import load_plugin
from chain.crypto.address import address_from_public_key
from chain.crypto.models.wallet import Wallet
from chain.crypto.utils import is_transaction_exception


class PoolWalletManager(object):
    _key = "pool_wallet:address:{}"

    def __init__(self):
        super().__init__()

        self.database = load_plugin("chain.plugins.database")

        self.redis = Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=os.environ.get("REDIS_PORT", 6379),
            db=os.environ.get("REDIS_DB", 0),
        )

    def key_for_address(self, address):
        return self._key.format(address)

    def clear_wallets(self):
        """Clear all pool wallets from redis
        """
        keys = self.redis.keys(self.key_for_address("*"))
        if keys:
            self.redis.delete(*keys)

    def save_wallet(self, wallet):
        self.redis.set(self.key_for_address(wallet.address), wallet.to_json())

    def find_by_address(self, address):
        """Finds a wallet by a given address. If wallet is not found, it is copied from
        blockchain wallet manager.

        :param string address: wallet address
        :returns Wallet: wallet object
        """
        key = self.key_for_address(address)
        if not self.redis.exists(key):
            self.save_wallet(self.database.wallets.find_by_address(address))
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

    def exists_by_address(self, address):
        key = self.key_for_address(address)
        return self.redis.exists(key)

    def exists_by_public_key(self, public_key):
        address = address_from_public_key(public_key)
        return self.exists_by_address(address)

    def delete_by_public_key(self, public_key):
        """Deletes a wallet by public key

        :param string public_key: wallets' public key
        """
        address = address_from_public_key(public_key)
        key = self.key_for_address(address)
        self.redis.delete(key)

    def can_apply_to_sender(self, transaction, block_height):
        """Checks if transaction can be applied to senders wallet

        :param Transaction transaction: Crypto transaction object
        :returns bool: True if can be applied, False otherwise
        """

        # If sender is not yet known or has no balance, they can't apply
        # The check is performed against the database wallet manager and not pool
        # wallet manager
        if self.database.wallets.exists(transaction.sender_public_key):
            db_wallet = self.database.wallets.find_by_public_key(
                transaction.sender_public_key
            )
            if db_wallet.balance == 0:
                print("Wallet is not allowed to send as it doesn't have any funds")
                return False

        if is_transaction_exception(transaction.id):
            print(
                "Transaction forcibly applied because it has been added as an "
                "exception".format(transaction.id)
            )
            return True
        sender = self.find_by_public_key(transaction.sender_public_key)
        return transaction.can_be_applied_to_wallet(
            sender, self.database.wallets, block_height
        )
