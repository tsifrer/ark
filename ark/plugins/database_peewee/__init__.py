from ark.interfaces.plugin import IPlugin

from .database import Database


class Plugin(IPlugin):
    name = 'database'
    pass

    def register(self, app):
        db = Database(app)
        db.connect()
        return db
