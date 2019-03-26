import math
from datetime import datetime
from time import sleep


from .utils import is_block_chained
from .constants import (
    BLOCK_ACCEPTED,
    BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED,
    BLOCK_REJECTED,
)
from chain.crypto import time, slots
from chain.crypto.utils import is_block_exception
from chain.crypto.objects.block import Block
from chain.common.plugins import load_plugin
from chain.config import Config
from chain.common.exceptions import PeerNotFoundException


class Blockchain(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # load_plugins(self)
        self.database = load_plugin('chain.plugins.database')
        self.peers = load_plugin('chain.plugins.peers')
        self.peers.setup()

    def start(self):
        # TODO: change prints to loggers
        config = Config()
        print('Starting the blockchain')

        apply_genesis_round = False
        try:
            block = self.database.get_last_block()

            # If block is not found in the db, insert a genesis block
            if not block:
                print('No block found in the database')
                block = Block.from_dict(config['genesis_block'])
                if block.payload_hash != config['network']['nethash']:
                    print(
                        'FATAL: The genesis block payload hash is different from '
                        'the configured nethash'
                    )
                    self.stop()
                    return

                else:
                    self.database.save_block(block)
                    apply_genesis_round = True

            # If database did not just restore database integrity, verify the blockchain
            # if not self.database.restored_database_integrity:
            print('Verifying database integrity')
            is_valid = False
            errors = None
            for _ in range(5):
                is_valid, errors = self.database.verify_blockchain()
                if is_valid:
                    break
                else:
                    print('Database is corrupted: {}'.format(errors))
                    milestone = config.get_milestone(block.height)
                    previous_round = math.floor((block.height - 1) / milestone['activeDelegates'])
                    if previous_round <= 1:
                        raise Exception('FATAL: Database is corrupted: {}'.format(errors))

                    print('Rolling back to round {}'.format(previous_round))
                    self.database.rollback_to_round(previous_round)
                    print('Rolled back to round {}'.format(previous_round))
            else:
                raise Exception('FATAL: After rolling back for 5 rounds, database is still corrupted: {}'.format(errors))

            print('Verified database integrity')
            # else:
            #     print(
            #         'Skipping database integrity check after successful database '
            #         'recovery'
            #     )

            # TODO: figure this  out
            # // only genesis block? special case of first round needs to be dealt with
            # if (block.data.height === 1) {
            #     await blockchain.database.deleteRound(1);
            # }

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

            # delegate_wallets = self.database.wallets.load_active_delegate_wallets(562)

            # for wallet in delegate_wallets:
            #     print(wallet.public_key, wallet.username, wallet.vote_balance)

            if apply_genesis_round:
                self.database.apply_round(block.height)

            self.start_syncing()

            print('Blockhain is syced!')

            self.consume_queue()

        except Exception as e:
            raise e  # TODO:
            # TODO: log exception
            self.stop()

    def start_syncing(self):
        start = datetime.now()
        print('STARTED', start)
        while True:
            last_block = self.database.get_last_block()
            if not self.is_synced(last_block):
                try:
                    self.sync_blocks(last_block)
                except PeerNotFoundException as e:
                    print(str(e))
                    print('Waiting for 1 second before continuing to give peers time to populate')
                    sleep(1)
            else:
                break
            print('Time taken', datetime.now() - start)

        print('Done syncing', datetime.now() - start)

    def sync_blocks(self, last_block):
        print()
        print()
        print('downloading harambe')
        print()
        blocks = self.peers.download_blocks(last_block.height)

        if blocks:
            print('chained', is_block_chained(last_block, blocks[0]))
            print('exception', is_block_exception(blocks[0]))
            is_chained = is_block_chained(last_block, blocks[0]) or is_block_exception(
                blocks[0]
            )
            if is_chained:
                print(
                    'Downloaded {} new blocks accounting for a total of {} transactions'.format(
                        len(blocks), sum([x.number_of_transactions for x in blocks])
                    )
                )

                for block in blocks:
                    status = self.process_block(block, last_block)
                    print('Block {} was {}'.format(block.id, status))
                    # TODO: this might be completely wrong to handle
                    if status == BLOCK_ACCEPTED:
                        last_block = block
                    else:
                        msg = 'Block {} was {}. Skipping all other blocks in this batch'.format(
                            block.id, status
                        )
                        print(block.to_json())
                        print(msg)
                        raise Exception(msg)
                # TODO:
                # blockchain.enqueueBlocks(blocks);
                # blockchain.dispatch("DOWNLOADED");

            else:
                print(
                    'Last downloaded block: {}'.format(last_block.id)
                )  # TODO: output block data
                print('WTF: {}'.format(last_block.height))
                raise Exception('Downloaded block not accepted: {}'.format(blocks[0].id))
        else:
            print('No new block found on this peer')

    def stop(self):
        print('Stopping blockchain')

    # def rollback_current_round(self):
    #     # TODO: implement this
    #     print('Rollback current round is not yet implemented')
    #     pass

    def fork_block(self, block):
        # TODO:
        print('FORKING')
        raise NotImplementedError()

    def is_synced(self, last_block):
        current_time = time.get_time()
        config = Config()
        blocktime = config.get_milestone(last_block.height)['blocktime']
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
        if not delegates:
            print('Could not find delegates for block height {}'.format(block.height))
            return False
        slot_number = slots.get_slot_number(block.height, block.timestamp)
        generator_username = self.database.wallets.find_by_public_key(
            block.generator_public_key
        ).username
        forging_delegate = None

        forging_delegate = delegates[slot_number % len(delegates)]

        if (
            forging_delegate
            and forging_delegate.public_key != block.generator_public_key
        ):
            forging_username = self.database.wallets.find_by_public_key(
                forging_delegate.public_key
            ).username
            print(
                'Delegate {} ({}) not allowed to forge, should be {} ({})'.format(
                    generator_username,
                    block.generator_public_key,
                    forging_username,
                    forging_delegate.public_key,
                )
            )
            return False
        # TODO: this seems weird as we can't decide if delegate is allowed to forge, but
        # we still accept it as a valid generator
        if not forging_delegate:
            print(
                'Could not decide if delegate {} ({}) is allowed to forge block {}'.format(
                    generator_username, block.generator_public_key, block.height
                )
            )
            # TODO: This return is not in the official ark core implementation!
            return False

        print(
            'Delegate {} ({}) allowed to forge block {}'.format(
                generator_username, block.generator_public_key, block.height
            )
        )
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
            print(
                "Block {} disregarded because it's already in blockchain".format(
                    block.height
                )
            )
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

    def consume_queue(self):
        queue = load_plugin('chain.plugins.process_queue')
        config = Config()
        while True:
            serialized_block = queue.pop_block()
            if serialized_block:
                print(serialized_block)
                last_block = self.database.get_last_block()
                block = Block.from_serialized(serialized_block)
                status = self.process_block(block, last_block)
                print(status)
                if status in [BLOCK_ACCEPTED, BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED]:
                    # TODO: Broadcast only current block
                    milestone = config.get_milestone(block.height)
                    current_slot = slots.get_slot_number(block.height, time.get_time())
                    if current_slot * milestone['blocktime'] <= block.timestamp:
                        # TODO: THIS IS MISSING
                        print('MISSING: IMPLEMENT BROADCASTING')
            else:
                # TODO: change this
                print('Nothing to process. Sleeping for 1 sec')
                sleep(1)

            # Our chain can get out of sync when it doesn't receive all the blocks
            # to the p2p endpoint, so if we're not in sync, force sync to the last
            # block
            last_block = self.database.get_last_block()
            if not self.is_synced(last_block):
                print('Force syncing with the network as we got out of sync')
                self.start_syncing()
                print('Done force syncing')
