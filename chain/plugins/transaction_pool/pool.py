import json
import os
from collections import defaultdict

from redis import Redis

from chain.common.config import config
from chain.common.plugins import load_plugin
from chain.crypto import time
from chain.crypto.objects.transaction import Transaction as CryptoTransaction
from chain.plugins.database.models.pool_transaction import PoolTransaction


class Pool(object):
    key_blocked = "transaction_pool:blocked:{}"

    def __init__(self):
        super().__init__()

        # Load the database plugin to correctly setup PoolTransaction model
        load_plugin("chain.plugins.database")

        self.redis = Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=os.environ.get("REDIS_PORT", 6379),
            db=os.environ.get("REDIS_DB", 0),
        )

    def _get_expired(self):
        """Fetches expired transactions from the database

        :returns list: List of expired transactions
        """
        current_time = time.get_time()
        transactions = list(
            PoolTransaction.select().where(PoolTransaction.expires_at <= current_time)
        )
        return transactions

    def _purge_expired(self):
        expired_transactions = self._get_expired()

        ids = []
        for transaction in expired_transactions:
            # TODO
            # this.walletManager.revertTransactionForSender(transaction);

            ids.append(transaction.id)

        delete_query = PoolTransaction.delete().where(PoolTransaction.id._in(ids))
        delete_query.execute()

    def transaction_exists(self, transaction_id):
        query = PoolTransaction.select().where(PoolTransaction.id == transaction_id)
        return query.exists()

    def is_sender_blocked(self, sender_public_key):
        return self.redis.exists(self.key_blocked.format(sender_public_key))

    def block_sender(self, sender_public_key):
        """Blocks a sender for one hour
        """
        key = self.key_blocked.format(sender_public_key)
        self.redis.set(key, 0, ex=3600)

    def has_exceeded_max_transactions(self, sender_public_key):
        """Checks whether sender or transaction has exceeded max transactions in queue

        :param str sender_public_key: Sender's public key
        """
        self._purge_expired()
        # TODO:

    def process_transactions(self, transactions):
        errors = defaultdict(list)

        for transaction_data in transactions:

            # NOTE: This check doesn't correctly check if transaction data is larger
            # than `max_transaction_bytes`. It doesn't account for special characters
            # which take two bytes.
            # It also doesn't really check if the transaction larger as it's checking
            # the payload we receive and not the actual transaction that we're going to
            # process. But this is done here like this for consistency with the core
            if len(json.dumps(transaction_data)) > config.pool.max_transaction_bytes:
                errors[transaction_data["id"]].append(
                    "Transaction {} is larger than {} bytes".format(
                        transaction_data["id"], config.pool.max_transaction_bytes
                    )
                )
                continue

            transaction = CryptoTransaction.from_dict(transaction_data)

            if self.transaction_exists(transaction.id):
                errors[transaction.id].append(
                    "Transaction {} already exists".format(transaction.id)
                )
            elif self.is_sender_blocked(transaction.sender_public_key):
                errors[transaction.id].append(
                    "Transaction {} rejected. Sender {} is blocked.".format(
                        transaction.id, transaction.sender_public_key
                    )
                )
            # elif
