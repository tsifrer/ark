
from ark.interfaces.plugin import IPlugin

from .database import Database

class Plugin(IPlugin):
    name = 'database'
    pass

    def register(self):
        db = Database()
        db.connect()
        return db

