from chain.common.config import config
from chain.crypto.constants import TRANSACTION_TYPE_MULTI_SIGNATURE


def _calculate_static_fee(transaction, block_height):
    fees = config.get_milestone(block_height)["fees"]["staticFees"]
    static_fee = fees[str(transaction.type)]
    if transaction.type == TRANSACTION_TYPE_MULTI_SIGNATURE:
        return static_fee * (len(transaction.asset["multisignature"]["keysgroup"]) + 1)
    return static_fee


def _calculate_dynamic_fee(transaction, satoshi_per_byte):
    if satoshi_per_byte <= 0:
        satoshi_per_byte = 1
    addon_bytes = config.pool["dynamic_fees"]["addon_bytes_for_type"][
        str(transaction.type)
    ]
    transaction_bytes = len(transaction.serialize()) / 2
    return (addon_bytes + transaction_bytes) * satoshi_per_byte


def valid_fee_for_broadcast(transaction, block_height):
    dynamic_fees = config.pool["dynamic_fees"]
    if dynamic_fees["enabled"]:
        min_broadcast_fee = _calculate_dynamic_fee(
            transaction, dynamic_fees["min_fee_broadcast"]
        )
        if transaction.fee >= min_broadcast_fee:
            return True
    else:
        static_fee = _calculate_static_fee(transaction, block_height)
        if transaction.fee == static_fee:
            return True
    return False


def valid_fee_for_pool(transaction, block_height):
    dynamic_fees = config.pool["dynamic_fees"]
    if dynamic_fees["enabled"]:
        min_pool_fee = _calculate_dynamic_fee(transaction, dynamic_fees["min_fee_pool"])
        if transaction.fee >= min_pool_fee:
            return True
    else:
        static_fee = _calculate_static_fee(transaction, block_height)
        if transaction.fee == static_fee:
            return True
    return False
