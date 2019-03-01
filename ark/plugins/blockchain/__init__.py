from ark.interfaces.plugin import IPlugin

from .blockchain import Blockchain


class Plugin(IPlugin):
    name = 'database'

    def register(self, app):
        blockchain = Blockchain(app)

        # blockchain.start()

        blockchain.p2p.start()

        return blockchain
