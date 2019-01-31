from hashlib import sha256
from binascii import hexlify, unhexlify
from binary.unsigned_integer import (
    write_bit32, write_bit8, write_bit64, read_bit32, read_bit64, read_bit8
)
# import avocato

from ark.crypto.models.transaction import Transaction
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
    # field name, json field name, required
    fields = [
        ('id', 'id', False,),
        ('id_hex', 'idHex', False,),
        ('timestamp', 'timestamp', True,),
        ('version', 'version', True,),
        ('height', 'height', True,),
        ('previous_block_hex', 'previousBlockHex', False,),
        ('previous_block', 'previousBlock', False,),
        ('number_of_transactions', 'numberOfTransactions', True,),
        ('total_amount', 'totalAmount', True,),
        ('total_fee', 'totalFee', True,),
        ('reward', 'reward', True,),
        ('payload_length', 'payloadLength', True,),
        ('payload_hash', 'payloadHash', True,),
        ('generator_public_key', 'generatorPublicKey', True,),
        ('block_signature', 'blockSignature', False,),
        # 'serialized',
        ('transactions', 'transactions', False,),
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
        if isinstance(data, (str, bytes,)):
            print('DESERIALZIING')
            self.deserialize(data)
        else:
            for field, json_field, required in self.fields:
                value = data.get(json_field)
                if required and value is None:
                    raise Exception('Missing field {}'.format(field))  # TODO: change exception
                setattr(self, field, value)


    @staticmethod
    def to_bytes_hex(value):
        """Converts integer value to hex representation
        Automatically adds leading zeros if hex number is shorter than 16 characters.
        """
        hex_num = ''
        if value is not None:
            hex_num = format(value, 'x')
        return '{}{}'.format('0' * (16 - len(hex_num)), hex_num)

    
    def get_id_hex(self):
        payload_hash = self.serialize()
        full_hash = sha256(payload_hash.encode('utf-8')).hexdigest()
        print(full_hash)
        # take first 8 characters and reverse them
        small_hash = full_hash[:8][::-1]
        # small_hash = ''
        # for x in range(8):
        #     small_hash += full_hash[7-x]
        # print(small_hash)
        print(small_hash)
        print(hexlify(small_hash.encode()))
        return small_hash

    def get_id(self):
        id_hex = self.get_id_hex()
        return int(hexlify(id_hex.encode()), 16)




    def serialize(self, include_signature=True):
        # TODO: make this a serializer that correctly converts input and checks that it's correct
        # on init
        self.previous_block_hex = Block.to_bytes_hex(int(self.previous_block))

        bytes_data = bytes()# bytes() or bytes(512)?
        bytes_data += write_bit32(self.version)
        bytes_data += write_bit32(self.timestamp)
        bytes_data += write_bit32(self.height)
        bytes_data += unhexlify(self.previous_block_hex)
        bytes_data += write_bit32(self.number_of_transactions)
        bytes_data += write_bit64(int(self.total_amount))
        bytes_data += write_bit64(int(self.total_fee))
        bytes_data += write_bit64(int(self.reward))
        bytes_data += write_bit32(self.payload_length)
        bytes_data += unhexlify(self.payload_hash)
        bytes_data += unhexlify(self.generator_public_key)

        if include_signature and self.block_signature:
            bytes_data += unhexlify(self.block_signature)

        return hexlify(bytes_data).decode()

    def serialize_full(self):
        # TODO: try to make these as default values instead of checking for it here
        if not self.transactions:
            self.transactions = []
        if not self.number_of_transactions:
            self.number_of_transactions = len(self.transactions)

        bytes_data = unhexlify(self.serialize())

        all_transaction_bytes = bytes()
        for transaction in self.transactions:
            serialized_transaction = Transaction(transaction).serialize()
            bytes_data += write_bit32(len(unhexlify(serialized_transaction)))
            all_transaction_bytes += unhexlify(serialized_transaction)

        bytes_data += all_transaction_bytes
        return hexlify(bytes_data).decode()



    def _deserialize_transactions(self, bytes_data):
        transaction_lenghts = []
        for x in range(self.number_of_transactions):
            #TODO: make this with offset
            transaction_lenghts.append(read_bit32(bytes_data[x * 4:(x+1) * 4]))

        self.transactions = []
        start = 4 * self.number_of_transactions
        for trans_len in transaction_lenghts:
            serialized_hex = hexlify(bytes_data[start:start+trans_len])
            # print(serialized_hex)
            self.transactions.append(Transaction(serialized_hex))# TODO
            start += trans_len
            




    def deserialize(self, serialized_hex, header_only=False):
        bytes_data = unhexlify(serialized_hex)

        self.version = read_bit32(bytes_data)
        self.timestamp = read_bit32(bytes_data, offset=4)
        self.height = read_bit32(bytes_data, offset=8)
        self.previous_block_hex = hexlify(bytes_data[12:8 + 12])

        self.previous_block = int(self.previous_block_hex, 16)
        self.number_of_transactions = read_bit32(bytes_data, offset=20)
        self.total_amount = read_bit64(bytes_data, offset=24)
        self.total_fee = read_bit64(bytes_data, offset=32)
        self.reward = read_bit64(bytes_data, offset=40)
        self.payload_length = read_bit32(bytes_data, offset=48)
        self.payload_hash = hexlify(bytes_data[52:32 + 52])
        self.generator_public_key = hexlify(bytes_data[84:33 + 84])
        # TODO: test the case where block signature is not present
        signature_len = int(hexlify(bytes_data[118:119]), 16)
        signature_to = signature_len + 2 + 117
        self.block_signature = hexlify(bytes_data[117:signature_to])

        remaining_bytes = bytes_data[signature_to:]
        # TODO: maybe If header_only = True, and there is no hex left to be processed, set header_only to
        # false, to avoid erroring
        # header_only = header_only or len(remaining_bytes) == 0
        if not header_only:
            self._deserialize_transactions(remaining_bytes)

        # TODO: implement deserialize completely, missing a couple of things still, like id, idhex and outlooktable
        # self.id_hex = self.get_id_hex()
        # self.id = self.get_id()




        # print(self.version)
        # print(self.timestamp)
        # print(self.previous_block_hex)
        # print(self.previous_block)
        # print(self.number_of_transactions)
        # print(self.total_amount)
        # print(self.total_fee)
        # print(self.reward)
        # print(self.payload_length)
        # print(self.payload_hash)
        # print(self.generator_public_key)
        # print(self.block_signature)
        # print(self.id_hex)
        # print(self.id)

        # self.previous_block_hex = 



















