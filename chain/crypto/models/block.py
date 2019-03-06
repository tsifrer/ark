from binascii import hexlify, unhexlify
from hashlib import sha256

from binary.unsigned_integer import read_bit32, read_bit64, write_bit32, write_bit64

from chain.crypto.models.transaction import Transaction


from chain.config import Config

from chain.crypto.utils import verify_hash
from chain.crypto import slots, time


class Block(object):
    # TODO: make this mapping better
    # field name, json field name, required, default, to_type
    fields = [
        ('id', 'id', False, None, int),
        ('id_hex', 'idHex', False, None, None),
        ('timestamp', 'timestamp', True, None, None),
        ('version', 'version', True, None, None),
        ('height', 'height', True, None, None),
        ('previous_block_hex', 'previousBlockHex', False, None, None),
        ('previous_block', 'previousBlock', False, None, int),
        ('number_of_transactions', 'numberOfTransactions', True, None, None),
        ('total_amount', 'totalAmount', True, 0, int),
        ('total_fee', 'totalFee', True, 0, int),
        ('reward', 'reward', True, 0, int),
        ('payload_length', 'payloadLength', True, None, None),
        ('payload_hash', 'payloadHash', True, None, None),
        ('generator_public_key', 'generatorPublicKey', True, None, None),
        ('block_signature', 'blockSignature', False, None, None),
        ('transactions', 'transactions', False, [], None),
    ]

    def __init__(self, data):
        if isinstance(data, (str, bytes)):
            self.deserialize(data)
        else:
            for field, json_field, required, default, to_type in self.fields:
                # If data is passed in as dict, expect camelcase fields,
                # otherwise expect snakecase fields
                if isinstance(data, dict):
                    value = data.get(json_field, default)
                else:
                    value = getattr(data, field, default)
                if value is not None and to_type:
                    value = to_type(value)
                if required and value is None:
                    raise Exception(
                        'Missing field {}'.format(field)
                    )  # TODO: change exception
                setattr(self, field, value)
            self._set_id()
            if self.transactions:
                transactions = []
                for transaction_data in self.transactions:
                    transactions.append(Transaction(transaction_data))
                self.transactions = transactions

        if self.transactions:
            transactions = []
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
        # if (
        #     this.transactions &&
        #     this.data.numberOfTransactions === 2 &&
        #     (this.data.height === 3084276 || this.data.height === 34420)
        # ) {
        #     const temp = this.transactions[0];
        #     this.transactions[0] = this.transactions[1];
        #     this.transactions[1] = temp;
        # }

        # print('IIIIDDD', self.id)
        # print(self.id_hex)

        # TODO: implement other stuffz
        # TODO: figure out these things how they should work and implement them

    def _set_id(self):
        if self.height == 1:
            # For genesis blocks, we should not recalculate the id as it is, or all
            # the current ID's are calculated wrong.
            # The comment from the core above this "fix" describes the problem
            # perfectly:
            # "// TODO genesis block calculated id is wrong for some reason"
            self.id_hex = Block.to_bytes_hex(self.id)
        else:
            self.id_hex = self.get_id_hex()
            self.id = self.get_id()

    @staticmethod
    def to_bytes_hex(value):
        """Converts integer value to hex representation
        Automatically adds leading zeros if hex number is shorter than 16 characters.
        """
        hex_num = ''
        if value is not None:
            hex_num = format(int(value), 'x')
        return ('{}{}'.format('0' * (16 - len(hex_num)), hex_num)).encode('utf-8')

    def get_id_hex(self):
        payload_hash = unhexlify(self.serialize())
        full_hash = sha256(payload_hash).digest()
        small_hash = full_hash[:8][::-1]
        return hexlify(small_hash).decode()

    def get_id(self):
        id_hex = self.get_id_hex()
        return int(id_hex, 16)

    def get_header(self):
        fields = [
            'id',
            'id_hex',
            'timestamp',
            'version',
            'height',
            'previous_block_hex',
            'previous_block',
            'number_of_transactions',
            'total_amount',
            'total_fee',
            'reward',
            'payload_length',
            'payload_hash',
            'generator_public_key',
            'block_signature',
        ]
        data = {}
        for field in fields:
            value = getattr(self, field)
            if isinstance(value, int):
                value = str(value)
            if isinstance(value, bytes):
                value = value.decode()
            data[field] = value
        return data

    def serialize(self, include_signature=True):
        # TODO: make this a serializer that correctly converts input and checks that
        # it's correct on init
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
            # serialized_transaction = Transaction(transaction).serialize()
            serialized_transaction = transaction.serialize()
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
            serialized_hex = hexlify(bytes_data[start : start + trans_len])
            self.transactions.append(Transaction(serialized_hex))
            start += trans_len

    def deserialize(self, serialized_hex, header_only=False):
        bytes_data = unhexlify(serialized_hex)

        self.version = read_bit32(bytes_data)
        self.timestamp = read_bit32(bytes_data, offset=4)
        self.height = read_bit32(bytes_data, offset=8)
        self.previous_block_hex = hexlify(bytes_data[12 : 8 + 12]).decode()

        self.previous_block = int(self.previous_block_hex, 16)
        self.number_of_transactions = read_bit32(bytes_data, offset=20)
        self.total_amount = read_bit64(bytes_data, offset=24)
        self.total_fee = read_bit64(bytes_data, offset=32)
        self.reward = read_bit64(bytes_data, offset=40)
        self.payload_length = read_bit32(bytes_data, offset=48)
        self.payload_hash = hexlify(bytes_data[52 : 32 + 52]).decode()
        self.generator_public_key = hexlify(bytes_data[84 : 33 + 84]).decode()
        # TODO: test the case where block signature is not present
        signature_len = int(hexlify(bytes_data[118:119]), 16)
        signature_to = signature_len + 2 + 117
        self.block_signature = hexlify(bytes_data[117:signature_to]).decode()

        remaining_bytes = bytes_data[signature_to:]
        header_only = header_only or len(remaining_bytes) == 0
        self.transactions = []
        if not header_only:
            self._deserialize_transactions(remaining_bytes)

        self._set_id()
        # self.id_hex = self.get_id_hex()
        # self.id = self.get_id()
        # TODO: implement edge cases (outlookTable thingy) where some block ids are broken

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
