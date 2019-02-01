from peewee import (
    BigIntegerField,
    BlobField,
    CharField,
    ForeignKeyField,
    IntegerField,
    Model,
    SmallIntegerField,
)

from .block import Block
from .wallet import Wallet


class Transaction(Model):
    id = CharField(max_length=64, primary_key=True)
    version = SmallIntegerField()
    block_id = ForeignKeyField(Block)
    sequence = SmallIntegerField()
    timestamp = IntegerField(index=True)
    sender_public_key = CharField(max_length=66, index=True)
    recipient_id = ForeignKeyField(Wallet)
    type = SmallIntegerField()
    vendor_field_hex = BlobField(null=True)
    amount = BigIntegerField()
    fee = BigIntegerField()
    serialized = BlobField()

    class Meta:
        table_name = 'transactions'
        indexes = (
            (
                ('sender_public_key', 'recipient_id', 'vendor_field_hex', 'timestamp'),
                False,
            ),
        )
