from peewee import BigIntegerField, CharField, Model

# TODO: This is potentially useless? Need to understand more about what this is used for.
class Wallet(Model):
    address = CharField(max_length=36, primary_key=True)
    public_key = CharField(max_length=66, unique=True)
    second_public_key = CharField(max_length=66, null=True, unique=True)
    vote = CharField(max_length=66, null=True)
    username = CharField(max_length=64, null=True, unique=True)
    balance = BigIntegerField()
    vote_balance = BigIntegerField()
    produced_blocks = BigIntegerField()
    missed_blocks = BigIntegerField()

    class Meta:
        table_name = "wallets"
        indexes = ((("public_key", "vote"), True),)
