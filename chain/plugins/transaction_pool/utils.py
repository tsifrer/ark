from base58 import b58decode_check

from binary.unsigned_integer import read_bit8

from chain.common.config import config


def is_recipient_on_current_network(recipient_id):
    prefix = read_bit8(b58decode_check(recipient_id))
    return prefix == config.network["pubKeyHash"]
