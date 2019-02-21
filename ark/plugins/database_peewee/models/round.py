from peewee import AutoField, BigIntegerField, CharField, Model


class Round(Model):
    id = AutoField(primary_key=True)
    public_key = CharField(max_length=66)
    balance = BigIntegerField()  # This is wallet.vote_balance
    round = BigIntegerField()

    class Meta:
        table_name = 'rounds'
        indexes = ((('round', 'public_key'), True),)
