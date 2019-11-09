from peewee import BigIntegerField, CharField, IntegerField, Model, SmallIntegerField

from playhouse.postgres_ext import JSONField

from chain.common.config import config


class PoolTransaction(Model):
    id = CharField(max_length=64, primary_key=True)
    version = SmallIntegerField()
    sequence = SmallIntegerField()
    timestamp = IntegerField(index=True)
    sender_public_key = CharField(max_length=66, index=True)
    recipient_id = CharField(max_length=66, null=True, index=True)
    type = SmallIntegerField()
    vendor_field = CharField(max_length=255, null=True)
    amount = BigIntegerField()
    fee = BigIntegerField()
    asset = JSONField(null=True)
    expires_at = IntegerField(index=True)

    class Meta:
        table_name = "pool_transactions"

    @classmethod
    def from_crypto(cls, transaction):
        # TODO: figure out how to improve this
        model = cls()
        model.id = transaction.id
        model.version = transaction.version
        model.sequence = transaction.sequence
        model.timestamp = transaction.timestamp
        model.sender_public_key = transaction.sender_public_key
        model.recipient_id = transaction.recipient_id
        model.type = transaction.type
        model.vendor_field = transaction.vendor_field
        model.amount = transaction.amount
        model.fee = transaction.fee
        model.asset = transaction.asset
        model.expires_at = transaction.calculate_expires_at(
            config.pool["max_transaction_age"]
        )
        return model
