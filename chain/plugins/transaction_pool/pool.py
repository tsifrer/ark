import json
import os

from redis import Redis

from chain.common.config import config
from chain.common.plugins import load_plugin
from chain.crypto import time
from chain.crypto.objects.transactions import from_dict, from_object
from chain.plugins.database.models.pool_transaction import PoolTransaction

from .fees import valid_fee_for_broadcast, valid_fee_for_pool
from .pool_wallet_manager import PoolWalletManager


class Pool(object):
    _blocked_key = "transaction_pool:blocked:{}"

    def __init__(self):
        super().__init__()

        # Load the database plugin to correctly setup PoolTransaction model and to
        # use it for getting the last block
        self.database = load_plugin("chain.plugins.database")

        self.redis = Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=os.environ.get("REDIS_PORT", 6379),
            db=os.environ.get("REDIS_DB", 0),
        )

        self.wallets = PoolWalletManager()

    def _purge_expired(self):
        current_time = time.get_time()
        expired_transactions = list(
            PoolTransaction.select().where(PoolTransaction.expires_at <= current_time)
        )

        ids = []
        for trans in expired_transactions:
            transaction = from_object(trans)
            sender_wallet = self.find_by_public_key(transaction.sender_public_key)
            transaction.revert_for_sender_wallet(sender_wallet)
            ids.append(transaction.id)

        delete_query = PoolTransaction.delete().where(PoolTransaction.id.in_(ids))
        delete_query.execute()

    def build_wallets(self):
        self.wallets.clear_wallets()
        self._purge_expired()
        last_block = self.database.get_last_block()
        for trans in PoolTransaction.select():
            transaction = from_object(trans)
            sender_wallet = self.wallets.find_by_public_key(
                transaction.sender_public_key
            )
            if transaction.can_be_applied_to_wallet(
                sender_wallet, self.walelts, self, last_block.height
            ):
                transaction.apply_to_sender_wallet(sender_wallet)
                self.wallets.save_wallet(sender_wallet)
            else:
                print(
                    "Transaction {} can't be applied to wallet {}".format(
                        transaction.id, sender_wallet.address
                    )
                )
                self._purge_sender(transaction.sender_public_key)

        print("Transaction pool wallets have been successfully built")

    def _purge_sender(self, sender_public_key):
        print("Purging sender {} from pool wallet manager")

        PoolTransaction.delete().where(
            PoolTransaction.sender_public_key == sender_public_key
        ).execute()

        self.wallets.delete_by_public_key(sender_public_key)

    def transaction_exists(self, transaction_id):
        query = PoolTransaction.select().where(PoolTransaction.id == transaction_id)
        return query.exists()

    def remove_transaction_by_id(self, transaction_id):
        query = PoolTransaction.delete().where(PoolTransaction.id == transaction_id)
        query.execute()

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

    def has_sender_exceeded_max_transactions(self, sender_public_key):
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

    def sender_has_transactions_of_type(self, transaction):
        query = PoolTransaction.select().where(
            PoolTransaction.sender_public_key == transaction.sender_public_key,
            PoolTransaction.type == transaction.type,
        )
        return query.exists()

    def sender_has_any_transactions(self, sender_public_key):
        query = PoolTransaction.select().where(
            PoolTransaction.sender_public_key == sender_public_key
        )
        return query.exists()

    def _validate_transaction(self, transaction, block_height, transactions):
        if self.database.transaction_is_forged(transaction.id):
            return "Transaction {} already forged".format(transaction.id)

        if self.transaction_exists(transaction.id):
            return "Transaction {} already exists".format(transaction.id)

        if self.is_sender_blocked(transaction.sender_public_key):
            return "Transaction {} rejected. Sender {} is blocked.".format(
                transaction.id, transaction.sender_public_key
            )

        current_time = time.get_time()
        if transaction.timestamp > current_time + 3600:
            error = "Transaction {} is {} seconds in the future".format(
                transaction.timestamp - current_time
            )
            return error

        if transaction.network and transaction.network != config.network["pubKeyHash"]:
            error = "Transaction network {} does not match chain network {}".format(
                transaction.network, config.network["pubKeyHash"]
            )
            return error

        pool_error = transaction.validate_for_transaction_pool(self, transactions)
        if pool_error:
            return pool_error

        if not transaction.verify():
            return "Transaction {} didn't pass verification process".format(
                transaction.id
            )

    def process_transactions(self, transactions_data):
        self._purge_expired()

        errors = {}
        excess = []
        accepted = []
        broadcasted = []
        transactions = []

        last_block = self.database.get_last_block()

        # TODO: Transaction sequence is currently growing until transaction pool is
        # completely empty
        last_transaction_sequence = (
            PoolTransaction.select(PoolTransaction.sequence)
            .order_by(PoolTransaction.sequence.desc())
            .first()
        )
        sequence = 0
        if last_transaction_sequence:
            sequence = last_transaction_sequence.sequence

        for transaction_data in transactions_data:

            # NOTE: This check should really check if transaction is not bigger than
            # maximum BYTES and not characters, but the implementation in core is wrong
            # and we need to be consistent with their implementation. Also this should
            # probably be checked after the payload is converted to CryptoTransaction
            json_transaction = len(json.dumps(transaction_data))
            if json_transaction > config.pool["max_transaction_characters"]:
                errors[
                    transaction_data["id"]
                ] = "Transaction {} is larger than {} characters".format(
                    transaction_data["id"], config.pool["max_transaction_characters"]
                )
                continue
            transaction = from_dict(transaction_data)
            sequence += 1
            transaction.sequence = sequence
            transactions.append(transaction)

        for transaction in transactions:
            if self.has_sender_exceeded_max_transactions(transaction.sender_public_key):
                excess.append(transaction.id)
                continue

            validation_error = self._validate_transaction(
                transaction, last_block.height, transactions
            )
            if validation_error:
                errors[transaction.id] = validation_error
                continue

            if not self.wallets.can_apply_to_sender(transaction, last_block.height):
                errors[
                    transaction.id
                ] = "Transaction {} can't be applied to senders wallet".format(
                    transaction.id
                )
                continue

            valid_for_pool = valid_fee_for_pool(transaction, last_block.height)
            valid_for_broadcast = valid_fee_for_broadcast(
                transaction, last_block.height
            )

            if not valid_for_broadcast and not valid_for_pool:
                errors[
                    transaction.id
                ] = "Fee is too low to broadcast and accept the transaction {}".format(
                    transaction.id
                )
                continue

            if valid_for_pool:
                count = PoolTransaction.select().count()
                if count > config.pool["max_transactions_in_pool"]:
                    lowest_pool = (
                        PoolTransaction.select(PoolTransaction.fee)
                        .order_by(PoolTransaction.fee.asc())
                        .first()
                    )
                    lowest = from_object(lowest_pool)
                    if lowest.fee < transaction.fee:
                        lowest_sender = self.wallets.find_by_public_key(
                            lowest.sender_public_key
                        )
                        lowest.revert_for_sender_wallet(lowest_sender)
                        self.wallets.save_wallet(lowest_sender)
                        lowest_pool.delete_instance()
                    else:
                        errors[transaction.id] = (
                            "Pool is full (has {} transactions) and this transaction's "
                            "fee {} is not higher than the lowest fee already in the "
                            "pool {}".format(count, transaction.fee, lowest_pool.fee)
                        )
                        continue

                # Add transaction to the pool
                sender_wallet = self.wallets.find_by_public_key(
                    transaction.sender_public_key
                )
                transaction.apply_to_sender_wallet(sender_wallet)
                self.wallets.save_wallet(sender_wallet)
                pool_transaction = PoolTransaction.from_crypto(transaction)
                pool_transaction.save()
                accepted.append(transaction.id)

            if valid_for_broadcast:
                broadcasted.append(transaction.id)
                # TODO:
                # if (result.broadcast.length > 0) {
                #     app.resolvePlugin<P2P.IMonitor>("p2p").broadcastTransactions
                # (guard.getBroadcastTransactions());
                # }

        return {
            "accepted": accepted,
            "broadcasted": broadcasted,
            "excess": excess,
            "errors": errors,
            "invalid": list(errors.keys()),
        }

    def accept_chained_block(self, block):
        """Processes recently accepted block by the blockchain.
        Removes block transactions from the pool and adjusts pool wallets for non
        existing transactions.

        :param Block block: Accepted block object
        """
        for transaction in block.transactions:

            if self.wallets.exists_by_address(transaction.recipient_id):
                recipient_wallet = self.wallets.find_by_address(
                    transaction.recipient_id
                )
                transaction.apply_to_recipient_wallet(recipient_wallet)
                self.wallets.save_wallet(recipient_wallet)

            sender_wallet = None
            if self.wallets.exists_by_public_key(transaction.sender_public_key):
                sender_wallet = self.wallets.find_by_public_key(
                    transaction.sender_public_key
                )

            if self.transaction_exists(transaction.id):
                self.remove_transaction_by_id(transaction.id)
            elif sender_wallet:
                if transaction.can_be_applied_to_wallet(
                    sender_wallet, self.wallets, block.height
                ):
                    transaction.apply_to_sender_wallet(sender_wallet)
                    self.wallets.save_wallet(sender_wallet)
                else:
                    self._purge_sender(transaction.sender_public_key)
                    self.block_sender(transaction.sender_public_key)

            if (
                sender_wallet
                and sender_wallet.can_be_purged()
                and not self.sender_has_any_transactions(transaction.sender_public_key)
            ):
                self.wallets.delete_by_public_key(sender_wallet.public_key)

        # If delegate is in pool wallet manager apply rewards and fees
        if self.wallets.exists_by_public_key(block.generator_public_key):
            delegate_wallet = self.wallets.find_by_public_key(
                block.generator_public_key
            )
            total = block.reward + block.total_fee
            delegate_wallet.balance += total
            self.wallets.save_wallet(delegate_wallet)
