from transitions import Machine

from ark.crypto.models.block import Block

STATE_STOPPED = 'stopped'
STATE_STARTING = 'starting'
STATE_STARTED = 'started'
STATE_EXITING = 'exiting'
STATE_ROLLBACKING = 'rollbacking'

STATES = [
    {'name': STATE_STOPPED},
    {'name': STATE_STARTING, 'on_enter': ['on_start']},
    {'name': STATE_STARTED},
    {'name': STATE_EXITING},
    {'name': STATE_ROLLBACKING, 'on_enter': ['on_rollback']}
]

TRANSITIONS = [
    {'trigger': 'start', 'source': STATE_STOPPED, 'dest': STATE_STARTING},
    {'trigger': 'set_started', 'source': STATE_STARTING, 'dest': STATE_STARTED},
    {
        'trigger': 'exit',
        'source': STATE_STARTING,
        'dest': STATE_EXITING,
        'before': ['on_exit'],
    },
    {'trigger': 'rollback', 'source': STATE_STARTING, 'dest': STATE_ROLLBACKING},
]


class BlockchainMachine(Machine):
    def __init__(self, app, database):
        self.app = app
        self.db = database
        super().__init__(
            self, states=STATES, transitions=TRANSITIONS, initial=STATE_STOPPED
        )

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
                    return self.rollback()
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
            #stateStorage.setLastBlock(block);
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
            # Fast rebuild is only available if last block is older than a week
            block_age = self.app.time.get_time() - block.timestamp
            fast_rebuild = block_age > 3600 * 24 * 7 and self.app.config['fast_rebuild']
            print('Fast rebuild: {}'.format(fast_rebuild))
            if fast_rebuild:
                # self.rebuild() # TODO: this is a rabit hole
                return

            





            # TODO: the rest of the stuff



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
