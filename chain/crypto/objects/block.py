from binascii import hexlify, unhexlify
from hashlib import sha256

from binary.unsigned_integer import write_bit32, write_bit64

from chain.config import Config
from chain.crypto import slots, time
from chain.crypto.bytebuffer import ByteBuffer
from chain.crypto.objects.base import (
    BigIntField,
    BytesField,
    CryptoObject,
    Field,
    IntField,
    StrField,
)
from chain.crypto.objects.transaction import Transaction
from chain.crypto.utils import verify_hash


class Block(CryptoObject):
    id = StrField(attr="id", required=False, default=None)
    id_hex = BytesField(attr="idHex", required=False, default=None)
    timestamp = IntField(attr="timestamp", required=True, default=None)
    version = IntField(attr="version", required=True, default=None)
    height = IntField(attr="height", required=True, default=None)
    previous_block_hex = BytesField(
        attr="previousBlockHex", required=False, default=None
    )
    previous_block = StrField(attr="previousBlock", required=False, default=None)
    number_of_transactions = IntField(
        attr="numberOfTransactions", required=True, default=0
    )
    total_amount = BigIntField(attr="totalAmount", required=True, default=0)
    total_fee = BigIntField(attr="totalFee", required=True, default=0)
    reward = BigIntField(attr="reward", required=True, default=0)
    payload_length = IntField(attr="payloadLength", required=True, default=0)
    payload_hash = StrField(attr="payloadHash", required=True, default=None)
    generator_public_key = StrField(
        attr="generatorPublicKey", required=True, default=None
    )
    block_signature = StrField(attr="blockSignature", required=False, default=None)
    transactions = Field(attr="transactions", required=False, default=[])

    @staticmethod
    def to_bytes_hex(value):
        """Converts integer value to hex representation
        Automatically adds leading zeros if hex number is shorter than 16 characters.
        """
        hex_num = ""
        if value is not None:
            hex_num = format(int(value), "x")
        return ("{}{}".format("0" * (16 - len(hex_num)), hex_num)).encode("utf-8")

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
            if self.number_of_transactions == 2 and (
                self.height == 3084276 or self.height == 34420
            ):
                self.transactions[0], self.transactions[1] = (
                    self.transactions[1],
                    self.transactions[0],
                )

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data must be dict")
        cls = cls()
        for field in cls._fields:
            value = data.get(field.attr, field.default)

            if value is None and field.required:
                raise ValueError("Attribute {} is required".format(field.name))

            if (
                value is not None
                and field.accepted_types
                and not isinstance(value, field.accepted_types)
            ):
                raise TypeError(
                    "Attribute {} ({}) must be of type {}".format(
                        field.name, type(value), field.accepted_types
                    )
                )

            value = field.to_value(value)
            setattr(cls, field.name, value)

        if cls.transactions and isinstance(cls.transactions, list):
            transactions = []
            for transaction_data in cls.transactions:
                transactions.append(Transaction.from_dict(transaction_data))
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
            if value is None and field.required:
                raise ValueError("Attribute {} is required".format(field.name))

            if (
                value is not None
                and field.accepted_types
                and not isinstance(value, field.accepted_types)
            ):
                raise TypeError(
                    "Attribute {} ({}) must be of type {}".format(
                        field.name, type(value), field.accepted_types
                    )
                )

            value = field.to_value(value)
            setattr(cls, field.name, value)

        if cls.transactions:
            for _ in cls.transactions:
                if not isinstance(cls.transaction, Transaction):
                    raise TypeError("Transactions must be a {}".format(Transaction))
        cls._construct_common()
        return cls

    @classmethod
    def from_serialized(cls, bytes_string):
        if not isinstance(bytes_string, bytes):
            raise TypeError("bytes_string must be bytes")
        cls = cls()
        cls.deserialize(bytes_string)
        cls._construct_common()
        return cls

    def get_id_hex(self):
        payload_hash = unhexlify(self.serialize())
        full_hash = sha256(payload_hash).digest()
        config = Config()
        milestone = config.get_milestone(self.height)
        if milestone["block"]["idFullSha256"]:
            return hexlify(full_hash)

        small_hash = full_hash[:8][::-1]
        return hexlify(small_hash)

    def get_id(self):
        id_hex = self.get_id_hex()
        config = Config()
        milestone = config.get_milestone(self.height)
        if milestone["block"]["idFullSha256"]:
            return id_hex.decode("utf-8")
        return str(int(id_hex, 16))

    def serialize(self, include_signature=True):
        config = Config()
        milestone = config.get_milestone(self.height - 1)
        if milestone["block"]["idFullSha256"]:
            if len(self.previous_block) != 64:
                raise Exception(
                    "Previous block shoud be SHA256, but found a non SHA256 block id"
                )
            self.previous_block_hex = self.previous_block.encode("utf-8")
        else:
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
        bytes_data += unhexlify(self.payload_hash.encode("utf-8"))
        bytes_data += unhexlify(self.generator_public_key)

        if include_signature and self.block_signature:
            bytes_data += unhexlify(self.block_signature.encode("utf-8"))

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
            serialized_transaction = unhexlify(transaction.serialize())
            bytes_data += write_bit32(len(serialized_transaction))
            all_transaction_bytes += serialized_transaction

        bytes_data += all_transaction_bytes
        return hexlify(bytes_data)

    def _deserialize_transactions(self, buff):
        transaction_lenghts = []
        for _ in range(self.number_of_transactions):
            transaction_lenghts.append(buff.pop_uint32())
        self.transactions = []
        for trans_len in transaction_lenghts:
            serialized_hex = hexlify(buff.pop_bytes(trans_len))
            self.transactions.append(Transaction.from_serialized(serialized_hex))

    def _deserialize_previous_block(self, buff):
        """
        For deserializing previous block id, we need to check the milestone for
        previous block
        """
        config = Config()
        milestone = config.get_milestone(self.height - 1)
        if milestone["block"]["idFullSha256"]:
            self.previous_block_hex = hexlify(buff.pop_bytes(32))
            self.previous_block = self.previous_block_hex.decode("utf-8")
        else:

            self.previous_block_hex = hexlify(buff.pop_bytes(8))
            self.previous_block = str(int(self.previous_block_hex, 16))

    def deserialize(self, serialized_hex):
        buff = ByteBuffer(unhexlify(serialized_hex))
        self.version = buff.pop_uint32()
        self.timestamp = buff.pop_uint32()
        self.height = buff.pop_uint32()
        self._deserialize_previous_block(buff)
        self.number_of_transactions = buff.pop_uint32()
        self.total_amount = buff.pop_uint64()
        self.total_fee = buff.pop_uint64()
        self.reward = buff.pop_uint64()
        self.payload_length = buff.pop_uint32()
        self.payload_hash = hexlify(buff.pop_bytes(32)).decode("utf-8")
        self.generator_public_key = hexlify(buff.pop_bytes(33)).decode("utf-8")
        # TODO: test the case where block signature is not present
        signature_len = int(hexlify(buff.read_bytes(1, offset=1)), 16)
        signature_to = signature_len + 2
        self.block_signature = hexlify(buff.pop_bytes(signature_to)).decode("utf-8")

        if len(buff) != 0:
            self._deserialize_transactions(buff)
        # TODO: implement edge cases (outlookTable thingy) where some block ids are
        # broken
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
            bytes_data,
            unhexlify(self.block_signature.encode("utf-8")),
            unhexlify(self.generator_public_key.encode("utf-8")),
        )
        return is_verified

    def verify(self):
        errors = []

        # TODO: find a better way to get milestone data
        config = Config()
        milestone = config.get_milestone(self.height)
        # Check that the previous block is set if it's not a genesis block
        if self.height > 1 and not self.previous_block:
            errors.append("Invalid previous block")

        # Chech that the block reward matches with the one specified in config
        if self.reward != milestone["reward"]:
            errors.append(
                "Invalid block reward: {} expected: {}".format(
                    self.reward, milestone["reward"]
                )
            )

        # Verify block signature
        is_valid_signature = self.verify_signature()
        if not is_valid_signature:
            errors.append("Failed to verify block signature")

        # Check if version is correct on the block
        if self.version != milestone["block"]["version"]:
            errors.append("Invalid block version")

        # Check that the block timestamp is not in the future
        is_invalid_timestamp = slots.get_slot_number(
            self.height, self.timestamp
        ) > slots.get_slot_number(self.height, time.get_time())
        if is_invalid_timestamp:
            errors.append("Invalid block timestamp")

        # Check if all transactions are valid
        invalid_transactions = [
            trans for trans in self.transactions if not trans.verify()
        ]
        if len(invalid_transactions) > 0:
            errors.append("One or more transactions are not verified")

        # Check that number of transactions and block.number_of_transactions match
        if len(self.transactions) != self.number_of_transactions:
            errors.append("Invalid number of transactions")

        # Check that number of transactions is not too high (except for genesis block)
        if (
            self.height > 1
            and len(self.transactions) > milestone["block"]["maxTransactions"]
        ):
            errors.append("Too many transactions")

        # Check if transactions add u pto the block values
        applied_transactions = []
        total_amount = 0
        total_fee = 0
        bytes_data = bytes()
        for transaction in self.transactions:
            if transaction.id in applied_transactions:
                errors.append(
                    "Encountered duplicate transaction: {}".format(transaction.id)
                )

            applied_transactions.append(transaction.id)
            total_amount += transaction.amount
            total_fee += transaction.fee
            bytes_data += unhexlify(transaction.id)

        if total_amount != self.total_amount:
            errors.append("Invalid total amount")

        if total_fee != self.total_fee:
            errors.append("Invalid total fee")

        if len(bytes_data) > milestone["block"]["maxPayload"]:
            errors.append("Payload is too large")

        if sha256(bytes_data).hexdigest() != self.payload_hash:
            errors.append("Invalid payload hash")

        return len(errors) == 0, errors

    def get_header(self):
        exclude_fields = ["transactions"]
        data = {}
        for field in self._fields:
            if field.name in exclude_fields:
                continue

            value = getattr(self, field.name)
            data[field.attr] = field.to_json_value(value)
        return data

    def to_json(self):
        # TODO: figure out another name for this as it's not really json, its a
        # dictionary but with the camelcase names as keys
        data = self.get_header()
        data["transactions"] = [t.to_json() for t in self.transactions]
        return data
