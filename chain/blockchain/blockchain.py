import math
from datetime import datetime
from random import randint
from time import sleep


from chain.blockchain.constants import (
    BLOCK_ACCEPTED,
    BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED,
    BLOCK_REJECTED,
)
from chain.blockchain.utils import is_block_chained
from chain.common.config import config
from chain.common.exceptions import PeerNotFoundException
from chain.common.plugins import load_plugin
from chain.crypto import slots, time
from chain.crypto.objects.block import Block
from chain.crypto.utils import calculate_round, is_block_exception, is_new_round


class Blockchain(object):
    """Blockchain class holds everything for running a successfull relay worker.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database = load_plugin("chain.plugins.database")
        self.process_queue = load_plugin("chain.plugins.process_queue")
        self.peers = load_plugin("chain.plugins.peers")
        self.peers.setup()

    def start(self):
        """Starts the blockchain. Depending of the state of the blockchain it will
        decide what needs to be done in order to correctly start syncing.
        """
        print("Starting the blockchain")

        apply_genesis_round = False
        try:
            block = self.database.get_last_block()

            # If block is not found in the db, insert a genesis block
            if not block:
                print("No block found in the database")
                block = Block.from_dict(config.genesis_block)
                if block.payload_hash != config.network["nethash"]:
                    print(
                        "FATAL: The genesis block payload hash is different from "
                        "the configured nethash"
                    )
                    self.stop()
                    return

                else:
                    self.database.save_block(block)
                    apply_genesis_round = True

            print("Verifying database integrity")
            is_valid = False
            errors = None
            for _ in range(5):
                is_valid, errors = self.database.verify_blockchain()
                if is_valid:
                    break
                else:
                    print("Database is corrupted: {}".format(errors))
                    milestone = config.get_milestone(block.height)
                    previous_round = math.floor(
                        (block.height - 1) / milestone["activeDelegates"]
                    )
                    if previous_round <= 1:
                        raise Exception(
                            "FATAL: Database is corrupted: {}".format(errors)
                        )

                    print("Rolling back to round {}".format(previous_round))
                    self.database.rollback_to_round(previous_round)
                    print("Rolled back to round {}".format(previous_round))
            else:
                raise Exception(
                    "FATAL: After rolling back for 5 rounds, database is still "
                    "corrupted: {}".format(errors)
                )

            print("Verified database integrity")

            # if (stateStorage.networkStart) {
            #     await blockchain.database.buildWallets(block.data.height);
            #     await blockchain.database.saveWallets(true);
            #     await blockchain.database.applyRound(block.data.height);
            #     await blockchain.transactionPool.buildWallets();

            #     return blockchain.dispatch("STARTED");
            # }

            print("Last block in database: {}".format(block.height))

            # if the node is shutdown between round, the round has already been applied
            # so we delete it to start a new, fresh round
            if is_new_round(block.height + 1):
                current_round, _, _ = calculate_round(block.height + 1)
                print(
                    "Start of new round detected {}. Removing it in order to correctly "
                    "start the chain with new round.".format(current_round)
                )
                self.database.delete_round(current_round)

            # Rebuild wallets
            self.database.wallets.build()

            if apply_genesis_round:
                self.database.apply_round(block.height)

            self.sync_chain()

            print("Blockhain is syced!")

            # Blockchain was just synced, so remove all blocks from process queue
            # as it was just synced. We clear it only on the start of the chain, to
            # awoid processing old blocks. If we ever run sync while it's already
            # runing, we don't want to run clear after sync as that might leave us
            # with missing blocks which will cause the blockchain to always sync back
            # rather than sync by accepting block from peers.
            self.process_queue.clear()

            self.consume_queue()
        except Exception as e:
            self.stop()
            # TODO: log exception
            raise e  # TODO:

    def sync_blocks_from_random_peer(self, last_block):
        """Fetches blocks after the last_block.height from random peer and processes
        them

        :param Block last_block: Last crypto Block object that is in the database
        """
        print()
        print()
        print("Fetching blocks from height {}".format(last_block.height))
        blocks = self.peers.fetch_blocks(last_block.height)

        if blocks:
            print("chained", is_block_chained(last_block, blocks[0]))
            print("exception", is_block_exception(blocks[0]))
            is_chained = is_block_chained(last_block, blocks[0]) or is_block_exception(
                blocks[0]
            )
            if is_chained:
                print(
                    "Downloaded {} new blocks accounting for a total of {} "
                    "transactions".format(
                        len(blocks), sum([x.number_of_transactions for x in blocks])
                    )
                )

                for block in blocks:
                    status = self.process_block(block, last_block)
                    print("Block {} was {}".format(block.id, status))
                    if status == BLOCK_ACCEPTED:
                        last_block = block
                    else:
                        # TODO: Think about banning the peer at this point as it's most
                        # likely that it's a bad peer
                        print(block.to_json())
                        print(
                            "Block {} was {}. Skipping all other blocks in this "
                            "batch".format(block.id, status)
                        )
                        raise
            else:
                # TODO: Think about banning the peer at this point as it's most
                # likely that it's a bad peer
                print(
                    "First block in the current batch of block is not chained. "
                    "Skipping all blocks in this batch."
                )
        else:
            print("No new block found on this peer")

    def sync_chain(self):
        """Syncs the chain up to the latest height by fetching the blocks from random
        peers.
        """
        start = datetime.now()
        print("Started synching", start)
        while True:
            last_block = self.database.get_last_block()
            if not self.is_synced(last_block):
                try:
                    self.sync_blocks_from_random_peer(last_block)
                except PeerNotFoundException as e:
                    print(str(e))
                    print(
                        "Waiting for 1 second before continuing to give peers time to "
                        "populate"
                    )
                    sleep(1)
            else:
                break
            print("Time taken", datetime.now() - start)
        print("Done syncing", datetime.now() - start)

    def stop(self):
        print("Stopping blockchain")

    def recover_from_fork(self):
        """Recover from fork. Reverts a random number of blocks.
        """
        print("Starting fork recovery")
        # Revert a random number of blocks. Somewhere between 4 and 102
        n_blocks = randint(4, 102)
        self.revert_blocks(n_blocks)
        # TODO:
        # stateStorage.numberOfBlocksToRollback = null;

        # logger.info(`Removed ${pluralize("block", random, true)}`);

        # await blockchain.transactionPool.buildWallets();
        # await blockchain.p2p.refreshPeersAfterFork();

    def revert_blocks(self, n_blocks):
        """Reverts last N blocks

        :param int n_blocks: number of blocks to revert
        """
        block = self.database.get_last_block()
        print(
            "Reverting {} blocks. Reverting to height {}".format(
                n_blocks, block.height - n_blocks
            )
        )
        for _ in range(n_blocks):
            if block.height == 1:
                print("Can't revert genesis block.")
                break

            self.database.revert_block(block)
            # TODO: Transaction pool stuff
            # if (this.transactionPool) {
            #     await this.transactionPool.addTransactions(lastBlock.transactions);
            # }
            print("Successfully reverted block {}".format(block.id))

            block = self.database.get_last_block()

        self.process_queue.clear()

    def is_synced(self, last_block):
        """Checks if blockchain is synced to at least second to last height

        :param Block last_block: last block that is in the database
        """
        current_time = time.get_time()
        blocktime = config.get_milestone(last_block.height)["blocktime"]
        return (current_time - last_block.timestamp) < (3 * blocktime)

    def _handle_exception_block(self, block):
        forged_block = self.database.get_block_by_id(block.id)
        if forged_block:
            return BLOCK_REJECTED

        print("Block {} ({}) forcibly accecpted".format(block.height, block.id))
        return self._handle_accepted_block(block)

    def _hande_verification_failed(self, block):
        # TODO:
        # this.blockchain.transactionPool.purgeSendersWithInvalidTransactions(this.block);
        return BLOCK_REJECTED

    def _handle_accepted_block(self, block):
        print("====== Handle apply block ======")
        self.database.apply_block(block)

        # TODO: a bunch of stuff regarding forked blocks, doing stuff to
        # transaction pool, reseting a wakeup, setting last block etc etc.
        return BLOCK_ACCEPTED

    def _validate_generator(self, block):
        delegates = self.database.get_active_delegates(block.height)
        if not delegates:
            print("Could not find delegates for block height {}".format(block.height))
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
                "Delegate {} ({}) not allowed to forge, should be {} ({})".format(
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
                "Could not decide if delegate {} ({}) is allowed to forge block "
                "{}".format(
                    generator_username, block.generator_public_key, block.height
                )
            )
            # TODO: This return is not in the official ark core implementation!
            return False

        print(
            "Delegate {} ({}) allowed to forge block {}".format(
                generator_username, block.generator_public_key, block.height
            )
        )
        return True

    def _handle_unchained_block(self, block, last_block, is_valid_generator):
        if block.height > last_block.height + 1:
            print(
                (
                    "Blockchain not ready to accept new block at height {}. "
                    "Last block: {}"
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
            print("Block {} just received".format(block.height))
            return BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED

        elif block.timestamp < last_block.timestamp:
            print(
                "Block {} disregarded, because the timestamp is lower than the previous"
                " timestamp".format(block.height)
            )
            return BLOCK_REJECTED

        else:
            if is_valid_generator:
                print("Detect double forging by {}".format(block.generator_public_key))
                delegates = self.database.get_active_delegates(block.height)

                is_active_delegate = False
                for delegate in delegates:
                    if delegate.public_key == block.generator_public_key:
                        is_active_delegate = True
                        break

                if is_active_delegate:
                    self.recover_from_fork()
                return BLOCK_REJECTED

            print(
                (
                    "Forked block disregarded because it is not allowed to be forged. "
                    "Caused by delegate {}"
                ).format(block.generator_public_key)
            )
            return BLOCK_REJECTED

    def _block_contains_forged_transactions(self, block):
        if len(block.transactions) > 0:
            transaction_ids = [transaction.id for transaction in block.transactions]
            forged_ids = self.database.get_forged_transaction_ids(transaction_ids)
            if len(forged_ids) > 0:
                print(
                    "Block {} disregarded, because it contains already forged "
                    "transactions"
                )
                return True
        return False

    def process_block(self, block, last_block):
        print()
        print()
        print("Started processing block {}".format(block.id))
        print("Last block height: {}".format(last_block.height))

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
        while True:
            serialized_block = self.process_queue.pop_block()
            if serialized_block:
                last_block = self.database.get_last_block()
                block = Block.from_serialized(serialized_block)
                status = self.process_block(block, last_block)
                print(status)
                if status in [BLOCK_ACCEPTED, BLOCK_DISCARDED_BUT_CAN_BE_BROADCASTED]:
                    # TODO: Broadcast only current block
                    milestone = config.get_milestone(block.height)
                    current_slot = slots.get_slot_number(block.height, time.get_time())
                    if current_slot * milestone["blocktime"] <= block.timestamp:
                        # TODO: THIS IS MISSING
                        print("MISSING: IMPLEMENT BROADCASTING")
            else:
                # TODO: change this
                print("Nothing to process. Sleeping for 1 sec")
                sleep(1)

            # Our chain can get out of sync when it doesn't receive all the blocks
            # to the p2p endpoint, so if we're not in sync, force sync to the last
            # block
            last_block = self.database.get_last_block()
            if not self.is_synced(last_block):
                print("Force syncing with the network as we got out of sync")
                self.sync_chain()
                print("Done force syncing")
