import os

from waitress import serve

from flask import Flask
from .views.peer import PeerView, BlockView, TransactionView, BlockCommonView

from .external import close_db


def create_app():
    app = Flask('p2p')

    app.teardown_appcontext(close_db)

    app.add_url_rule('/peer/status', view_func=PeerView.as_view('peer'))
    app.add_url_rule('/peer/blocks', view_func=BlockView.as_view('block'))
    app.add_url_rule('/peer/blocks/common', view_func=BlockCommonView.as_view('block_common'))
    app.add_url_rule('/peer/transactions', view_func=TransactionView.as_view('transaction'))
    return app


def start_server():
    app = create_app()
    serve(app, host=os.environ.get('SERVER_HOST', '127.0.0.1'), port=8080)
