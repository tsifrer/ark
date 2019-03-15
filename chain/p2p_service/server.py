import json
import os

from flask import Flask, current_app, jsonify

from gunicorn.app.base import BaseApplication

from werkzeug.exceptions import HTTPException

from .exceptions import P2PException
from .external import close_db
from .views.peer import PeerView, BlockView, TransactionView, BlockCommonView


def _handle_api_errors(ex):
    if isinstance(ex, HTTPException):
        data = {
            'success': False,
            'status_code': ex.code,
            'message': ex.description
        }
    elif isinstance(ex, P2PException):
        data = ex.to_dict()
    else:
        data = {
            'success': False,
            'status_code': 500,
            'message': 'Internal Server Error',
        }

    log = current_app.logger.debug
    if data['status_code'] >= 500:
        log = current_app.logger.error
    elif data['status_code'] >= 400:
        log = current_app.logger.debug
    log(json.dumps(data))
    return jsonify(data), data['status_code']


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

    app.register_error_handler(Exception, _handle_api_errors)

    app.add_url_rule('/peer/status', view_func=PeerView.as_view('peer'))
    app.add_url_rule('/peer/blocks', view_func=BlockView.as_view('block'))
    app.add_url_rule('/peer/blocks/common', view_func=BlockCommonView.as_view('block_common'))
    app.add_url_rule('/peer/transactions', view_func=TransactionView.as_view('transaction'))
    return app


def start_server():
    P2PService().run()
