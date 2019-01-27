
from ark.interfaces.plugin import IPlugin

from .database import Database

class Plugin(IPlugin):
    name = 'database'
    pass

    def register(self, loop):
        db = Database(loop)
        db.connect()
        return db

