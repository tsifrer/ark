import logging
from binascii import hexlify, unhexlify
from hashlib import sha256
from struct import pack

import avocato

from base58 import b58decode_check, b58encode_check

from binary.hex import write_high
from binary.unsigned_integer import write_bit32, write_bit64, write_bit8

from chain.common.config import config
from chain.crypto.address import address_from_public_key
from chain.crypto.bytebuffer import ByteBuffer
from chain.crypto.constants import (
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_DELEGATE_RESIGNATION,
    TRANSACTION_TYPE_IPFS,
    TRANSACTION_TYPE_MULTI_PAYMENT,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_TIMELOCK_TRANSFER,
    TRANSACTION_TYPE_TRANSFER,
    TRANSACTION_TYPE_VOTE,
)
from chain.crypto.objects.base import (
    BigIntField,
    BytesField,
    DictField,
    Field,
    IntField,
    ListField,
    StrField,
)
from chain.crypto.utils import is_transaction_exception, verify_hash

logger = logging.getLogger(__name__)


class BaseTransaction(avocato.AvocatoObject):
    version = IntField(attr="version", required=False, default=None)
    network = IntField(attr="network", required=False, default=None)
    type = IntField(attr="type", required=True, default=None)
    timestamp = IntField(attr="timestamp", required=True, default=None)
    sender_public_key = StrField(attr="senderPublicKey", required=True, default=None)
    fee = BigIntField(attr="fee", required=True, default=0)
    amount = BigIntField(attr="amount", required=True, default=0)
    expiration = IntField(attr="expiration", required=False, default=None)
    recipient_id = StrField(attr="recipientId", required=False, default=None)
    asset = DictField(attr="asset", required=False)
    vendor_field = StrField(attr="vendorField", required=False, default=None)
    id = StrField(attr="id", required=False, default=None)
    signature = StrField(attr="signature", required=False, default=None)
    second_signature = StrField(attr="secondSignature", required=False, default=None)
    sign_signature = StrField(attr="signSignature", required=False, default=None)
    signatures = ListField(attr="signatures", required=False)
    block_id = StrField(attr="blockId", required=False, default=None)
    sequence = IntField(attr="sequence", required=False, default=0)
    # TODO: What kind of a field is this?
    timelock = Field(attr="timelock", required=False, default=None)
    timelock_type = IntField(attr="timelockType", required=False, default=None)
    ipfs_hash = BytesField(attr="ipfsHash", required=False, default=None)
    # TODO: What kind of a field is this?
    payments = Field(attr="payments", required=False)

    # TODO: test
    def _construct_common(self):
        self._apply_v1_compatibility()
        self.id = self.get_id()

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
        cls._construct_common()
        return cls

    @classmethod
    def from_serialized(cls, bytes_string):
        if not isinstance(bytes_string, bytes):
            raise TypeError("bytes_string must be bytes")
        cls = cls()
        cls.deserialize(bytes_string)
        cls._construct_common()

        for field in cls._fields:
            value = getattr(cls, field.name, None)
            if value is None:
                if field.required:
                    raise ValueError("Attribute {} is required".format(field.name))
                else:
                    setattr(cls, field.name, field.default)
        return cls

    @classmethod
    def from_object(cls, data):
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
        cls._construct_common()
        return cls

    @staticmethod
    def can_have_vendor_field(transaction_type):
        return transaction_type in [
            TRANSACTION_TYPE_TRANSFER,
            TRANSACTION_TYPE_TIMELOCK_TRANSFER,
        ]

    def _serialize_vendor_field(self):
        """Serialize vendor field of the transaction
        """
        bytes_data = bytes()
        if BaseTransaction.can_have_vendor_field(self.type) and self.vendor_field:
            data = self.vendor_field.encode("utf-8")
            bytes_data += write_bit8(len(data))
            bytes_data += data
            return bytes_data
        else:
            bytes_data += write_bit8(0x00)
            return bytes_data

    def _serialize_type(self):
        """Serialize transaction specific data (eg. delegate registration)
        """
        bytes_data = bytes()

        if self.type == TRANSACTION_TYPE_TRANSFER:
            bytes_data += write_bit64(self.amount)
            bytes_data += write_bit32(self.expiration or 0)
            bytes_data += write_high(hexlify(b58decode_check(self.recipient_id)))

        elif self.type == TRANSACTION_TYPE_SECOND_SIGNATURE:
            bytes_data += unhexlify(
                self.asset["signature"]["publicKey"].encode("utf-8")
            )

        elif self.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            delegate_bytes = hexlify(self.asset["delegate"]["username"].encode("utf-8"))
            bytes_data += write_bit8(len(delegate_bytes))
            bytes_data += unhexlify(delegate_bytes)

        elif self.type == TRANSACTION_TYPE_VOTE:
            vote_bytes = []
            for vote in self.asset["votes"]:
                if vote.startswith("+"):
                    vote_bytes.append("01{}".format(vote[1:]))
                else:
                    vote_bytes.append("00{}".format(vote[1:]))
            bytes_data += write_bit8(len(self.asset["votes"]))
            bytes_data += unhexlify("".join(vote_bytes))

        elif self.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
            keysgroup = []
            if self.version is None or self.version == 1:
                for key in self.asset["multisignature"]["keysgroup"]:
                    keysgroup.append(key[1:] if key.startswith("+") else key)
            else:
                keysgroup = self.asset["multisignature"]["keysgroup"]

            bytes_data += write_bit8(self.asset["multisignature"]["min"])
            bytes_data += write_bit8(len(self.asset["multisignature"]["keysgroup"]))
            bytes_data += write_bit8(self.asset["multisignature"]["lifetime"])
            bytes_data += unhexlify("".join(keysgroup).encode("utf-8"))

        elif self.type == TRANSACTION_TYPE_IPFS:
            bytes_data += write_bit8(len(self.asset["ipfs"]["dag"]) // 2)
            bytes_data += unhexlify(self.asset["ipfs"]["dag"])

        elif self.type == TRANSACTION_TYPE_TIMELOCK_TRANSFER:
            bytes_data += write_bit64(self.amount)
            bytes_data += write_bit8(self.timelock_type)
            bytes_data += write_bit64(self.timelock)
            bytes_data += b58decode_check(self.recipient_id)

        elif self.type == TRANSACTION_TYPE_MULTI_PAYMENT:
            bytes_data += write_bit32(len(self.asset["payments"]))
            for payment in self.asset["payments"]:
                bytes_data += write_bit64(payment["amount"])
                bytes_data += b58decode_check(payment["recipientId"])

        elif self.type == TRANSACTION_TYPE_DELEGATE_RESIGNATION:
            pass
        else:
            raise Exception("Transaction type is invalid")  # TODO: better exception
        return bytes_data

    def _serialize_signatures(self):
        """Serialize signature data of the transaction
        """
        bytes_data = bytes()
        if self.signature:
            bytes_data += unhexlify(self.signature)

            if self.second_signature:
                bytes_data += unhexlify(self.second_signature)
            elif self.sign_signature:
                bytes_data += unhexlify(self.sign_signature)

            if self.signatures:
                # add 0xff separator to signal start of multi-signature transactions
                bytes_data += write_bit8(0xFF)
                bytes_data += unhexlify("".join(self.signatures))

        return bytes_data

    def serialize(self):
        """Serialize Transaction
        """
        bytes_data = bytes()  # bytes() or bytes(512)?
        bytes_data += write_bit8(0xFF)  # fill, to distinguish between v1 and v2
        bytes_data += write_bit8(self.version or 0x01)
        bytes_data += write_bit8(self.network or config.network["pubKeyHash"])
        bytes_data += write_bit8(self.type)
        bytes_data += write_bit32(self.timestamp)
        bytes_data += write_high(self.sender_public_key.encode("utf-8"))
        bytes_data += write_bit64(self.fee)

        # TODO: test this thorougly as it might be completely wrong
        bytes_data += self._serialize_vendor_field()
        bytes_data += self._serialize_type()
        bytes_data += self._serialize_signatures()

        return hexlify(bytes_data)

    def _deserialize_type(self, buff):
        # TODO: test this extensively
        if self.type == TRANSACTION_TYPE_TRANSFER:
            self.amount = buff.pop_uint64()
            self.expiration = buff.pop_uint32()
            self.recipient_id = b58encode_check(buff.pop_bytes(21)).decode("utf-8")

        elif self.type == TRANSACTION_TYPE_SECOND_SIGNATURE:
            self.asset["signature"] = {
                "publicKey": hexlify(buff.pop_bytes(33)).decode("utf-8")
            }

        elif self.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            username_length = buff.pop_uint8()
            self.asset["delegate"] = {
                "username": buff.pop_bytes(username_length).decode("utf-8")
            }

        elif self.type == TRANSACTION_TYPE_VOTE:
            vote_length = buff.pop_uint8()
            self.asset["votes"] = []

            for _ in range(vote_length):
                vote = hexlify(buff.pop_bytes(34)).decode("utf-8")
                operator = "+" if vote[1] == "1" else "-"
                self.asset["votes"].append("{}{}".format(operator, vote[2:]))

        elif self.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
            self.asset["multisignature"] = {"keysgroup": [], "min": buff.pop_uint8()}

            keys_num = buff.pop_uint8()
            self.asset["multisignature"]["lifetime"] = buff.pop_uint8()

            for _ in range(keys_num):
                key = hexlify(buff.pop_bytes(33)).decode("utf-8")
                self.asset["multisignature"]["keysgroup"].append(key)

        elif self.type == TRANSACTION_TYPE_IPFS:
            dag_length = buff.pop_uint8()
            self.asset["ipfs"] = {
                "dag": hexlify(buff.pop_bytes(dag_length)).decode("utf-8")
            }

        elif self.type == TRANSACTION_TYPE_TIMELOCK_TRANSFER:
            self.amount = buff.pop_uint64()
            self.timelock_type = buff.pop_uint8()
            self.timelock = buff.pop_uint64()
            self.recipient_id = b58encode_check(buff.pop_bytes(21)).decode("utf-8")

        elif self.type == TRANSACTION_TYPE_MULTI_PAYMENT:
            self.asset["payments"] = []
            total = buff.pop_uint32()
            amount = 0
            for _ in range(total):
                payment_amount = buff.pop_uint64()
                self.asset["payments"].append(
                    {
                        "amount": payment_amount,
                        "recipientId": b58encode_check(buff.pop_bytes(21)).decode(
                            "utf-8"
                        ),
                    }
                )
                amount += payment_amount
            self.amount = amount

        elif self.type == TRANSACTION_TYPE_DELEGATE_RESIGNATION:
            pass
        else:
            raise Exception("Transaction type is invalid")  # TODO: better exception

    def _deserialize_signature(self, buff):
        # if self.version == 1:
        self._deserialize_ECDSA(buff)
        # else:
        #     self._deserialize_schnorr(buff)

    def _deserialize_ECDSA(self, buff):
        # Signature

        # hexlify(buff.pop_bytes(33)).decode("utf-8")

        if len(buff) > 0:
            signature_length = int(hexlify(buff.read_bytes(1, offset=1)), 16) + 2
            self.signature = hexlify(buff.pop_bytes(signature_length)).decode("utf-8")

        # Second signature
        if len(buff) > 0:
            is_multi_sig = buff.read_uint8() == 255
            if is_multi_sig:
                buff.pop_uint8()
                # Multiple signatures
                self.signatures = []
                while len(buff) > 0:
                    multi_signature_length = (
                        int(hexlify(buff.read_bytes(1, offset=1)), 16) + 2
                    )
                    self.signatures.append(
                        hexlify(buff.pop_bytes(multi_signature_length)).decode("utf-8")
                    )
            else:
                # Second signature
                second_signature_length = (
                    int(hexlify(buff.read_bytes(1, offset=1)), 16) + 2
                )
                self.second_signature = hexlify(
                    buff.pop_bytes(second_signature_length)
                ).decode("utf-8")

    def _deserialize_schnorr(self, buff):
        raise NotImplementedError

    def _apply_v1_compatibility(self):
        if self.version != 1:
            return

        if self.second_signature:
            self.sign_signature = self.second_signature

        if self.type == TRANSACTION_TYPE_VOTE:
            self.recipient_id = address_from_public_key(
                self.sender_public_key, self.network
            )
        elif self.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
            keysgroup = []
            for key in self.asset["multisignature"]["keysgroup"]:
                if not key.startswith("+"):
                    key = "+{}".format(key)
                keysgroup.append(key)
            self.asset["multisignature"]["keysgroup"] = keysgroup

    def deserialize(self, serialized_hex):
        buff = ByteBuffer(unhexlify(serialized_hex))
        buff.pop_bytes(1)  # skip 0xFF marker
        self.version = buff.pop_uint8()
        self.network = buff.pop_uint8()
        self.type = buff.pop_uint8()
        self.timestamp = buff.pop_uint32()
        self.sender_public_key = hexlify(buff.pop_bytes(33)).decode("utf-8")
        self.fee = buff.pop_uint64()
        vendor_length = buff.pop_uint8()
        if vendor_length > 0:
            if BaseTransaction.can_have_vendor_field(self.type):
                self.vendor_field = buff.pop_bytes(vendor_length).decode("utf-8")
            else:
                buff.pop_bytes(vendor_length)

        self._deserialize_type(buff)
        self._deserialize_signature(buff)

    def get_bytes(self, skip_signature=False, skip_second_signature=False):
        """
        Serializes the given transaction prior to AIP11 (legacy).
        """
        # TODO: rename to to_bytes which makes more sense than get_bytes
        if self.version and self.version != 1:
            raise Exception("Invalid transaction version")  # TODO: better exception

        bytes_data = bytes()
        bytes_data += write_bit8(self.type)
        bytes_data += write_bit32(self.timestamp)
        bytes_data += write_high(self.sender_public_key)

        # Apply a fix for broken type 1 (second signature) and 4 (multi signature)
        # transactions, which were erroneously calculated with a recipient id,
        # also apply a fix for all other broken transactions
        is_broken_type = self.type in [
            TRANSACTION_TYPE_SECOND_SIGNATURE,
            TRANSACTION_TYPE_MULTI_SIGNATURE,
        ]

        if not self.recipient_id or (
            is_transaction_exception(self.id) or is_broken_type
        ):
            bytes_data += pack("21x")
        else:
            bytes_data += b58decode_check(self.recipient_id)

        if self.vendor_field:
            encoded_vendor_field = self.vendor_field.encode("utf-8")
            bytes_data += encoded_vendor_field
            num_of_zeroes = 64 - len(encoded_vendor_field)
            if num_of_zeroes > 0:
                bytes_data += pack("{}x".format(num_of_zeroes))
        else:
            bytes_data += pack("64x")

        bytes_data += write_bit64(self.amount)
        bytes_data += write_bit64(self.fee)

        if self.type == TRANSACTION_TYPE_SECOND_SIGNATURE:
            public_key = self.asset["signature"]["publicKey"]
            bytes_data += unhexlify(public_key)
        elif self.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            bytes_data += self.asset["delegate"]["username"].encode()
        elif self.type == TRANSACTION_TYPE_VOTE:
            bytes_data += "".join(self.asset["votes"]).encode()
        elif self.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
            bytes_data += write_bit8(self.asset["multisignature"]["min"])
            bytes_data += write_bit8(self.asset["multisignature"]["lifetime"])
            bytes_data += "".join(self.asset["multisignature"]["keysgroup"]).encode()

        if not skip_signature and self.signature:
            bytes_data += write_high(self.signature)

        if not skip_second_signature and self.sign_signature:
            bytes_data += write_high(self.sign_signature)

        return bytes_data

    def verify(self):
        if self.version and self.version != 1:
            return False

        if not self.signature:
            return False

        transaction_bytes = self.get_bytes(
            skip_signature=True, skip_second_signature=True
        )
        is_verified = verify_hash(
            transaction_bytes,
            unhexlify(self.signature.encode("utf-8")),
            unhexlify(self.sender_public_key.encode("utf-8")),
        )
        return is_verified

    def verify_second_signature(self, public_key):
        if self.version and self.version != 1:
            transaction_bytes = self.get_bytes()
            second_signature = self.second_signature
        else:
            transaction_bytes = self.get_bytes(skip_second_signature=True)
            second_signature = self.sign_signature

        if not second_signature:
            return False

        is_verified = verify_hash(
            transaction_bytes,
            unhexlify(second_signature.encode("utf-8")),
            unhexlify(public_key.encode("utf-8")),
        )
        return is_verified

    def get_hash(self):
        """Generates sha256 hash of bytes.

        :returns (str): transaction hash
        """
        transaction_bytes = self.get_bytes()
        return sha256(transaction_bytes).hexdigest()

    def get_id(self):
        """Generates an ID for current transaction from bytes

        :returns (str): transaction id
        """
        transaction_id = self.get_hash()

        # Some transactions in the past might have erroneously calculated IDs
        # so if they are defined as exceptions, override the ID with the one defined
        # in exceptions
        exceptions = config.exceptions.get("transactionIdFixTable", {})
        if transaction_id in exceptions:
            transaction_id = exceptions[transaction_id]

        return transaction_id

    def to_json(self):
        """Convers transaction to dictiionary with camelCase field names

        :returns (dict): dictionary with camelCase field names
        """
        data = {}
        for field in self._fields:
            value = getattr(self, field.name)
            data[field.attr] = field.to_json_value(value)
        return data

    def calculate_expires_at(self, max_transaction_age):
        """Derives transaction expiration time in number of seconds since the genesis
        block.

        :param int max_transaction_age: maximum age of a transaction in seconds
        :returns int: expiration time in seconds or None if transaction does not expire
        """
        if self.expiration and self.expiration > 0:
            return self.expiration

        if self.type == TRANSACTION_TYPE_TIMELOCK_TRANSFER:
            return None

        return self.timestamp + max_transaction_age

    def can_be_applied_to_wallet(self, wallet, wallet_manager, block_height):
        """Checks if transaction can be applied to the wallet

        :param (Wallet) wallet: wallet you want to apply the transaction to
        :param (WalletManager) wallet_manager: wallet manager
        :param (int) block_height: current block height
        :returns (bool): True if can be applied, False otherwise
        """
        if wallet.multisignature:
            logger.error("Multi signatures are currently not supported")
            return False

        if self.sender_public_key != wallet.public_key:
            logger.error("Sender public key does not match the wallet")
            return False

        balance = wallet.balance - self.amount - self.fee
        if balance < 0:
            logger.error("Insufficient balance in the wallet")
            return False

        if wallet.second_public_key:
            if not self.verify_second_signature(wallet.second_public_key):
                logger.error("Failed to verify second-signature")
                return False
        elif self.second_signature or self.sign_signature:
            milestone = config.get_milestone(block_height)
            # Accept invalid second signature fields prior the applied patch
            if not milestone["ignoreInvalidSecondSignatureField"]:
                logger.error("Wallet does not allow second signatures")
                return False

        return True

    def apply_to_sender_wallet(self, wallet):
        """Applies transaction to senders wallet.

        :param (Wallet) wallet: senders wallet
        """
        address = address_from_public_key(self.sender_public_key)
        incorrect_wallet = (
            self.sender_public_key != wallet.public_key and address != wallet.address
        )
        if incorrect_wallet:
            raise Exception(
                "Incorrect wallet. Wallet with address {} ({}) does not match with "
                "transaction address {} ({})".format(
                    wallet.address, wallet.public_key, address, self.sender_public_key
                )
            )

        total = self.amount + self.fee
        wallet.balance -= total

    def apply_to_recipient_wallet(self, wallet):
        """Applies transaction to recipients wallet

        :param (Wallet) wallet: recipients wallet
        """
        if self.recipient_id != wallet.address:
            raise Exception(
                "Incorrect wallet. Wallet with address {} does not match"
                "with transaction recipient address {}".format(
                    wallet.address, self.recipient_id
                )
            )

        wallet.balance += self.amount

    def revert_for_sender_wallet(self, wallet):
        """Reverts transaction on senders wallet

        :param (Wallet) wallet: senders wallet
        """
        address = address_from_public_key(self.sender_public_key)
        incorrect_wallet = (
            self.sender_public_key != wallet.public_key and address != wallet.address
        )
        if incorrect_wallet:
            raise Exception(
                "Incorrect wallet. Wallet with address {} ({}) does not match with "
                "transaction address {} ({})".format(
                    wallet.address, wallet.public_key, address, self.sender_public_key
                )
            )
        total = self.amount + self.fee
        wallet.balance += total

    def revert_for_recipient_wallet(self, wallet):
        """Reverts transaction on recipients wallet

        :param (Wallet) wallet: recipients wallet
        """
        if self.recipient_id != wallet.address:
            raise Exception(
                "Incorrect wallet. Wallet with address {} does not match"
                "with transaction recipient address {}".format(
                    wallet.address, self.recipient_id
                )
            )
        wallet.balance -= self.amount

    def validate_for_transaction_pool(self, pool, transactions):
        """Custom validation for each transaction type before it's accepted to
        transaction pool

        :param (Pool) pool: current Pool object
        :param (list) transactions: List of Transactions in the current batch to process

        :returns: None if validation passed, error message (str) instead
        """
        return "Transaction with type {} is not supported".format(self.type)

    def apply(self, sender, recipient, wallet_manager):
        """Custom apply functionality for each transaction type

        :param (Wallet) sender: sender Wallet object
        :param (Wallet) recipient: recipient Wallet object or None if recipient is not
                                   set
        :param (WalletManager) wallet_manager: Wallet manager object
        """
        pass
