from ark.interfaces.blockchain import IBlockchain
from ark.settings import PLUGINS

from .state_machine import BlockchainMachine
from .utils import is_block_exception
from ark.crypto import time, slots

BLOCK_ACCEPTED = 'accepted'
BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED = 'discarded_but_can_be_broadcasted'
BLOCK_REJECTED = 'rejected'


# def verify_block(block):



class Blockchain(IBlockchain):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.machine = BlockchainMachine(self, app, self.database)

    @property
    def state(self):
        return self.machine.state

    @property
    def database(self):
        return PLUGINS['database']

    @property
    def p2p(self):
        return PLUGINS['p2p']

    def start(self):
        self.machine.start()

    def stop(self):
        self.machine.stop()

    def rollback_current_round(self):
        # TODO: implement this
        print('Rollback current round is not yet implemented')
        pass

    def is_synced(self):
        block = self.database.get_last_block()
        current_time = time.get_time()
        blocktime = self.app.config.get_milestone(block.height)['blocktime']
        return (current_time - block.timestamp) < (3 * blocktime)




    def _handle_exception_block(self, block):
        forged_block = self.database.get_block_by_id(block.id)
        if forged_block:
            return BLOCK_REJECTED

        print('Block {} ({}) forcibly accecpted'.format(forged_block.height, forged_block.id))
        return self._handle_accepted_block(block)



    def _hande_verification_failed(self, block):
        # TODO:
        # this.blockchain.transactionPool.purgeSendersWithInvalidTransactions(this.block);
        return BLOCK_REJECTED


    def _handle_accepted_block(self, block):
        # TODO: implement thiiiiis
        pass



    def _validate_generator(self, block):
        delegates = self.database.get_active_delegates(block.height)
        slot_number = slots.get_slot_number(block.height, block.timestamp)
        forging_delegate = delegates[slot_number % len(delegates)]
        # generator_username = 




    def process_block(self, block):
        if is_block_exception(self.app, block):
            return self._handle_exception_block(block)

        is_verified, _ = block.verify()
        if not is_verified:
            return self._hande_verification_failed(block)








