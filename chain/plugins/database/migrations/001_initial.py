"""Peewee migrations -- 001_initial.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import datetime as dt
import peewee as pw

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

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
            indexes = [(('round', 'public_key'), True)]

    @migrator.create_model
    class Transaction(pw.Model):
        id = pw.CharField(max_length=64, primary_key=True)
        version = pw.SmallIntegerField()
        block_id = pw.ForeignKeyField(
            backref='transaction_set',
            column_name='block_id',
            field='id',
            model=migrator.orm['blocks'],
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
                        'sender_public_key',
                        'recipient_id',
                        'vendor_field_hex',
                        'timestamp',
                    ),
                    False,
                )
            ]

    @migrator.create_model
    class Wallet(pw.Model):
        address = pw.CharField(max_length=36, primary_key=True)
        public_key = pw.CharField(max_length=66, unique=True)
        second_public_key = pw.CharField(max_length=66, null=True, unique=True)
        vote = pw.CharField(max_length=66, null=True)
        username = pw.CharField(max_length=64, null=True, unique=True)
        balance = pw.BigIntegerField()
        vote_balance = pw.BigIntegerField()
        produced_blocks = pw.BigIntegerField()
        missed_blocks = pw.BigIntegerField()

        class Meta:
            table_name = "wallets"
            indexes = [(('public_key', 'vote'), True)]


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('wallets')

    migrator.remove_model('transactions')

    migrator.remove_model('rounds')

    migrator.remove_model('blocks')
