"""Peewee migrations -- 003_added_pool_transaction.py.
"""
import peewee as pw

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass


def migrate(migrator, database, fake=False, **kwargs):
    @migrator.create_model
    class PoolTransaction(pw.Model):
        id = pw.CharField(max_length=64, primary_key=True)
        version = pw.SmallIntegerField()
        block_id = pw.ForeignKeyField(
            backref="pooltransaction_set",
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
        asset = pw_pext.JSONField(null=True)
        expires_at = pw.IntegerField(index=True)

        class Meta:
            table_name = "pool_transactions"
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

    migrator.remove_model("pool_transactions")
