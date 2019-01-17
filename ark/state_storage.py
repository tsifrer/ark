
class BaseStateStorage(object):

    def reset():
        raise NotImplementedError()

    def clear():
        raise NotImplementedError()

    def clear_wake_up_timeout():
        raise NotImplementedError()

    def get_last_block():
        raise NotImplementedError()

    def set_last_block(block):
        raise NotImplementedError()

    def get_last_blocks():
        raise NotImplementedError()

    def get_last_blocks_data():
        raise NotImplementedError()

    def get_last_block_ids():
        raise NotImplementedError()

    def get_last_blocks_by_height(start, end=None):
        raise NotImplementedError()

    def get_common_blocks(ids):
        raise NotImplementedError()

    def cache_transactions(transactions):
        raise NotImplementedError()

    def remove_cached_transaction_ids(transaction_ids):
        raise NotImplementedError()

    def get_cached_transaction_ids():
        raise NotImplementedError()

    def ping_block(incoming_block):
        raise NotImplementedError()

    def push_ping_block(block):
        raise NotImplementedError()
