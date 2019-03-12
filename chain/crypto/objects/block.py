from binascii import hexlify, unhexlify
from hashlib import sha256

from binary.unsigned_integer import read_bit32, read_bit64, write_bit32, write_bit64

from chain.config import Config
from chain.crypto import slots, time
from chain.crypto.models.transaction import Transaction
from chain.crypto.objects.base import CryptoField, CryptoObject
from chain.crypto.utils import verify_hash


class Block(CryptoObject):
    id = CryptoField(attr='id', required=False, default=None, field_type=int)
    id_hex = CryptoField(attr='idHex', required=False, default=None, field_type=bytes)
    timestamp = CryptoField(attr='timestamp', required=True, default=None, field_type=int)
    version = CryptoField(attr='version', required=True, default=None, field_type=int)
    height = CryptoField(attr='height', required=True, default=None, field_type=int)
    previous_block_hex = CryptoField(attr='previousBlockHex', required=False, default=None, field_type=bytes)
    previous_block = CryptoField(attr='previousBlock', required=False, default=None, field_type=int)
    number_of_transactions = CryptoField(attr='numberOfTransactions', required=True, default=None, field_type=int)
    total_amount = CryptoField(attr='totalAmount', required=True, default=None, field_type=int)
    total_fee = CryptoField(attr='totalFee', required=True, default=None, field_type=int)
    reward = CryptoField(attr='reward', required=True, default=None, field_type=int)
    payload_length = CryptoField(attr='payloadLength', required=True, default=None, field_type=int)
    payload_hash = CryptoField(attr='payloadHash', required=True, default=None, field_type=bytes)
    generator_public_key = CryptoField(attr='generatorPublicKey', required=True, default=None, field_type=str)
    block_signature = CryptoField(attr='blockSignature', required=False, default=None, field_type=bytes)
    transactions = CryptoField(attr='transaction', required=False, default=None, field_type=None)

    @staticmethod
    def to_bytes_hex(value):
        """Converts integer value to hex representation
        Automatically adds leading zeros if hex number is shorter than 16 characters.
        """
        hex_num = ''
        if value is not None:
            hex_num = format(int(value), 'x')
        return ('{}{}'.format('0' * (16 - len(hex_num)), hex_num)).encode('utf-8')

    def _set_id(self):
        if self.height == 1:
            # For genesis blocks, we don't recalculate the id as it is wrong.
            # The comment from the core code for this "fix" describes the problem
            # perfectly:
            # "// TODO genesis block calculated id is wrong for some reason"
            self.id_hex = Block.to_bytes_hex(self.id)
        else:
            self.id_hex = self.get_id_hex()
            self.id = self.get_id()

    def _construct_common(self):
        self._set_id()

        if self.transactions:
            for index, transaction in enumerate(self.transactions):
                # override blockId and timestamp so all transactions match
                # with the current block
                transaction.block_id = self.id
                # TODO: these next line breaks tests # THIS LOOKS LIKE IT'S A LIE
                # AS NOTHING WORKS CORRECTLY IF WE OVERRIDE TRANSACTION TIMESTAMP
                # WITH BLOCK TIMESTAMP
                # transaction.timestamp = self.timestamp
                # add sequence to keep the data in sequence when storing it to db
                transaction.sequence = index

            # // order of transactions messed up in mainnet V1
            # // TODO: move this to network constants exception using block ids
            if (self.number_of_transactions == 2 and (self.height == 3084276 or self.height == 34420)):
                self.transactions[0], self.transactions[1] = self.transactions[1], self.transactions[0]

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError('data must be dict')
        cls = cls()
        for field in cls._fields:
            value = data.get(field.attr, field.default)
            if field.type and value != field.default and not isinstance(value, field.type):
                raise TypeError('Attribute {} must be a {}'.format(field.attr, field.type))
            if field.required and value is field.default:
                raise Exception(
                    'Missing field {}'.format(field.name)
                )  # TODO: change exception
            setattr(cls, field.name, value)

        if cls.transactions and isinstance(cls.transaction, list):
            transactions = []
            for transaction_data in cls.transactions:
                transactions.append(Transaction(transaction_data))
            cls.transactions = transactions
        cls._construct_common()
        return cls

    @classmethod
    def from_object(cls, data):
        # if not isinstance(data, dict):
        #     raise TypeError('Data must be in dictionary format')
        cls = cls()
        for field in cls._fields:
            value = getattr(data, field.name, field.default)
            if field.type and value != field.default and not isinstance(value, field.type):
                raise TypeError('Attribute {} must be a {}'.format(field.attr, field.type))
            if field.required and value is field.default:
                raise Exception(
                    'Missing field {}'.format(field.name)
                )  # TODO: change exception
            setattr(cls, field.name, value)

        if cls.transactions:
            transactions = []
            for transaction_data in cls.transactions:
                transactions.append(Transaction(transaction_data))
            cls.transactions = transactions
        cls._construct_common()
        return cls

    @classmethod
    def from_serialized(cls, bytes_string):
        if not isinstance(bytes_string, bytes):
            raise TypeError('bytes_string must be bytes')
        cls = cls()
        cls.deserialize(bytes_string)
        cls._construct_common()
        return cls

    def get_id_hex(self):
        payload_hash = unhexlify(self.serialize())
        full_hash = sha256(payload_hash).digest()
        small_hash = full_hash[:8][::-1]
        return hexlify(small_hash)

    def get_id(self):
        id_hex = self.get_id_hex()
        return int(id_hex, 16)

    def get_header(self):
        fields = [
            ('id', str,),
            ('id_hex', None,),
            ('timestamp', None,),
            ('version', None,),
            ('height', None,),
            ('previous_block_hex', None,),
            ('previous_block', str,),
            ('number_of_transactions', None,),
            ('total_amount', str,),
            ('total_fee', str,),
            ('reward', str,),
            ('payload_length', None,),
            ('payload_hash', None,),
            ('generator_public_key', None,),
            ('block_signature', None,),
        ]
        data = {}
        for field, to_type in fields:
            value = getattr(self, field)
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            if to_type:
                value = to_type(value)
            data[field] = value
        return data

    def serialize(self, include_signature=True):
        self.previous_block_hex = Block.to_bytes_hex(self.previous_block)

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

        return hexlify(bytes_data)

    def serialize_full(self):
        # TODO: try to make these as default values instead of checking for it here
        if not self.transactions:
            self.transactions = []
        if not self.number_of_transactions:
            self.number_of_transactions = len(self.transactions)

        bytes_data = unhexlify(self.serialize())

        all_transaction_bytes = bytes()
        for transaction in self.transactions:
            # serialized_transaction = Transaction(transaction).serialize()
            serialized_transaction = transaction.serialize()
            bytes_data += write_bit32(len(unhexlify(serialized_transaction)))
            all_transaction_bytes += unhexlify(serialized_transaction)

        bytes_data += all_transaction_bytes
        return hexlify(bytes_data)

    def _deserialize_transactions(self, bytes_data):
        transaction_lenghts = []
        for x in range(self.number_of_transactions):
            transaction_lenghts.append(read_bit32(bytes_data, offset=x * 4))
        self.transactions = []
        start = 4 * self.number_of_transactions
        for trans_len in transaction_lenghts:
            serialized_hex = hexlify(bytes_data[start : start + trans_len])
            self.transactions.append(Transaction(serialized_hex))
            start += trans_len

    def deserialize(self, serialized_hex):
        bytes_data = unhexlify(serialized_hex)

        self.version = read_bit32(bytes_data)
        self.timestamp = read_bit32(bytes_data, offset=4)
        self.height = read_bit32(bytes_data, offset=8)
        self.previous_block_hex = hexlify(bytes_data[12 : 8 + 12]).decode('utf-8')

        self.previous_block = int(self.previous_block_hex, 16)
        self.number_of_transactions = read_bit32(bytes_data, offset=20)
        self.total_amount = read_bit64(bytes_data, offset=24)
        self.total_fee = read_bit64(bytes_data, offset=32)
        self.reward = read_bit64(bytes_data, offset=40)
        self.payload_length = read_bit32(bytes_data, offset=48)
        self.payload_hash = hexlify(bytes_data[52 : 32 + 52])
        self.generator_public_key = hexlify(bytes_data[84 : 33 + 84]).decode('utf-8')
        # TODO: test the case where block signature is not present
        signature_len = int(hexlify(bytes_data[118:119]), 16)
        signature_to = signature_len + 2 + 117
        self.block_signature = hexlify(bytes_data[117:signature_to])

        remaining_bytes = bytes_data[signature_to:]

        if len(remaining_bytes) != 0:
            self._deserialize_transactions(remaining_bytes)

        # TODO: implement edge cases (outlookTable thingy) where some block ids are broken
        # const { outlookTable } = configManager.config.exceptions;
        # if (outlookTable && outlookTable[block.id]) {
        #     block.id = outlookTable[block.id];
        #     block.idHex = Block.toBytesHex(block.id);
        # }

    def verify_signature(self):
        """Verify signature associated with this block
        """
        bytes_data = unhexlify(self.serialize(include_signature=False))
        is_verified = verify_hash(
            bytes_data, self.block_signature, self.generator_public_key
        )
        return is_verified

    def verify(self):
        errors = []
        print('VERIFYING')

        # TODO: find a better way to get milestone data
        config = Config()
        milestone = config.get_milestone(self.height)
        # Check that the previous block is set if it's not a genesis block
        if self.height > 1 and not self.previous_block:
            errors.append('Invalid previous block')

        # Chech that the block reward matches with the one specified in config
        if self.reward != milestone['reward']:
            errors.append(
                'Invalid block reward: {} expected: {}'.format(
                    self.reward, milestone['reward']
                )
            )

        # Verify block signature
        is_valid_signature = self.verify_signature()
        if not is_valid_signature:
            errors.append('Failed to verify block signature')

        # Check if version is correct on the block
        if self.version != milestone['block']['version']:
            errors.append('Invalid block version')

        # Check that the block timestamp is not in the future
        is_invalid_timestamp = slots.get_slot_number(
            self.height, self.timestamp
        ) > slots.get_slot_number(self.height, time.get_time())
        if is_invalid_timestamp:
            errors.append('Invalid block timestamp')

        # Check if all transactions are valid
        invalid_transactions = [
            trans for trans in self.transactions if not trans.verify()
        ]
        if len(invalid_transactions) > 0:
            errors.append('One or more transactions are not verified')

        # Check that number of transactions and block.number_of_transactions match
        if len(self.transactions) != self.number_of_transactions:
            errors.append('Invalid number of transactions')

        # Check that number of transactions is not too high (except for genesis block)
        if (
            self.height > 1
            and len(self.transactions) > milestone['block']['maxTransactions']
        ):
            errors.append('Too many transactions')

        # Check if transactions add u pto the block values
        applied_transactions = []
        total_amount = 0
        total_fee = 0
        bytes_data = bytes()
        for transaction in self.transactions:
            if transaction.id in applied_transactions:
                errors.append(
                    'Encountered duplicate transaction: {}'.format(transaction.id)
                )

            applied_transactions.append(transaction.id)
            total_amount += transaction.amount
            total_fee += transaction.fee
            bytes_data += unhexlify(transaction.id)

        if total_amount != self.total_amount:
            errors.append('Invalid total amount')

        if total_fee != self.total_fee:
            errors.append('Invalid total fee')

        if len(bytes_data) > milestone['block']['maxPayload']:
            errors.append('Payload is too large')

        if sha256(bytes_data).hexdigest() != self.payload_hash:
            errors.append('Invalid payload hash')

        return len(errors) == 0, errors
