from ark.interfaces.plugin import IPlugin

from .blockchain import Blockchain

class Plugin(IPlugin):
    name = 'database'
    pass

    def register(self, app):
        blockchain = Blockchain(app)
        blockchain.start()
        print(blockchain.state)
        return blockchain
