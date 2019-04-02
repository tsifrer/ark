"""Peewee migrations -- 001_initial.py.
"""

import peewee as pw

SQL = pw.SQL


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    @migrator.create_model
    class Block(pw.Model):
        id = pw.CharField(max_length=64, primary_key=True)
        version = pw.SmallIntegerField()
        timestamp = pw.IntegerField(unique=True)
        previous_block = pw.CharField(max_length=64, null=True, unique=True)
        height = pw.IntegerField(unique=True)
        number_of_transactions = pw.IntegerField()
        total_amount = pw.BigIntegerField()
        total_fee = pw.BigIntegerField()
        reward = pw.BigIntegerField()
        payload_length = pw.IntegerField()
        payload_hash = pw.CharField(max_length=64)
        generator_public_key = pw.CharField(index=True, max_length=66)
        block_signature = pw.CharField(max_length=256)

        class Meta:
            table_name = "blocks"

    @migrator.create_model
    class Round(pw.Model):
        id = pw.AutoField()
        public_key = pw.CharField(max_length=66)
        balance = pw.BigIntegerField()
        round = pw.BigIntegerField()

        class Meta:
            table_name = "rounds"
            indexes = [(("round", "public_key"), True)]

    @migrator.create_model
    class Transaction(pw.Model):
        id = pw.CharField(max_length=64, primary_key=True)
        version = pw.SmallIntegerField()
        block_id = pw.ForeignKeyField(
            backref="transaction_set",
            column_name="block_id",
            field="id",
            model=migrator.orm["blocks"],
        )
        sequence = pw.SmallIntegerField()
        timestamp = pw.IntegerField(index=True)
        sender_public_key = pw.CharField(index=True, max_length=66)
        recipient_id = pw.CharField(index=True, max_length=66, null=True)
        type = pw.SmallIntegerField()
        vendor_field_hex = pw.BlobField(null=True)
        amount = pw.BigIntegerField()
        fee = pw.BigIntegerField()
        serialized = pw.BlobField()

        class Meta:
            table_name = "transactions"
            indexes = [
                (
                    (
                        "sender_public_key",
                        "recipient_id",
                        "vendor_field_hex",
                        "timestamp",
                    ),
                    False,
                )
            ]


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model("transactions")

    migrator.remove_model("rounds")

    migrator.remove_model("blocks")
