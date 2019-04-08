"""Peewee migrations -- 002_added_transaction_asset.py.
"""
import peewee as pw

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    migrator.add_fields("transactions", asset=pw_pext.JSONField(null=True))


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_fields("transactions", "asset")
