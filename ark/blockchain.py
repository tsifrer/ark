
class BaseBlockchain(object):

    @property
    def state():
        raise NotImplementedError()

    @property
    def p2p():
        raise NotImplementedError()

    @property
    def transaction_pool():
        raise NotImplementedError()

    @property
    def database():
        raise NotImplementedError()

    def dispatch(event):
        raise NotImplementedError()

    def start(skip_started_check):
        raise NotImplementedError()

    def stop():
        raise NotImplementedError()

    def check_network():
        raise NotImplementedError()

    def update_network_status():
        raise NotImplementedError()

    def rebuild(n_blocks):
        raise NotImplementedError()

    def reset_state():
        raise NotImplementedError()

    def clear_and_stop_queue():
        raise NotImplementedError()

    def post_transaction(transactions):
        raise NotImplementedError()

    def handle_incoming_block(block):
        raise NotImplementedError()

    def rollback_current_round():
        raise NotImplementedError()

    def remove_blocks(n_blocks):
        raise NotImplementedError()

    def remove_top_blocks(count):
        raise NotImplementedError()

    def rebuild_block(block, callback):
        raise NotImplementedError()

    def process_block(block, callback):
        raise NotImplementedError()

    def force_wakeup():
        raise NotImplementedError()

    def fork_block():
        raise NotImplementedError()

    def get_unconfirmed_transactions(block_size):
        raise NotImplementedError()

    def is_synced(block):
        raise NotImplementedError()

    def is_rebuild_synced(block):
        raise NotImplementedError()

    def get_last_block():
        raise NotImplementedError()

    def get_last_height():
        raise NotImplementedError()

    def get_last_downloaded_block():
        raise NotImplementedError()

    def get_block_ping():
        raise NotImplementedError()

    def ping_block(incoming_block):
        raise NotImplementedError()

    def push_ping_block(block):
        raise NotImplementedError()

    def get_events():
        raise NotImplementedError()
