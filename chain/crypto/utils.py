import logging
import math

from coincurve import PublicKey

from chain.common.config import config

logger = logging.getLogger(__name__)


def verify_hash(message, signature, public_key):
    if not isinstance(signature, bytes):
        raise TypeError("signature must be bytes")
    if not isinstance(public_key, bytes):
        raise TypeError("public_key must be bytes")

    pub_key = PublicKey(public_key)
    try:
        is_verified = pub_key.verify(signature, message)
    except ValueError as e:
        logger.error(str(e))
        logger.error(
            "Signature that could not be parsed %s, message: %s", signature, message
        )
        return False
    return is_verified


def is_block_exception(block):
    # TODO: cache this calculation on config object as it's not gonna change during
    # runtime
    exception_blocks = config.exceptions.get("blocks", [])
    exception_blocks = [block_id for block_id in exception_blocks]
    return block.id in exception_blocks


def is_transaction_exception(transaction_id):
    if not transaction_id:
        return False
    if not isinstance(transaction_id, str):
        raise TypeError("transaction_id must be str")
    exception_transactions = config.exceptions.get("transaction", [])
    return transaction_id in exception_transactions


def calculate_round(height):
    max_delegates = config.get_milestone(height)["activeDelegates"]
    current_round = math.floor((height - 1) / max_delegates) + 1
    next_round = math.floor(height / max_delegates) + 1
    return current_round, next_round, max_delegates


def is_new_round(height):
    """Checks if height is at the start of new round
    """
    max_delegates = config.get_milestone(height)["activeDelegates"]
    return height % max_delegates == 1
