from chain.common.interfaces import IPlugin

from .manager import PeerManager


class Plugin(IPlugin):
    name = 'peers'

    def register(self):
        return PeerManager()
