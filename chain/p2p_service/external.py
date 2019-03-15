from chain.common.plugins import load_plugin

from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = load_plugin('chain.plugins.database')
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
