from struct import pack
from binascii import hexlify, unhexlify
from binary.hex import write_high, write_low
from binary.unsigned_integer import (
    write_bit32,
    write_bit8,
    write_bit64,
    read_bit32,
    read_bit64,
    read_bit8,
)
from chain.crypto.constants import (
    TRANSACTION_TYPE_TRANSFER,
    TRANSACTION_TYPE_TIMELOCK_TRANSFER,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_VOTE,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_IPFS,
    TRANSACTION_TYPE_MULTI_PAYMENT,
    TRANSACTION_TYPE_DELEGATE_RESIGNATION,
)
from base58 import b58decode_check, b58encode_check
from chain.crypto.address import address_from_public_key
from chain.config import Config
from hashlib import sha256
from chain.crypto.utils import verify_hash, is_transaction_exception


class Transaction(object):
    # TODO: make this mapping better
    # field name, json field name, required, default, to_type
    fields = [
        ('version', 'version', False, None, None),
        ('network', 'network', False, None, None),
        ('type', 'type', True, None, None),
        ('timestamp', 'timestamp', True, None, None),
        ('sender_public_key', 'senderPublicKey', True, None, None),
        ('fee', 'fee', True, 0, int),
        ('amount', 'amount', True, 0, int),
        ('expiration', 'expiration', False, None, None),
        ('recipient_id', 'recipientId', False, None, None),
        ('asset', 'asset', False, None, None),
        ('vendor_field', 'vendorField', False, None, None),
        ('vendor_field_hex', 'vendorFieldHex', False, None, None),
        ('id', 'id', False, None, None),
        ('signature', 'signature', False, None, None),
        ('second_signature', 'secondSignature', False, None, None),
        ('sign_signature', 'signSignature', False, None, None),
        ('signatures', 'signatures', False, [], None),
        ('block_id', 'blockId', False, None, None),
        ('sequence', 'sequence', False, None, None),
        ('timelock', 'timelock', False, None, None),
        ('timelock_type', 'timelockType', False, None, None),
        ('ipfs_hash', 'ipfsHash', False, None, None),
        ('payments', 'payments', False, None, None),
    ]

    def __init__(self, data):
        if isinstance(data, (str, bytes)):
            self.deserialize(data)
        else:
            for field, json_field, required, default, to_type in self.fields:
                value = data.get(json_field, default)
                if to_type:
                    value = to_type(value)
                if required and value is None:
                    raise Exception(
                        'Missing field {}'.format(field)
                    )  # TODO: change exception
                setattr(self, field, value)

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
        if Transaction.can_have_vendor_field(self.type):
            if self.vendor_field:
                bytes_data += write_bit8(len(self.vendor_field))
                bytes_data += self.vendor_field.encode('utf-8')
                return bytes_data
            elif self.vendor_field_hex:
                bytes_data += write_bit8(len(self.vendor_field_hex) / 2)
                bytes_data += self.vendor_field_hex.encode('utf-8')
                return bytes_data

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
                self.asset['signature']['publicKey'].encode('utf-8')
            )

        elif self.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            delegate_bytes = hexlify(self.asset['delegate']['username'].encode('utf-8'))
            bytes_data += write_bit8(len(delegate_bytes))
            bytes_data += unhexlify(delegate_bytes)

        elif self.type == TRANSACTION_TYPE_VOTE:
            vote_bytes = []
            for vote in self.asset['votes']:
                if vote.startswith('+'):
                    vote_bytes.append('01{}'.format(vote[1:]))
                else:
                    vote_bytes.append('00{}'.format(vote[1:]))
            bytes_data += write_bit8(len(self.asset['votes']))
            bytes_data += unhexlify(''.join(vote_bytes))

        elif self.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
            keysgroup = []
            if self.version is None or self.version == 1:
                for key in self.asset['multisignature']['keysgroup']:
                    keysgroup.append(key[1:] if key.startswith('+') else key)
            else:
                keysgroup = self.asset['multisignature']['keysgroup']

            bytes_data += write_bit8(self.asset['multisignature']['min'])
            bytes_data += write_bit8(len(self.asset['multisignature']['keysgroup']))
            bytes_data += write_bit8(self.asset['multisignature']['lifetime'])
            bytes_data += unhexlify(''.join(keysgroup))

        elif self.type == TRANSACTION_TYPE_IPFS:
            bytes_data += write_bit8(len(self.asset['ipfs']['dag']) // 2)
            bytes_data += unhexlify(self.asset['ipfs']['dag'])

        elif self.type == TRANSACTION_TYPE_TIMELOCK_TRANSFER:
            bytes_data += write_bit64(self.amount)
            bytes_data += write_bit8(self.timelock_type)
            bytes_data += write_bit64(self.timelock)
            bytes_data += hexlify(b58decode_check(self.recipient_id))

        elif self.type == TRANSACTION_TYPE_MULTI_PAYMENT:
            bytes_data += write_bit32(len(self.asset['payments']))
            for payment in self.asset['payments']:
                bytes_data += write_bit64(payment['amount'])
                bytes_data += hexlify(b58decode_check(payment['recipientId']))

        elif self.type == TRANSACTION_TYPE_DELEGATE_RESIGNATION:
            pass
        else:
            raise Exception('Transaction type is invalid')  # TODO: better exception
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
            bytes_data += unhexlify(''.join(self.signatures))
        return bytes_data

    def serialize(self):
        """Serialize Transaction
        """
        bytes_data = bytes()  # bytes() or bytes(512)?
        bytes_data += write_bit8(0xFF)  # fill, to distinguish between v1 and v2
        bytes_data += write_bit8(self.version or 0x01)
        bytes_data += write_bit8(
            self.network or 30
        )  # TODO:  or network_config['pubKeyHash']
        bytes_data += write_bit8(self.type)
        bytes_data += write_bit32(self.timestamp)
        bytes_data += write_high(self.sender_public_key.encode('utf-8'))
        bytes_data += write_bit64(self.fee)

        # TODO: test this thorougly as it might be completely wrong
        bytes_data += self._serialize_vendor_field()
        bytes_data += self._serialize_type()
        bytes_data += self._serialize_signatures()

        return hexlify(bytes_data).decode()

    def _deserialize_type(self, bytes_data):
        # TODO: test this extensively
        if self.type == TRANSACTION_TYPE_TRANSFER:
            self.amount = read_bit64(bytes_data)
            self.expiration = read_bit32(bytes_data, offset=8)
            self.recipient_id = b58encode_check(bytes_data[12 : 21 + 12])
            return bytes_data[33:]

        elif self.type == TRANSACTION_TYPE_SECOND_SIGNATURE:
            self.asset['signature'] = {'publicKey': hexlify(bytes_data[:33])}
            return bytes_data[33:]

        elif self.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            username_length = read_bit8(bytes_data) // 2
            username_end = username_length + 1
            self.asset['delegate'] = {'username': bytes_data[1:username_end]}
            return bytes_data[username_end:]

        elif self.type == TRANSACTION_TYPE_VOTE:
            vote_length = read_bit8(bytes_data)
            self.asset['votes'] = []

            start = 1
            for _ in range(vote_length):
                vote = hexlify(bytes_data[start : 34 + start]).decode('utf-8')
                operator = '+' if vote[1] == '1' else '-'
                self.asset['votes'].append('{}{}'.format(operator, vote[2:]))
                start += 34
            return bytes_data[start:]

        elif self.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
            self.asset['multisignature'] = {
                'keysgroup': [],
                'min': read_bit8(bytes_data),
                'lifetime': read_bit8(bytes_data, offset=2),
            }
            keys_num = read_bit8(bytes_data, offset=1)
            start = 3
            for _ in range(keys_num):
                key = hexlify(bytes_data[start : 33 + start])
                self.asset['multisignature']['keysgroup'].append(key)
                start += 33
            return bytes_data[start:]

        elif self.type == TRANSACTION_TYPE_IPFS:
            dag_length = read_bit8(bytes_data)
            self.asset['ipfs'] = {'dag': hexlify(bytes_data[1:dag_length])}
            return bytes_data[dag_length:]

        elif self.type == TRANSACTION_TYPE_TIMELOCK_TRANSFER:
            self.amount = read_bit64(bytes_data)
            self.timelock_type = read_bit8(bytes_data, offset=8)
            self.timelock = read_bit64(bytes_data, offset=9)
            self.recipient_id = b58encode_check(bytes_data[17 : 21 + 17])
            return bytes_data[38:]

        elif self.type == TRANSACTION_TYPE_MULTI_PAYMENT:
            self.asset['payments'] = []
            total = read_bit32(bytes_data)
            offset = 4
            amount = 0
            for x in total:
                payment_amount = read_bit64(bytes_data, offset=offset)
                self.asset['payments'].append(
                    {
                        'amount': payment_amount,
                        'recipientId': b58encode_check(
                            bytes_data[offset + 8 : 21 + offset + 8]
                        ),
                    }
                )
                amount += payment_amount
                offset += 8 + 21

            self.amount = payment_amount
            return bytes_data[offset:]

        elif self.type == TRANSACTION_TYPE_DELEGATE_RESIGNATION:
            pass
        else:
            raise Exception('Transaction type is invalid')  # TODO: better exception

    def _deserialize_signature(self, bytes_data):
        # Signature
        if len(bytes_data) > 0:
            signature_length = int(hexlify(bytes_data[1:2]), 16) + 2
            self.signature = hexlify(bytes_data[:signature_length])
            bytes_data = bytes_data[signature_length:]

        # Second signature
        if len(bytes_data) > 0:
            is_multi_sig = read_bit8(bytes_data) == 255
            if is_multi_sig:
                # Multiple signatures
                self.signatures = []
                # TODO: implement this
                raise NotImplementedError()
            else:
                # Second signature
                second_signature_length = int(hexlify(bytes_data[1:2]), 16) + 2
                self.second_signature = hexlify(bytes_data[:second_signature_length])

    # def _apply_v1_compatibility(self):
    #     if self.version != 1:
    #         return

    #     if self.second_signature:
    #         self.sign_signature = self.second_signature

    #     fill_recipient_types = [
    #         TRANSACTION_TYPE_VOTE,
    #         TRANSACTION_TYPE_SECOND_SIGNATURE,
    #         TRANSACTION_TYPE_MULTI_SIGNATURE
    #     ]
    #     if self.type in fill_recipient_types:
    #         self.recipient_id = address_from_public_key(self.sender_public_key, self.network)

    #     if self.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
    #         self.asset['multisignature']['keysgroup'] = [
    #             '+{}'.format(key) for key in self.asset['multisignature']['keysgroup']
    #         ]

    #     if self.vendor_field_hex:
    #         self.vendor_field = unhexlify(self.vendor_field_hex)

    #     self.id = self.get_id()

    #     # TODO
    #     """
    #     // Apply fix for broken type 1 and 4 transactions, which were
    #     // erroneously calculated with a recipient id.
    #     if (transactionIdFixTable[transaction.id]) {
    #         transaction.id = transactionIdFixTable[transaction.id];
    #     }
    #     """

    def deserialize(self, serialized_hex):
        bytes_data = unhexlify(serialized_hex)

        self.version = read_bit8(bytes_data, offset=1)
        self.network = read_bit8(bytes_data, offset=2)
        self.type = read_bit8(bytes_data, offset=3)
        self.timestamp = read_bit32(bytes_data, offset=4)
        self.sender_public_key = hexlify(bytes_data[8 : 33 + 8])
        self.fee = read_bit64(bytes_data, offset=41)
        self.amount = 0
        self.asset = {}

        if Transaction.can_have_vendor_field(self.type):
            vendor_length = read_bit8(bytes_data, offset=49)
            if vendor_length > 0:
                self.vendor_field_hex = hexlify(bytes_data[49 : vendor_length + 49])

            remaining_bytes = bytes_data[49 + 1 + vendor_length :]
        else:
            remaining_bytes = bytes_data[49 + 1 :]

        signature_bytes = self._deserialize_type(remaining_bytes)
        self._deserialize_signature(signature_bytes)

        # self._apply_v1_compatibility()

    def get_bytes(self, skip_signature=False, skip_second_signature=False):
        # TODO: rename to to_bytes which makes more sense than get_bytes
        if self.version and self.version != 1:
            raise Exception('Invalid transaction version')  # TODO: better exception

        bytes_data = bytes()
        bytes_data += write_bit8(self.type)
        bytes_data += write_bit32(self.timestamp)
        bytes_data += write_high(self.sender_public_key)

        # Apply a fix for broken type 1 (second signature) and 4 (multi signature)
        # transactions, which were erroneously calculated with a recipient id,
        # also apply a fix for all other broken transactions
        is_broken_type = (
            self.type == TRANSACTION_TYPE_SECOND_SIGNATURE
            or self.type == TRANSACTION_TYPE_MULTI_SIGNATURE
        )

        if not self.recipient_id or (is_transaction_exception(self) or is_broken_type):
            bytes_data += pack('21x')
        else:
            # bytes_data += write_high(hexlify(b58decode_check(self.recipient_id)))
            bytes_data += b58decode_check(self.recipient_id)

        if self.vendor_field_hex:
            bytes_data += unhexlify(self.vendor_field_hex)
            num_of_zeroes = 64 - len(unhexlify(self.vendor_field_hex))
            if num_of_zeroes > 0:
                bytes_data += pack('{}x'.format(num_of_zeroes))
        elif self.vendor_field:
            bytes_data += self.vendor_field
            num_of_zeroes = 64 - len(unhexlify(self.vendor_field))
            if num_of_zeroes > 0:
                bytes_data += pack('{}x'.format(num_of_zeroes))
            bytes_data += pack('{}x'.format(num_of_zeroes))
        else:
            bytes_data += pack('64x')

        bytes_data += write_bit64(self.amount)
        bytes_data += write_bit64(self.fee)

        if self.type == TRANSACTION_TYPE_SECOND_SIGNATURE:
            public_key = self.asset['signature']['publicKey']
            bytes_data += unhexlify(public_key)
        elif self.type == TRANSACTION_TYPE_DELEGATE_REGISTRATION:
            bytes_data += self.asset['delegate']['username'].encode()
        elif self.type == TRANSACTION_TYPE_VOTE:
            bytes_data += ''.join(self.asset['votes']).encode()
        elif self.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
            bytes_data += write_bit8(self.asset['multisignature']['min'])
            bytes_data += write_bit8(self.asset['multisignature']['lifetime'])
            bytes_data += ''.join(self.asset['multisignature']['keysgroup']).encode()

        if not skip_signature and self.signature:
            bytes_data += write_high(self.signature)

        if not skip_second_signature and self.sign_signature:
            bytes_data += write_high(self.signSignature)

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
            transaction_bytes, self.signature, self.sender_public_key
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

        is_verified = verify_hash(transaction_bytes, second_signature, public_key)
        return is_verified
