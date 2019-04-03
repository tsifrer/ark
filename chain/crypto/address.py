import hashlib
import re
from binascii import unhexlify

from base58 import b58encode_check

from binary.unsigned_integer import write_bit8

from chain.common.config import config


def address_from_public_key(public_key, network_version=None):
    """Get an address from a public key

    Args:
        public_key (str):
        network_version (int, optional):

    Returns:
        bytes:
    """
    match = re.fullmatch("^[0-9A-Fa-f]{66}$", public_key)
    if not match:
        raise Exception("Invalid public key")  # TODO: better exception

    if not network_version:
        network_version = config.network["pubKeyHash"]

    ripemd160 = hashlib.new("ripemd160", unhexlify(public_key.encode()))
    payload = write_bit8(network_version) + ripemd160.digest()
    return b58encode_check(payload).decode()
