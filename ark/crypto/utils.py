import math
from binascii import unhexlify

from coincurve import PublicKey
from ark.config import Config

def verify_hash(message, signature, public_key):
    if not isinstance(signature, bytes):
        signature = unhexlify(signature)
    if not isinstance(public_key, bytes):
        public_key = unhexlify(public_key)

    pub_key = PublicKey(public_key)
    is_verified = pub_key.verify(signature, message)
    return is_verified


def is_block_exception(block):
    config = Config()
    exception_blocks = config['exceptions'].get('blocks', [])
    return block.id in exception_blocks


def is_transaction_exception(block):
    config = Config()
    exception_blocks = config['exceptions'].get('transaction', [])
    return block.id in exception_blocks


def calculate_round(height):
    config = Config()
    max_delegates = config.get_milestone(height)['activeDelegates']

    current_round = math.floor((height - 1) / max_delegates) + 1
    next_round = math.floor(height / max_delegates) + 1
    return current_round, next_round, max_delegates
