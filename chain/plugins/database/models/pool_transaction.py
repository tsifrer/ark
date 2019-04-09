from peewee import IntegerField

from .transaction import Transaction


class PoolTransaction(Transaction):
    """
    NOTE: Inherits all fields from Transaction model
    """
    expires_at = IntegerField(index=True)

    class Meta:
        table_name = "pool_transactions"
