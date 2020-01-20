import json
import http
import signal
import typing
import logging
import asyncio
import base64

import websockets
from websockets import WebSocketServerProtocol
from websockets.server import HTTPResponse
from websockets.http import Headers

from .types import Socket
from .utils import onlyfirst

logger: logging.Logger = logging.getLogger("websocks")


class TCPSocket(Socket):
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.r = reader
        self.w = writer

    async def recv(self, num: int = 4096) -> bytes:
        data = await self.r.read(num)
        logger.debug(f"<<< {data}")
        return data

    async def send(self, data: bytes) -> int:
        self.w.write(data)
        await self.w.drain()
        logger.debug(f">>> {data}")
        return len(data)

    def close(self) -> None:
        self.w.close()

    @property
    def closed(self) -> bool:
        return self.w.is_closing()


async def create_connection(host: str, port: int) -> TCPSocket:
    """create a TCP socket"""
    r, w = await asyncio.open_connection(host=host, port=port)
    return TCPSocket(r, w)


async def bridge(alice: Socket, bob: Socket) -> None:
    async def _bridge(sender: Socket, receiver: Socket) -> None:
        while True:
            data = await sender.recv()
            if not data:
                return
            await receiver.send(data)

    await onlyfirst(_bridge(alice, bob), _bridge(bob, alice))


class Server:
    def __init__(
        self,
        userlist: typing.Dict[str, str],
        *,
        host: str = "0.0.0.0",
        port: int = 8765,
    ):
        self.userlist = userlist
        self.host = host
        self.port = port

    async def _link(self, sock: WebSocketServerProtocol, path: str):
        logger.info(f"Connect from {sock.remote_address}")
        try:
            while True:
                data = await sock.recv()
                assert isinstance(data, str)
                request = json.loads(data)
                try:
                    remote = await create_connection(request["HOST"], request["PORT"])
                    await sock.send(json.dumps({"ALLOW": True}))
                except (OSError, asyncio.TimeoutError):
                    await sock.send(json.dumps({"ALLOW": False}))
                else:
                    try:
                        await bridge(sock, remote)
                    except TypeError:  # websocks closed
                        continue
                    finally:
                        if not remote.closed:
                            remote.close()
                        if sock.closed:
                            raise websockets.exceptions.ConnectionClosed(
                                sock.close_code
                            )

                await sock.send(json.dumps({"STATUS": "CLOSED"}))
                while True:
                    msg = await sock.recv()
                    if isinstance(msg, str):
                        break

        except (AssertionError, KeyError):
            await sock.close()
        except websockets.exceptions.ConnectionClosed:
            pass

    async def handshake(
        self, path: str, request_headers: Headers
    ) -> typing.Optional[HTTPResponse]:
        if not request_headers.get("Authorization"):
            return http.HTTPStatus.UNAUTHORIZED, {}, b""
        # parse credentials
        _type, _credentials = request_headers.get("Authorization").split(" ")
        username, password = base64.b64decode(_credentials).decode("utf8").split(":")
        if not (username in self.userlist and password == self.userlist[username]):
            logger.warning(f"Authorization Error: {username}:{password}")
            return http.HTTPStatus.UNAUTHORIZED, {}, b""

    async def run_server(self) -> typing.NoReturn:
        async with websockets.serve(
            self._link, host=self.host, port=self.port, process_request=self.handshake
        ) as server:
            logger.info(f"Websocks Server serving on {self.host}:{self.port}")

            def termina(signo, frame):
                logger.info(f"Websocks Server has closed.")
                raise SystemExit(0)

            signal.signal(signal.SIGINT, termina)
            signal.signal(signal.SIGTERM, termina)

            while True:
                await asyncio.sleep(1)

    def run(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run_server())
        loop.stop()
