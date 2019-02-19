import json
# from transitions import Machine
from transitions.extensions import HierarchicalMachine as Machine
from ark.crypto.models.block import Block
from .utils import is_block_chained, is_block_exception

STATE_STOPPED = 'stopped'
STATE_STARTING = 'starting'
STATE_EXITING = 'exiting'
STATE_ROLLBACKING = 'rollbacking'
STATE_SYNC = 'sync'
STATE_SYNC_SYNCING = 'syncing'
STATE_SYNC_DOWNLOADING = 'downloading'
STATE_NESTED_SYNC_SYNCING = '{}_{}'.format(STATE_SYNC, STATE_SYNC_SYNCING)
STATE_NESTED_SYNC_DOWNLOADING = '{}_{}'.format(STATE_SYNC, STATE_SYNC_DOWNLOADING)
STATE_IDLE = 'IDLE'

STATES = [
    {'name': STATE_STOPPED},
    {'name': STATE_STARTING, 'on_enter': ['on_start']},
    {
        'name': STATE_SYNC,
        'children': [
            {'name': STATE_SYNC_SYNCING, 'on_enter': ['on_sync_syncing']},
            {'name': STATE_SYNC_DOWNLOADING, 'on_enter': ['on_sync_downloading']},
        ],
        'initial': STATE_SYNC_SYNCING,
    },
    {'name': STATE_EXITING},
    {'name': STATE_ROLLBACKING, 'on_enter': ['on_rollback']},
    {'name': STATE_IDLE}
]

TRANSITIONS = [
    {'trigger': 'start', 'source': STATE_STOPPED, 'dest': STATE_STARTING},
    {'trigger': 'set_started', 'source': STATE_STARTING, 'dest': STATE_SYNC},
    {
        'trigger': 'exit',
        'source': STATE_STARTING,
        'dest': STATE_EXITING,
        'before': ['on_exit'],
    },
    {'trigger': 'rollback', 'source': STATE_STARTING, 'dest': STATE_ROLLBACKING},
    {'trigger': 'sync_blocks', 'source': STATE_NESTED_SYNC_SYNCING, 'dest': STATE_NESTED_SYNC_DOWNLOADING},
    {'trigger': 'set_syncing', 'source': STATE_NESTED_SYNC_DOWNLOADING, 'dest': STATE_NESTED_SYNC_SYNCING},
    {'trigger': 'set_idle', 'source': STATE_NESTED_SYNC_SYNCING, 'dest': STATE_IDLE},

]


class BlockchainMachine(Machine):
    def __init__(self, blockchain, app, database):
        self.app = app
        self.blockchain = blockchain
        self.db = database
        super().__init__(
            self, states=STATES, transitions=TRANSITIONS, initial=STATE_STOPPED
        )

    def on_sync_downloading(self):
        print('downloading harambe')
        last_block = self.db.get_last_block()
        blocks = self.blockchain.p2p.download_blocks(last_block.height)

        if blocks:
            is_chained = is_block_chained(last_block, blocks[0]) or is_block_exception(self.app, blocks[0])
            if is_chained:
                print('Downloaded {} new blocks accounting for a total of {} transactions'.format(
                    len(blocks), sum([x.number_of_transactions for x in blocks])
                ))

                for block in blocks:
                    self.blockchain.process_block(block)
                # TODO:
                # blockchain.enqueueBlocks(blocks);
                # blockchain.dispatch("DOWNLOADED");

            else:
                print('Downloaded block not accepted: {}'.format(blocks[0])) # TODO: output block data
                print('Last downloaded block: {}'.format(last_block)) # TODO: output block data
        else:
            print('No new block found on this peer')

        self.set_syncing()






    def on_sync_syncing(self):
        # TODO: this has much more functionality other than just downloading blocks
        print('on_sync_syncing')

        if self.blockchain.is_synced():
            print('Blockhain is syced!')
            self.set_idle()
        else:
            self.sync_blocks()


    def on_start(self):
        # TODO: change prints to loggers
        print('Starting the blockchain')
        try:
            block = self.db.get_last_block()

            # If block is not found in the db, insert a genesis block
            if not block:
                print('No block found in the database')
                block = Block(self.app.config['genesis_block'])
                if block.payload_hash != self.app.config['network']['nethash']:
                    print(
                        'FATAL: The genesis block payload hash is different from '
                        'the configured nethash'
                    )
                    self.exit()
                    return

                else:
                    self.db.save_block(block)

            # If database did not just restore database integrity, verify the blockchain
            if not self.db.restored_database_integrity:
                print('Verifying database integrity')
                is_valid, errors = self.db.verify_blockchain()
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

            active_delegates = self.db.get_active_delegates(block.height)
            if not active_delegates:
                # TODO: rollback_current_round doesn't do anything ATM
                self.blockchain.rollback_current_round()


            # TODO: Rebuild SPV stuff

            # TODO: the rest of the stuff

            # Rebuild wallets
            self.db.wallets.build()



            self.set_started()
        except Exception as e:
            raise e  # TODO:
            # TODO: log exception
            self.exit()

    def on_exit(self):
        # TODO: implement this
        print('Exiting')

    def on_rollback(self):
        # TODO: implement this
        # rollbackDatabase
        pass
