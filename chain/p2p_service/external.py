from flask import g

from chain.common.plugins import load_plugin


def get_db():
    if 'db' not in g:
        g.db = load_plugin('chain.plugins.database')
    return g.db


def get_peer_manager():
    if 'peer_manager' not in g:
        g.peer_manager = load_plugin('chain.plugins.peers')
    return g.peer_manager


def get_process_queue():
    if 'process_queue' not in g:
        g.process_queue = load_plugin('chain.plugins.process_queue')
    return g.process_queue


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
