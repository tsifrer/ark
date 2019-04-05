from peewee import CharField, IntegerField, Model

from .fields import BytesField


class PoolTransaction(Model):
    sequence = IntegerField(primary_key=True)
    id = CharField(max_length=64, unique=True)
    serialized = BytesField()
    expires_at = IntegerField(index=True)

    class Meta:
        table_name = "pool_transactions"
