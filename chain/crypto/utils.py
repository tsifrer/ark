import math

from coincurve import PublicKey

from chain.config import Config


def verify_hash(message, signature, public_key):
    if not isinstance(signature, bytes):
        raise TypeError('signature must be bytes')
    if not isinstance(public_key, bytes):
        raise TypeError('public_key must be bytes')

    pub_key = PublicKey(public_key)
    is_verified = pub_key.verify(signature, message)
    return is_verified


def is_block_exception(block):
    config = Config()
    # TODO: cache this calculation on config object as it's not gonna change during
    # runtime
    exception_blocks = config['exceptions'].get('blocks', [])
    exception_blocks = [block_id for block_id in exception_blocks]
    return block.id in exception_blocks


def is_transaction_exception(transaction):
    config = Config()
    exception_transactions = config['exceptions'].get('transaction', [])
    return transaction.id in exception_transactions


def calculate_round(height):
    config = Config()
    max_delegates = config.get_milestone(height)['activeDelegates']
    current_round = math.floor((height - 1) / max_delegates) + 1
    next_round = math.floor(height / max_delegates) + 1
    return current_round, next_round, max_delegates
