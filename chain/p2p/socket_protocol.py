import asyncio
import logging
import logging.config

import websockets
from websockets.exceptions import ConnectionClosed
from websockets.framing import OP_CLOSE, OP_TEXT, encode_data, parse_close
from websockets.protocol import State

logger = logging.getLogger(__name__)


class SCSocketServerProtocol(websockets.WebSocketServerProtocol):
    ping_key = "ping"

    async def ping(self, data=None):
        await self.ensure_open()
        if data is None:
            data = "#1"
        if data is not None:
            data = encode_data(data)

        # Protect against duplicates if a payload is explicitly set.
        if self.ping_key in self.pings:
            raise ValueError("already waiting for a pong with the same data")
        self.pings[self.ping_key] = self.loop.create_future()

        await self.write_frame(True, OP_TEXT, data)

        return asyncio.shield(self.pings[self.ping_key])

    async def pong(self, data=None):
        await self.ensure_open()
        if data is None:
            data = "#2"
        if data is not None:
            data = encode_data(data)
        await self.write_frame(True, OP_TEXT, data)

    async def read_data_frame(self, max_size):
        """
        Read a single data frame from the connection.
        Process control frames received before the next data frame.
        Return ``None`` if a close frame is encountered before any data frame.
        """
        # 6.2. Receiving Data
        while True:
            frame = await self.read_frame(max_size)

            # 5.5. Control Frames
            if frame.opcode == OP_CLOSE:
                # 7.1.5.  The WebSocket Connection Close Code
                # 7.1.6.  The WebSocket Connection Close Reason
                self.close_code, self.close_reason = parse_close(frame.data)
                try:
                    # Echo the original data instead of re-serializing it with
                    # serialize_close() because that fails when the close frame
                    # is empty and parse_close() synthetizes a 1005 close code.
                    await self.write_close_frame(frame.data)
                except ConnectionClosed:
                    # It doesn't really matter if the connection was closed
                    # before we could send back a close frame.
                    pass
                return None

            elif frame.opcode == OP_TEXT:
                # PING
                if frame.data == b"#1":
                    # Answer pings.
                    logger.debug(
                        "%s: %s - received ping, sending pong: %s",
                        self.remote_address,
                        self.side,
                        frame.data or "[empty]",
                    )
                    await self.pong()
                    continue
                # PONG
                elif frame.data == b"#2":
                    # Acknowledge pings on solicited pongs.
                    if self.ping_key in self.pings:
                        logger.debug(
                            "%s: %s - received solicited pong: %s",
                            self.remote_address,
                            self.side,
                            frame.data or "[empty]",
                        )
                        # Acknowledge all pings up to the one matching this pong.
                        ping = self.pings[self.ping_key]
                        if not ping.done():
                            ping.set_result(None)
                        del self.pings[self.ping_key]
                    else:
                        logger.debug(
                            "%s - received unsolicited pong: %s",
                            self.side,
                            frame.data or "[empty]",
                        )
                    continue

            return frame

    def abort_pings(self):
        """
        Raise ConnectionClosed in pending keepalive pings.
        They'll never receive a pong once the connection is closed.
        """
        assert self.state is State.CLOSED
        exc = self.connection_closed_exc()

        for ping in self.pings.values():
            ping.set_exception(exc)
            # If the exception is never retrieved, it will be logged when ping
            # is garbage-collected. This is confusing for users.
            # Given that ping is done (with an exception), canceling it does
            # nothing, but it prevents logging the exception.
            ping.cancel()

        if self.pings:
            pings_hex = ", ".join(ping_id or "[empty]" for ping_id in self.pings)
            logger.debug("server - aborted pending ping: %s", pings_hex)
