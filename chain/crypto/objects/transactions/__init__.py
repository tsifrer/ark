from binascii import unhexlify

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

from .base import BaseTransaction  # noqa
from .delegate_registration import DelegateRegistrationTransaction
from .delegate_resignation import DelegateResignationTransaction
from .ipfs import IPFSTransaction
from .multi_payment import MultiPaymentransaction
from .multi_signature import MultiSignatureTransaction
from .second_signature import SecondSignatureTransaction
from .timelock_transfer import TimelockTransferTransaction
from .transfer import TransferTransaction
from .vote import VoteTransaction

# TODO: Make this somewhat dynamic so people can install new transaction types
# directly from pip and map it (or something like that)
TRANSACTION_TYPE_MAPPING = {
    TRANSACTION_TYPE_DELEGATE_REGISTRATION: DelegateRegistrationTransaction,
    TRANSACTION_TYPE_DELEGATE_RESIGNATION: DelegateResignationTransaction,
    TRANSACTION_TYPE_IPFS: IPFSTransaction,
    TRANSACTION_TYPE_MULTI_PAYMENT: MultiPaymentransaction,
    TRANSACTION_TYPE_MULTI_SIGNATURE: MultiSignatureTransaction,
    TRANSACTION_TYPE_SECOND_SIGNATURE: SecondSignatureTransaction,
    TRANSACTION_TYPE_TIMELOCK_TRANSFER: TimelockTransferTransaction,
    TRANSACTION_TYPE_TRANSFER: TransferTransaction,
    TRANSACTION_TYPE_VOTE: VoteTransaction,
}


def from_serialized(serialized_hex):
    if not isinstance(serialized_hex, bytes):
        raise TypeError("serialized_hex must be bytes")

    buff = ByteBuffer(unhexlify(serialized_hex))
    buff.pop_bytes(3)  # skip first 3 bytes (marker, version and network)
    transaction_type = buff.pop_uint8()

    transaction_cls = TRANSACTION_TYPE_MAPPING.get(transaction_type)
    if not transaction_cls:
        raise Exception(
            "Couldn't find transaction {} in mapping".format(transaction_type)
        )
    return transaction_cls.from_serialized(serialized_hex)


def from_dict(data):
    if not isinstance(data, dict):
        raise TypeError("data must be dict")

    transaction_cls = TRANSACTION_TYPE_MAPPING.get(data.get("type"))
    if not transaction_cls:
        raise Exception(
            "Couldn't find transaction {} in mapping".format(data.get("type"))
        )
    return transaction_cls.from_dict(data)
