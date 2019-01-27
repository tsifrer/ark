from peewee import BigIntegerField, CharField, IntegerField, Model, SmallIntegerField



class Block(Model):
    id = CharField(max_length=64, primary_key=True)
    version = SmallIntegerField()
    timestamp = IntegerField(unique=True)
    previous_block = CharField(max_length=64, null=True, unique=True)
    height = IntegerField(unique=True)
    number_of_transactions = IntegerField()
    total_amount = BigIntegerField()
    total_fee = BigIntegerField()
    reward = BigIntegerField()
    payload_length = IntegerField()
    payload_hash = CharField(max_length=64)
    generator_public_key = CharField(max_length=66, index=True)
    block_signature = CharField(max_length=256)

    class Meta:
        table_name = 'blocks'
