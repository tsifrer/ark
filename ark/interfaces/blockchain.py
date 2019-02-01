import abc


class IBlockchain(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def state(self):
        """Returns name of the current blockchain state
        """
        pass

    # @property
    # @abc.abstractmethod
    # def p2p():
    #     raise NotImplementedError()

    # @property
    # @abc.abstractmethod
    # def transaction_pool():
    #     raise NotImplementedError()

    @property
    @abc.abstractmethod
    def database():
        pass

    # @abc.abstractmethod
    # def dispatch(event):
    #     raise NotImplementedError()

    @abc.abstractmethod
    def start(self):
        """Starts the blockchain
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """Stops the blockchain
        """
        pass

    # @abc.abstractmethod
    # def check_network():
    #     raise NotImplementedError()

    # @abc.abstractmethod
    # def update_network_status():
    #     raise NotImplementedError()

    # @abc.abstractmethod
    # def rebuild(n_blocks):
    #     raise NotImplementedError()

    # def reset_state():
    #     raise NotImplementedError()

    # def clear_and_stop_queue():
    #     raise NotImplementedError()

    # def post_transaction(transactions):
    #     raise NotImplementedError()

    # def handle_incoming_block(block):
    #     raise NotImplementedError()

    # def rollback_current_round():
    #     raise NotImplementedError()

    # def remove_blocks(n_blocks):
    #     raise NotImplementedError()

    # def remove_top_blocks(count):
    #     raise NotImplementedError()

    # def rebuild_block(block, callback):
    #     raise NotImplementedError()

    # def process_block(block, callback):
    #     raise NotImplementedError()

    # def force_wakeup():
    #     raise NotImplementedError()

    # def fork_block():
    #     raise NotImplementedError()

    # def get_unconfirmed_transactions(block_size):
    #     raise NotImplementedError()

    # def is_synced(block):
    #     raise NotImplementedError()

    # def is_rebuild_synced(block):
    #     raise NotImplementedError()

    # def get_last_block():
    #     raise NotImplementedError()

    # def get_last_height():
    #     raise NotImplementedError()

    # def get_last_downloaded_block():
    #     raise NotImplementedError()

    # def get_block_ping():
    #     raise NotImplementedError()

    # def ping_block(incoming_block):
    #     raise NotImplementedError()

    # def push_ping_block(block):
    #     raise NotImplementedError()

    # def get_events():
    #     raise NotImplementedError()
