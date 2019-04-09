import json
import os
from collections import defaultdict

from redis import Redis

from chain.common.config import config
from chain.common.plugins import load_plugin
from chain.crypto import time
from chain.crypto.objects.transaction import Transaction as CryptoTransaction
from chain.plugins.database.models.pool_transaction import PoolTransaction
from chain.crypto import slots, time
from chain.crypto.constants import (
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_DELEGATE_RESIGNATION,
    TRANSACTION_TYPE_MULTI_PAYMENT,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_VOTE,
    TRANSACTION_TYPE_TRANSFER,
)

from .utils import is_recipient_on_current_network


class Pool(object):
    _blocked_key = "transaction_pool:blocked:{}"

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
        """Checks if sender is blocked.
        If key exists in redis, then the sender is blocked, otherwise it's not.

        :param string sender_public_key: Sender's public key
        :returns bool: True if blocked, False otherwise.
        """
        return self.redis.exists(self._blocked_key.format(sender_public_key))

    def block_sender(self, sender_public_key):
        """Blocks a sender for one hour

        :param string sender_public_key: Sender's public key
        """
        key = self._blocked_key.format(sender_public_key)
        self.redis.set(key, 0, ex=3600)

    def has_exceeded_max_transactions(self, sender_public_key):
        """Checks whether sender or transaction has exceeded max transactions in queue

        :param str sender_public_key: Sender's public key
        """
        self._purge_expired()
        if sender_public_key in config.pool["allowed_senders"]:
            print(
                "Sender with public key {} is an allowed sender, thus skipping "
                "throttling".format(sender_public_key)
            )
            return False

        count = (
            PoolTransaction.select()
            .where(PoolTransaction.sender_public_key == sender_public_key)
            .count()
        )
        return count > config.pool["max_transactions_per_sender"]

    def _sender_has_transactions_of_type(self, transaction):
        query = PoolTransaction.select().where(
            PoolTransaction.sender_public_key == transaction.sender_public_key,
            PoolTransaction.type == transaction.type,
        )
        return query.exists()

    def _validate_transaction_by_type(self, transaction, all_transactions):
        vote_and_signature = [TRANSACTION_TYPE_VOTE, TRANSACTION_TYPE_SECOND_SIGNATURE]
        if transaction.type in vote_and_signature:
            if self._sender_has_transactions_of_type(transaction):
                error = (
                    "Sender {} already has a transaction of type {} in the "
                    "pool".format(transaction.sender_public_key, transaction.type)
                )
                return False, error
            else:
                return True, None

        elif transaction.type == TRANSACTION_TYPE_TRANSFER:
            if not is_recipient_on_current_network(transaction.recipient_id):
                error = "Recipient {} is not on the same network".format(
                    transaction.recipient_id
                )
                return False, error
            else:
                return True, None

        elif transaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            if self._sender_has_transactions_of_type(transaction):
                error = (
                    "Sender {} already has a transaction of type {} in the "
                    "pool".format(transaction.sender_public_key, transaction.type)
                )
                return False, error

            # Reject all delegate registration transactions with the same delegate
            # name if there are more than one with the same name
            num_same_delegate_registration_in_payload = [
                trans
                for trans in all_transactions
                if trans.asset["delegate"]["username"]
                == transaction.asset["delegate"]["username"]
            ]
            if len(num_same_delegate_registration_in_payload) > 1:
                error = (
                    "Multiple delegate registrations for {} in transaction "
                    "payload".format(transaction.asset["delegate"]["username"])
                )
                return False, error

            # Reject a transaction if delegate registration transaction for the same
            # username is already in the pool
            exists_in_pool = (
                PoolTransaction.select()
                .where(
                    PoolTransaction.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION,
                    PoolTransaction.asset["delegate"]["username"]
                    == transaction.asset["delegate"]["username"],
                )
                .exists()
            )
            if exists_in_pool:
                error = "Delegate registration for {} already in the pool".format(
                    transaction.asset["delegate"]["username"]
                )
                return False, error

            return True, None
        error = "Invalidating transaction of unsupported type {}".format(
            transaction.type
        )
        return False, error

    def _validate_transaction(self, transaction, all_transactions):
        self._purge_expired()

        current_time = time.get_time()
        if transaction.timestamp > current_time + 3600:
            error = "Transaction {} is {} seconds in the future".format(
                transaction.timestamp - current_time
            )
            return False, error

        if transaction.network and transaction.network != config.network["pubKeyHash"]:
            error = "Transaction network {} does not match chain network {}".format(
                transaction.network, config.network["pubKeyHash"]
            )
            return False, error

        is_valid, errors = self._validate_transaction_by_type(
            transaction, all_transactions
        )
        return is_valid, errors

    def process_transactions(self, transactions_data):
        errors = defaultdict(list)
        excess = []
        transactions = []
        for transaction_data in transactions_data:

            # NOTE: This check should really check if transaction is not bigger than
            # maximum BYTES and not characters, but the implementation in core is wrong
            # and we need to be consistent with their implementation. Also this should
            # probably be checked after the payload is converted to CryptoTransaction
            json_transaction = len(json.dumps(transaction_data))
            if json_transaction > config.pool.max_transaction_characters:
                errors[transaction_data["id"]].append(
                    "Transaction {} is larger than {} characters".format(
                        transaction_data["id"],
                        config.pool["max_transaction_characters"],
                    )
                )
                continue

            transactions.append(CryptoTransaction.from_dict(transaction_data))

        for transaction in transactions:
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
            elif self.has_exceeded_max_transactions(transaction.sender_public_key):
                excess.append(transaction.id)
            else:
                is_valid, validation_errors = self._validate_transaction(transaction, transactions)

                if is_valid:
                    if transaction.verify():



                else:
                    errors.extend(validation_errors)
