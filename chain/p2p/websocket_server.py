import asyncio
import functools
import json
import logging
import logging.config
import os
import sys
import uuid

import websockets

from chain.common.utils import get_chain_version
from chain.p2p.rate_limiter import AsyncRateLimiter
from chain.p2p.socket_protocol import SCSocketServerProtocol
from chain.p2p.websocket_handlers import Handlers
from chain.plugins.peers.tasks import add_peer
from chain.plugins.peers.utils import ip_is_blacklisted

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
        }
    },
    "loggers": {
        "peewee": {"propagate": False, "level": "WARNING", "handlers": ["console"]},
        "websockets": {"propagate": False, "level": "WARNING", "handlers": ["console"]},
        "asyncio": {"propagate": False, "level": "WARNING", "handlers": ["console"]},
        "chain.p2p.socket_protocol": {
            "propagate": False,
            "level": "WARNING",
            "handlers": ["console"],
        },
        "": {"handlers": ["console"], "level": "DEBUG"},
    },
}

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class ChainSocketHandler(object):
    def __init__(self, websocket, handlers):
        super().__init__()
        self.handlers = handlers
        self.ws = websocket
        self.ip = self.ws.remote_address[0]
        # Add websocket IP as peer
        self._add_as_peer()

    def log_error(self, msg, *args):
        logger.error("{}: {}".format(self.ip, msg), *args)

    def log_info(self, msg, *args):
        logger.info("{}: {}".format(self.ip, msg), *args)

    def _add_as_peer(self):
        self.log_info("Weboscket connected")
        if not ip_is_blacklisted(self.ip):
            # TODO: Maybe get Port from the peer getStatus config?
            add_peer(ip=self.ip, port=4002, chain_version=None, nethash=None, os=None)

    async def send(self, cid, data, headers=None):
        if not headers:
            last_block = await self.handlers.get_last_block()
            headers = {
                "version": get_chain_version(),
                "height": last_block.height,
                "port": 4002,
            }
        await self.ws.send(
            json.dumps({"rid": cid, "data": {"data": data, "headers": headers}})
        )

    def lost_connection(self):
        self.log_info("Websocket lost connection")

    async def handle_event(self, cid, event, data):
        if event == "p2p.peer.getBlocks":
            blocks = await self.handlers.get_blocks(data)
            await self.send(cid, blocks)

        elif event == "p2p.peer.postBlock":
            await self.handlers.post_block(data, self.ip)
            await self.send(cid, {})

        elif event == "p2p.peer.getCommonBlocks":
            common = await self.handlers.get_common_blocks(data)
            await self.send(cid, common)

        elif event == "p2p.peer.getStatus":
            status = await self.handlers.get_status()
            await self.send(cid, status)

        elif event == "p2p.peer.getPeers":
            # TODO: implement it properly
            await self.send(cid, [])

        elif event == "p2p.peer.postTransactions":
            # TODO: implement it properly
            accepted_transactions = await self.handlers.post_transactions(data, self.ip)
            await self.send(cid, accepted_transactions)

        else:
            self.log_error("Wrong event: %s", data)
            await self.send(
                json.dumps({"rid": cid, "error": {"message": "Event not supported"}})
            )


async def handle_rate_limit(websocket):
    print("Handle rate limit")
    await websocket.send(
        json.dumps(
            {"event": "#disconnect", "data": {"code": 4403, "data": "Forbidden"}}
        )
    )


async def ws_handler(websocket, path, handlers, rate_limiter):
    ip = websocket.remote_address[0]
    print(ip)
    if await rate_limiter.exceeds_rate_limit(ip):
        await handle_rate_limit(websocket)
        return

    socket = ChainSocketHandler(websocket, handlers)
    try:
        async for message in websocket:
            print("Handling: %s" % message)
            socket.log_info("Handling message: %s", message)
            data = json.loads(message)
            event = data["event"]
            if await rate_limiter.exceeds_rate_limit(ip, event):
                await handle_rate_limit(websocket)
                break

            # TODO: data["data"]["headers"] validation

            # TODO: Make #handshake mandatory, before we accept other stuff
            if event == "#handshake":
                await websocket.send(
                    json.dumps(
                        {
                            "rid": data["cid"],
                            "data": {
                                "id": str(uuid.uuid4()),
                                "pingTimeout": 10000,
                                "isAuthenticated": False,
                            },
                        }
                    )
                )

            elif event == "#disconnect":
                break

            else:
                await socket.handle_event(data["cid"], event, data["data"]["data"])
    except Exception as e:
        socket.log_error("%s", e)
        raise e
    finally:
        socket.lost_connection()


async def _socketcluster_path_check(path, request_headers):
    if path != "/socketcluster/":
        print("Wrong path {}".format(path))
        return 404, [], b"404 Not Found\n"


def start_server():
    host = os.environ.get("WS_HOST", "127.0.0.1")
    port = os.environ.get("WS_PORT", "4002")
    print("Starting server on {}:{}".format(host, port))

    rate_limiter = AsyncRateLimiter()
    handlers = Handlers()
    bound_handler = functools.partial(
        ws_handler, handlers=handlers, rate_limiter=rate_limiter
    )
    start_server = websockets.serve(
        bound_handler,
        host,
        port,
        create_protocol=SCSocketServerProtocol,
        process_request=_socketcluster_path_check,
        ping_interval=8,
        ping_timeout=10,
    )

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
