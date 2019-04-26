from chain.common.interfaces import IPlugin


class Plugin(IPlugin):
    name = "database"

    def register(self):
        # TODO: Circular imports. Fix them in the future
        from .database import Database

        return Database()
