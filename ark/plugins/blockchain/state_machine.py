from transitions import Machine

STATE_STOPPED = 'stopped'
STATE_STARTING = 'starting'
STATE_STARTED = 'started'
STATE_EXIT = 'exit'

STATES = [
    {'name': STATE_STOPPED},
    {'name': STATE_STARTING, 'on_enter': ['on_start']},
    {'name': STATE_STARTED},
    {'name': STATE_EXIT},
]

TRANSITIONS = [
    {'trigger': 'start', 'source': STATE_STOPPED, 'dest': STATE_STARTING},
    {'trigger': 'set_started', 'source': STATE_STARTING, 'dest': STATE_STARTED},
    {
        'trigger': 'exit',
        'source': STATE_STARTING,
        'dest': STATE_EXIT,
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
        print('Starting the blockchain')
        try:
            block = self.db.get_last_block()

            if not block:
                print('No block found in the database')

            print(self.app.config['genesis_block'])

            self.set_started()
        except Exception as e:
            raise e  # TODO:
            # TODO: log exception
            self.exit()

    def on_exit(self):
        # TODO: implement this
        print('Exiting')
