from transitions import Machine

STATE_UNINITIALIZED = 'uninitialized'
STATE_INITIALIZE = 'initialize'
STATE_STOPPED = 'stopped'

STATES = [
    {'name': STATE_UNINITIALIZED},
    {'name': STATE_INITIALIZE},
    {'name': STATE_STOPPED, 'on_enter': ['stooopid']},
]

TRANSITIONS = [
    {
        'trigger': 'start',
        'source': STATE_UNINITIALIZED,
        'dest': STATE_INITIALIZE
    },
    {
        'trigger': 'stop',
        'source': [STATE_UNINITIALIZED, STATE_INITIALIZE],  # TODO: this can probably be `*`
        'dest': STATE_STOPPED
    },
]


class BlockchainMachine(Machine):

    def __init__(self):
        super().__init__(
            self,
            states=STATES,
            transitions=TRANSITIONS,
            initial=STATE_UNINITIALIZED
        )

    def on_enter_initialize(self):
        print('INITIALIZEEEE')

    def stooopid(self):
        print(self.state)
        print('STOPPING THIS SHIEEEET')
