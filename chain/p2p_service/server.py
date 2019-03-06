import os

from pyramid.config import Configurator

from waitress import serve


def create_app():
    with Configurator() as config:
        config.scan('.views.internal')
        config.add_route('block_store', '/blocks')

        app = config.make_wsgi_app()
    return app


def start_server():
    app = create_app()
    serve(app, host=os.environ.get('SERVER_HOST', '127.0.0.1'), port=8080)
