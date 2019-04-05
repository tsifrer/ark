from chain.common.interfaces import IPlugin

from .pool import Pool


class Plugin(IPlugin):
    name = "transaction_pool"

    def register(self):
        return Pool()
