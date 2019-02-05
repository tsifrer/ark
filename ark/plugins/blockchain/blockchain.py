from ark.interfaces.blockchain import IBlockchain
from ark.settings import PLUGINS

from .state_machine import BlockchainMachine


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