from chain.common.interfaces import IPlugin

from .p2p import P2P


class Plugin(IPlugin):
    name = 'p2p'

    def register(self, app):
        p2p = P2P(app)
        return p2p


from pyramid.config import Configurator

from waitress import serve


def create_app():
    with Configurator() as config:
        config.scan('.views.internal')
        config.add_route('hello', '/')

        app = config.make_wsgi_app()
    return app


def start_server():
    app = create_app()
    serve(app, host='127.0.0.1', port=8080)
