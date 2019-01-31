import hashlib
from binascii import unhexlify

from base58 import b58encode_check

from binary.unsigned_integer import write_bit8


def address_from_public_key(public_key, network_version=None):
    """Get an address from a public key

    Args:
        public_key (str):
        network_version (int, optional):

    Returns:
        bytes:
    """
    # TODO: also check if public key matches the regex, same as in core
    # ```
    #      const pubKeyRegex = /^[0-9A-Fa-f]{66}$/;
    #    if (!pubKeyRegex.test(publicKey)) {
    #        throw new Error(`publicKey '${publicKey}' is invalid`);
    #   }
    #    ```
    # TODO: resolve the network vesion to get it from the config somehow
    # if not network_version:
    #     network = get_network()
    #     network_version = network['version']

    ripemd160 = hashlib.new('ripemd160', unhexlify(public_key.encode()))
    seed = write_bit8(network_version) + ripemd160.digest()
    return b58encode_check(seed).decode()
