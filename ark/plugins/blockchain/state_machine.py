from transitions import Machine

from ark.crypto.models.block import Block

STATE_STOPPED = 'stopped'
STATE_STARTING = 'starting'
STATE_STARTED = 'started'
STATE_EXITING = 'exiting'

STATES = [
    {'name': STATE_STOPPED},
    {'name': STATE_STARTING, 'on_enter': ['on_start']},
    {'name': STATE_STARTED},
    {'name': STATE_EXITING},
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


            print(self.db.verify_blockchain())
                # audit = self.db.verify


        



            self.set_started()
        except Exception as e:
            raise e  # TODO:
            # TODO: log exception
            self.exit()

    def on_exit(self):
        # TODO: implement this
        print('Exiting')
