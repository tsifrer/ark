from ark.interfaces.plugin import IPlugin

from .p2p import P2P


class Plugin(IPlugin):
    name = 'p2p'

    def register(self, app):
        p2p = P2P(app)
        return p2p
