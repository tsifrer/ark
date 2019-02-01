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

    @classmethod
    def from_crypto(cls, block):
        # TODO: figure out how to improve this
        model = cls()
        model.id = block.id
        model.version = block.version
        model.timestamp = block.timestamp
        model.previous_block = block.previous_block
        model.height = block.height
        model.number_of_transactions = block.number_of_transactions
        model.total_amount = block.total_amount
        model.total_fee = block.total_fee
        model.reward = block.reward
        model.payload_length = block.payload_length
        model.payload_hash = block.payload_hash
        model.generator_public_key = block.generator_public_key
        model.block_signature = block.block_signature
        return model
