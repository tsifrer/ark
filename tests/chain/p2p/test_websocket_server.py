import pytest

from chain.p2p.websocket_handlers import Handlers
from chain.p2p.websocket_server import ChainSocketHandler


@pytest.fixture
def socket(mocker):
    ws_handlers = Handlers()
    ws = mocker.MagicMock()
    ws.remote_addres.return_value = ('192.168.0.1', '4002')
    yield ChainSocketHandler(ws, ws_handlers)


# @pytest.mark.asyncio
# async def test_handle_event(socket):
#     # ws_handlers = Handlers()
#     # ws = mocker.MagicMock()
#     # ws.remote_addres.return_value = ('192.168.0.1', '4002')
#     # handler = ChainSocketHandler(ws, ws_handlers)

#     await socket.handle_event(123, "p2p.peer.getBlocks", {"harambe": "omg", "lastBlockHeight": 300})
