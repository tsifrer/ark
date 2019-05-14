import peewee as pw


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    migrator.remove_fields("pool_transactions", "block_id")
    migrator.remove_fields("pool_transactions", "serialized")


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.add_fields(
        "pool_transactions",
        block_id=pw.ForeignKeyField(
            backref="pooltransaction_set",
            column_name="block_id",
            field="id",
            model=migrator.orm["blocks"],
        ),
    )

    migrator.change_fields(
        "pool_transactions", vendor_field_hex=pw.BlobField(null=True)
    )
