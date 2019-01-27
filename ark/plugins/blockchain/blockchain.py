from ark.interfaces.blockchain import IBlockchain
from ark.settings import PLUGINS

from .state_machine import BlockchainMachine


class Blockchain(IBlockchain):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.machine = BlockchainMachine()

    @property
    def state(self):
        return self.machine.state

    @property
    def database(self):
        return PLUGINS['database']

    def start(self):
        self.machine.start()
        # self.machine.stooopid()

    def stop(self):
        self.machine.stop()
