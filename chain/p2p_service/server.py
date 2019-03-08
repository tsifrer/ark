import os

from pyramid.config import Configurator

from waitress import serve


def create_app():
    with Configurator() as config:
        config.scan('.views.internal')
        config.add_route('block_store', '/internal/blocks')
        config.add_route('status', '/peer/status')
        config.add_route('peer_block_view', '/peer/blocks')

        app = config.make_wsgi_app()
    return app


def start_server():
    app = create_app()
    serve(app, host=os.environ.get('SERVER_HOST', '127.0.0.1'), port=8080)
