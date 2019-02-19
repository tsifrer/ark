from ark.interfaces.blockchain import IBlockchain
from ark.settings import PLUGINS

from .state_machine import BlockchainMachine
from .utils import is_block_exception, is_block_chained
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

    def fork_block(self, block):
        # TODO:
        print('FORKING')
        raise NotImplementedError()

    def is_synced(self):
        block = self.database.get_last_block()
        current_time = time.get_time()
        blocktime = self.app.config.get_milestone(block.height)['blocktime']
        return (current_time - block.timestamp) < (3 * blocktime)

    def _handle_exception_block(self, block):
        forged_block = self.database.get_block_by_id(block.id)
        if forged_block:
            return BLOCK_REJECTED

        print('Block {} ({}) forcibly accecpted'.format(
            forged_block.height, forged_block.id
        ))
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
        generator_username = self.database.wallets.find_by_public_key(
            block.generator_public_key
        ).username
        forging_delegate = None
        if delegates:
            forging_delegate = delegates[slot_number % len(delegates)]

        if forging_delegate and forging_delegate.public_key != block.generator_public_key:
            forging_username = self.database.wallets.find_by_public_key(
                forging_delegate.public_key
            ).username
            print('Delegate {} ({}) not allowed to forge, should be {} ({})'.format(
                generator_username,
                block.generator_public_key,
                forging_username,
                forging_delegate.public_key,
            ))
            return False

        # TODO: this seems weird as we can't decide if delegate is allowed to forge, but
        # we still accept it as a valid generator
        if not forging_delegate:
            print('Could not decide if delegate {} ({}) is allowed to forge block {}'.format(
                generator_username, block.generator_public_key, block.height
            ))

        print('Delegate {} ({}) allowed to forge block {}'.format(
            generator_username, block.generator_public_key, block.height
        ))
        return True

    def _handle_unchained_block(self, block, last_block, is_valid_generator):
        if block.height > last_block.height + 1:
            print(
                (
                    'Blockchain not ready to accept new block at height {}. '
                    'Last block: {}'
                ).format(block.height, last_block.height)
            )
            return BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED

        elif block.height < last_block.height:
            print("Block {} disregarded because it's already in blockchain".format(
                block.height
            ))
            return BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED

        elif block.height == last_block.height and block.id == last_block.id:
            print('Block {} just received'.format(block.height))
            return BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED

        elif block.timestamp < last_block.timestamp:
            print(
                'Block {} disregarded, because the timestamp is lower than the previous timestamp'.format(
                    block.height
                )
            )
            return BLOCK_REJECTED

        else:
            if is_valid_generator:
                print('Detect double forging by {}'.format(block.generator_public_key))
                delegates = self.db.get_active_delegates(block.height)

                is_active_delegate = False
                for delegate in delegates:
                    if delegate.public_key == block.generator_public_key:
                        is_active_delegate = True
                        break

                if is_active_delegate:
                    self.fork_block(block)
                return BLOCK_REJECTED

            print(
                (
                    'Forked block disregarded because it is not allowed to be forged. '
                    'Caused by delegate {}'
                ).format(block.generator_public_key)
            )
            return BLOCK_REJECTED

    def _block_contains_forged_transactions(self, block):
        if len(block.transactions) > 0:
            transaction_ids = [transaction.id for transaction in block.transactions]
            forged_ids = self.database.get_forged_transaction_ids(transaction_ids)
            if len(forged_ids) > 0:
                print(
                    'Block {} disregarded, because it contains already forged transactions'
                )
                return True
        return False

    def process_block(self, block):
        if is_block_exception(self.app, block):
            return self._handle_exception_block(block)

        is_verified, _ = block.verify()
        if not is_verified:
            return self._hande_verification_failed(block)

        is_valid_generator = self._validate_generator(block)

        last_block = self.database.get_last_block()
        is_chained = is_block_chained(last_block, block)
        if not is_chained:
            return self._handle_unchained_block(block, last_block, is_valid_generator)

        if not is_valid_generator:
            return BLOCK_REJECTED

        contains_forged_transactions = self._block_contains_forged_transactions(block)
        if contains_forged_transactions:
            return BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED

        return self._handle_accepted_block(block)







