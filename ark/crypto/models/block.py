from hashlib import sha256
from binascii import hexlify, unhexlify
from binary.unsigned_integer import (
    write_bit32, write_bit64, read_bit32, read_bit64
)

from ark.crypto.models.transaction import Transaction

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

    def __init__(self, data):
        if isinstance(data, (str, bytes,)):
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
        return ('{}{}'.format('0' * (16 - len(hex_num)), hex_num)).encode('utf-8')

    def get_id_hex(self):
        payload_hash = self.serialize()
        full_hash = sha256(unhexlify(payload_hash)).digest()
        small_hash = full_hash[:8][::-1]
        return hexlify(small_hash)

    def get_id(self):
        id_hex = self.get_id_hex()
        return int(id_hex, 16)

    def serialize(self, include_signature=True):
        # TODO: make this a serializer that correctly converts input and checks that it's correct
        # on init
        self.previous_block_hex = Block.to_bytes_hex(int(self.previous_block))

        bytes_data = bytes()
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
            transaction_lenghts.append(read_bit32(bytes_data, offset=x * 4))

        self.transactions = []
        start = 4 * self.number_of_transactions
        for trans_len in transaction_lenghts:
            serialized_hex = hexlify(bytes_data[start:start+trans_len])
            self.transactions.append(Transaction(serialized_hex))
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
        header_only = header_only or len(remaining_bytes) == 0
        if not header_only:
            self._deserialize_transactions(remaining_bytes)

        self.id_hex = self.get_id_hex()
        self.id = self.get_id()
        # TODO: implement edge cases (outlookTable thingy) where some block ids are broken
