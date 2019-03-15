import os

from flask import Flask

from gunicorn.app.base import BaseApplication

from .external import close_db
from .views.peer import PeerView, BlockView, TransactionView, BlockCommonView


class P2PService(BaseApplication):

    def __init__(self):
        self.options = {
            'bind': '{}:{}'.format(os.environ.get('SERVER_HOST', '127.0.0.1'), '8080'),
            'workers': 1, #number_of_workers(),
            'accesslog': '-',
        }
        self.application = create_app()
        super().__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def create_app():
    app = Flask('p2p')

    app.teardown_appcontext(close_db)

    app.add_url_rule('/peer/status', view_func=PeerView.as_view('peer'))
    app.add_url_rule('/peer/blocks', view_func=BlockView.as_view('block'))
    app.add_url_rule('/peer/blocks/common', view_func=BlockCommonView.as_view('block_common'))
    app.add_url_rule('/peer/transactions', view_func=TransactionView.as_view('transaction'))
    return app


def start_server():
    P2PService().run()
