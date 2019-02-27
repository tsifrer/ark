from datetime import datetime
from time import sleep
from ark.interfaces.blockchain import IBlockchain
from ark.settings import PLUGINS

from .utils import is_block_chained
from .constants import (
    BLOCK_ACCEPTED,
    BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED,
    BLOCK_REJECTED,
)
from ark.crypto import time, slots
from ark.crypto.utils import is_block_exception
from ark.crypto.models.block import Block


class Blockchain(object):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

    @property
    def database(self):
        return PLUGINS['database']

    @property
    def p2p(self):
        return PLUGINS['p2p']

    def start(self):
        # TODO: change prints to loggers
        print('Starting the blockchain')
        try:
            block = self.database.get_last_block()

            # If block is not found in the db, insert a genesis block
            if not block:
                print('No block found in the database')
                block = Block(self.app.config['genesis_block'])
                if block.payload_hash != self.app.config['network']['nethash']:
                    print(
                        'FATAL: The genesis block payload hash is different from '
                        'the configured nethash'
                    )
                    self.stop()
                    return

                else:
                    self.database.save_block(block)

            # If database did not just restore database integrity, verify the blockchain
            if not self.database.restored_database_integrity:
                print('Verifying database integrity')
                is_valid, errors = self.database.verify_blockchain()
                if not is_valid:
                    print('FATAL: Database is corrupted')
                    print(errors)
                    # return self.rollback() # TODO: uncomment
                print('Verified database integrity')
            else:
                print(
                    'Skipping database integrity check after successful database '
                    'recovery'
                )

            # TODO: figure this  out
            # // only genesis block? special case of first round needs to be dealt with
            # if (block.data.height === 1) {
            #     await blockchain.database.deleteRound(1);
            # }

            milestone = self.app.config.get_milestone(block.height)

            # TODO: Watafak
            # stateStorage.setLastBlock(block);
            # stateStorage.lastDownloadedBlock = block;

            # if (stateStorage.networkStart) {
            #     await blockchain.database.buildWallets(block.data.height);
            #     await blockchain.database.saveWallets(true);
            #     await blockchain.database.applyRound(block.data.height);
            #     await blockchain.transactionPool.buildWallets();

            #     return blockchain.dispatch("STARTED");
            # }

            # if (process.env.NODE_ENV === "test") {
            #     logger.verbose("TEST SUITE DETECTED! SYNCING WALLETS AND STARTING IMMEDIATELY. :bangbang:");

            #     stateStorage.setLastBlock(new Block(config.get("genesisBlock")));
            #     await blockchain.database.buildWallets(block.data.height);

            #     return blockchain.dispatch("STARTED");
            # }

            print('Last block in database: {}'.format(block.height))
            # TODO: whatever the comment below means
            # removing blocks up to the last round to compute active delegate list later if needed
            # active_delegates = self.database.get_active_delegates(block.height)
            # if not active_delegates:
            #     # TODO: rollback_current_round doesn't do anything ATM
            #     self.rollback_current_round()


            # TODO: Rebuild SPV stuff

            # TODO: the rest of the stuff

            # Rebuild wallets
            self.database.wallets.build()


            delegate_wallets = self.database.wallets.load_active_delegate_wallets(562)

            # for wallet in delegate_wallets:
            #     print(wallet.public_key, wallet.username, wallet.vote_balance)

            if block.height == 1:
                self.database.apply_round(block.height)



            self.start_syncing()
        except Exception as e:
            raise e  # TODO:
            # TODO: log exception
            self.stop()



    def start_syncing(self):
        start = datetime.now()
        print('STARTED', start)
        while True:
            last_block = self.database.get_last_block()
            if self.is_synced(last_block):
                print('Blockhain is syced!')
                break
            else:
                self.sync_blocks(last_block)
            print('Time taken', datetime.now() - start)

        print('Done syncing', datetime.now() - start)



    def sync_blocks(self, last_block):
        print()
        print()
        print('downloading harambe')
        print()
        blocks = self.p2p.download_blocks(last_block.height)

        if blocks:
            print('chained', is_block_chained(last_block, blocks[0]))
            print('exception', is_block_exception(blocks[0]))
            is_chained = is_block_chained(last_block, blocks[0]) or is_block_exception(blocks[0])
            if is_chained:
                print('Downloaded {} new blocks accounting for a total of {} transactions'.format(
                    len(blocks), sum([x.number_of_transactions for x in blocks])
                ))

                for block in blocks:
                    status = self.process_block(block, last_block)
                    print('Block {} was {}'.format(block.id, status))
                    # TODO: this might be completely wrong to handle
                    if status == BLOCK_REJECTED:
                        msg = 'Block {} was rejected. Skipping all other blocks in this batch'.format(block.id)
                        print(msg)
                        raise Exception(msg)
                    if status == BLOCK_ACCEPTED:
                        last_block = block
                # TODO:
                # blockchain.enqueueBlocks(blocks);
                # blockchain.dispatch("DOWNLOADED");

            else:
                print('Downloaded block not accepted: {}'.format(blocks[0].id)) # TODO: output block data
                print('Last downloaded block: {}'.format(last_block.id)) # TODO: output block data
                print('WTF: {}'.format(last_block.height))
        else:
            print('No new block found on this peer')

    def stop(self):
        print('Stopping blockchain')

    def rollback_current_round(self):
        # TODO: implement this
        print('Rollback current round is not yet implemented')
        pass

    def fork_block(self, block):
        # TODO:
        print('FORKING')
        raise NotImplementedError()

    def is_synced(self, last_block):
        current_time = time.get_time()
        blocktime = self.app.config.get_milestone(last_block.height)['blocktime']
        return (current_time - last_block.timestamp) < (3 * blocktime)

    def _handle_exception_block(self, block):
        forged_block = self.database.get_block_by_id(block.id)
        if forged_block:
            return BLOCK_REJECTED

        print('Block {} ({}) forcibly accecpted'.format(block.height, block.id))
        return self._handle_accepted_block(block)

    def _hande_verification_failed(self, block):
        # TODO:
        # this.blockchain.transactionPool.purgeSendersWithInvalidTransactions(this.block);
        return BLOCK_REJECTED

    def _handle_accepted_block(self, block):
        print('====== Handle apply block ======')
        self.database.apply_block(block)

        # TODO: a bunch of stuff regarding forked blocks, doing stuff to
        # transaction pool, reseting a wakeup, setting last block etc etc.
        return BLOCK_ACCEPTED

    def _validate_generator(self, block):
        delegates = self.database.get_active_delegates(block.height)
        slot_number = slots.get_slot_number(block.height, block.timestamp)
        generator_username = self.database.wallets.find_by_public_key(
            block.generator_public_key
        ).username
        forging_delegate = None

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
            # TODO: This return is not in the official ark core implementation!
            return False

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
                delegates = self.database.get_active_delegates(block.height)

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

    def process_block(self, block, last_block):
        print()
        print()
        print('Started processing block {}'.format(block.id))
        print(block.__dict__)

        print('Last block height: {}'.format(last_block.height))

        if is_block_exception(block):
            return self._handle_exception_block(block)

        is_verified, errors = block.verify()
        if not is_verified:
            print(errors)
            return self._hande_verification_failed(block)

        is_valid_generator = self._validate_generator(block)

        is_chained = is_block_chained(last_block, block)
        if not is_chained:
            return self._handle_unchained_block(block, last_block, is_valid_generator)

        if not is_valid_generator:
            return BLOCK_REJECTED

        contains_forged_transactions = self._block_contains_forged_transactions(block)
        if contains_forged_transactions:
            return BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED

        return self._handle_accepted_block(block)







