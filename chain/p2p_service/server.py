import os

from pyramid.config import Configurator

from waitress import serve

from paste.translogger import TransLogger


def create_app():
    settings = {
        # 'debug_notfound': False,
        # 'debug_routematch': False,
        'pyramid.debug_all': True,

    }

    with Configurator(settings=settings) as config:
        config.scan('.views.common')

        config.scan('.views.internal')
        config.add_route('block_store', '/internal/blocks')

        config.scan('.views.peer')
        config.add_route('peer_status', '/peer/status')
        config.add_route('peer_blocks', '/peer/blocks')
        config.add_route('peer_transactions', '/peer/transactions')
        config.add_route('peer_common_blocks', '/peer/blocks/common')
        # config.add_route('peer_list', '/peer/list')

        app = config.make_wsgi_app()
        app = TransLogger(app, setup_console_handler=True)

    return app


def start_server():
    app = create_app()
    serve(app, host=os.environ.get('SERVER_HOST', '127.0.0.1'), port=8080)
