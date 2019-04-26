from chain.common.interfaces import IPlugin


class Plugin(IPlugin):
    name = "transaction_pool"

    def register(self):
        # TODO: Circular imports. Fix them in the future
        from .pool import Pool

        return Pool()
