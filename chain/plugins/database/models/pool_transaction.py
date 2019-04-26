from peewee import IntegerField

from chain.common.config import config

from .transaction import Transaction


class PoolTransaction(Transaction):
    """
    NOTE: Inherits all fields from Transaction model
    """

    expires_at = IntegerField(index=True)

    class Meta:
        table_name = "pool_transactions"

    @classmethod
    def from_crypto(cls, transaction):
        # TODO: figure out how to improve this
        model = cls()
        model.id = transaction.id
        model.version = transaction.version
        model.block_id = transaction.block_id
        model.sequence = transaction.sequence
        model.timestamp = transaction.timestamp
        model.sender_public_key = transaction.sender_public_key
        model.recipient_id = transaction.recipient_id
        model.type = transaction.type
        model.vendor_field_hex = transaction.vendor_field_hex
        model.amount = transaction.amount
        model.fee = transaction.fee
        model.asset = transaction.asset
        model.expires_at = transaction.calculate_expires_at(
            config.pool["max_transaction_age"]
        )
        # TODO: probably obsolete
        serialized = transaction.serialize()
        model.serialized = serialized
        return model
