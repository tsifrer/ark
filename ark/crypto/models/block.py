from binascii import hexlify, unhexlify
from binary.unsigned_integer import write_bit32, write_bit8, write_bit64
# import avocato


# class Block(avocato.Serializer):
#     id = avocato.StrField(null=True)
#     id_hex = avocato.StrField(null=True)

#     timestamp = avocato.IntField()
#     version = avocato.IntField()
#     height = avocato.IntField()
#     previous_block_hex = avocato.StrField(null=True)
#     previous_block = avocato.StrField()
#     number_of_transactions = avocato.IntField()
#     total_amount = avocato.DecimalField()
#     total_fee = avocato.DecimalField()
#     reward = avocato.DecimalField()
#     payload_length = avocato.IntField()
#     payload_hash = avocato.StrField()
#     generator_public_key = avocato.StrField()

#     block_signature = avocato.StrField(null=True)
#     # serialized = avocato.StrField(null=True)
#     # transactions = 


class Block(object):
    # field name, required
    fields = [
        ('id', False,),
        ('id_hex', False,),
        ('timestamp', True,),
        ('version', True,),
        ('height', True,),
        ('previous_block_hex', False,),
        ('previous_block', True,),
        ('number_of_transactions', True,),
        ('total_amount', True,),
        ('total_fee', True,),
        ('reward', True,),
        ('payload_length', True,),
        ('payload_hash', True,),
        ('generator_public_key', True,),
        ('block_signature', False,),
        # 'serialized',
        # 'transactions',
    ]
    # id = avocato.StrField(null=True)
    # id_hex = avocato.StrField(null=True)

    # timestamp = avocato.IntField()
    # version = avocato.IntField()
    # height = avocato.IntField()
    # previous_block_hex = avocato.StrField(null=True)
    # previous_block = avocato.StrField()
    # number_of_transactions = avocato.IntField()
    # total_amount = avocato.DecimalField()
    # total_fee = avocato.DecimalField()
    # reward = avocato.DecimalField()
    # payload_length = avocato.IntField()
    # payload_hash = avocato.StrField()
    # generator_public_key = avocato.StrField()

    # block_signature = avocato.StrField(null=True)
    # serialized = avocato.StrField(null=True)
    # transactions = 

    def __init__(self, data):
        if isinstance(data, str):
            data = self.deserialize(data)

        for field, required in self.fields:
            value = data.get(field)
            if required and not value:
                raise Exception('Missing field {}'.format(field))  # TODO: change exception
            setattr(self, field, value)

    # def _deserialize_header():

    # def deserialize(serialized_hex, header_only=False):
    #     unhexlify(serialized_hex)

    @staticmethod
    def to_bytes_hex(value):
        """Converts integer value to hex representation
        Automatically adds leading zeros if hex number is shorter than 16 characters.
        """
        hex_num = ''
        if value is not None:
            hex_num = format(value, 'x')
        return '{}{}'.format('0' * (16 - len(hex_num)), hex_num)


    def serialize(self, include_signature=True):
        self.previous_block_hex = Block.to_bytes_hex(self.previous_block)

        bytes_data = bytes(512)# maybe just bytes()?
        bytes_data += write_bit32(self.version)
        bytes_data += write_bit32(self.timestamp)
        bytes_data += write_bit32(self.height)
        bytes_data += self.previous_block_hex
        bytes_data += write_bit32(self.number_of_transactions)
        bytes_data += write_bit64(self.total_amount)
        bytes_data += write_bit64(self.total_fee)
        bytes_data += write_bit64(self.reward)
        bytes_data += write_bit32(self.payload_length)
        bytes_data += self.payload_hash
        bytes_data += self.generator_public_key

        if self.block_signature:
            bytes_data += self.block_signature

        return hexlify(bytes_data).decode()





















