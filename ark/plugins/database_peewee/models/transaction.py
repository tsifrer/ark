from peewee import (
    BigIntegerField,
    BlobField,
    CharField,
    ForeignKeyField,
    IntegerField,
    Model,
    SmallIntegerField,
    fn,
)

from .block import Block


class Transaction(Model):
    id = CharField(max_length=64, primary_key=True)
    version = SmallIntegerField()
    block_id = ForeignKeyField(Block)
    sequence = SmallIntegerField()
    timestamp = IntegerField(index=True)
    sender_public_key = CharField(max_length=66, index=True)
    recipient_id = CharField(max_length=66, null=True, index=True)
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
        model.serialized = transaction.serialize()
        return model

    @staticmethod
    def statistics():
        """Returns statistics about Blocks table
        """
        stats = Transaction.select(
            fn.COUNT(Transaction.id),
            fn.SUM(Transaction.fee),
            fn.SUM(Transaction.amount),
        ).scalar(as_tuple=True)

        return {
            'transactions_count': stats[0],
            'total_fee': stats[1],
            'total_amount': stats[2],
        }
