import asyncio
import logging
import os
import ssl
from contextlib import suppress
from http import HTTPStatus
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Union

from aiohttp import ClientSession, TCPConnector
from aiohttp import ClientTimeout
from aiohttp import ServerConnectionError
from cryptography.hazmat.primitives._serialization import Encoding, PrivateFormat, BestAvailableEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from websockets.client import WebSocketClientProtocol
from websockets.client import connect
from websockets.connection import State
from websockets.exceptions import ConnectionClosed

import pysignalr.exceptions as exceptions
from pysignalr import NegotiationTimeout
from pysignalr.messages import CompletionMessage
from pysignalr.messages import Message
from pysignalr.messages import PingMessage
from pysignalr.protocol.abstract import Protocol
from pysignalr.transport.abstract import ConnectionState
from pysignalr.transport.abstract import Transport
from pysignalr.utils import get_connection_url
from pysignalr.utils import get_negotiate_url
from pysignalr.utils import replace_scheme

DEFAULT_MAX_SIZE = 2 ** 20  # 1 MB
DEFAULT_PING_INTERVAL = 10
DEFAULT_CONNECTION_TIMEOUT = 10

_logger = logging.getLogger('pysignalr.transport')

default_ca = """-----BEGIN CERTIFICATE-----
MIIELTCCAxWgAwIBAgIURU7qH0JVb8BlRd7S/LdrHi9fBEAwDQYJKoZIhvcNAQEL
BQAwgaUxCzAJBgNVBAYTAkdCMQ8wDQYDVQQIDAZTdXNzZXgxETAPBgNVBAcMCEJy
aWdodG9uMRowGAYDVQQKDBFTZW5zb3IgQWNjZXNzIEx0ZDEMMAoGA1UECwwDVk1T
MR8wHQYDVQQDDBZTZW5zb3IgQWNjZXNzIFZNUyBSb290MScwJQYJKoZIhvcNAQkB
FhhzYWxlc0BzZW5zb3JhY2Nlc3MuY28udWswHhcNMjIwNDIwMDk0NTQ5WhcNMzIw
NDE3MDk0NTQ5WjCBpTELMAkGA1UEBhMCR0IxDzANBgNVBAgMBlN1c3NleDERMA8G
A1UEBwwIQnJpZ2h0b24xGjAYBgNVBAoMEVNlbnNvciBBY2Nlc3MgTHRkMQwwCgYD
VQQLDANWTVMxHzAdBgNVBAMMFlNlbnNvciBBY2Nlc3MgVk1TIFJvb3QxJzAlBgkq
hkiG9w0BCQEWGHNhbGVzQHNlbnNvcmFjY2Vzcy5jby51azCCASIwDQYJKoZIhvcN
AQEBBQADggEPADCCAQoCggEBAKQQYYHRdfuwrvlPQ6qfaijtND2VIpo1KhN5AFnG
U6q79Iu1BerKFlazdSL1TsPEWdmHIvBnpLkzuW7IF4gGRzgRDPSK0v4Wjhl6a1lD
g1qKTOX/Z4Kc9espFIrlbA6B4TrbQsbePMSyca+Ru+qHvO30qqqZUNGR5s7G8wVl
dIhzccUPWGm9C6TyjFfL8lwqBVjYcWDP/iAlDfw1tcPodL1qcEd3EKHkASL8D7iE
nFoLSEcW15VZ68cdCufRPfxCmL7FjddmiQ/itildV2szX5hWxlQik6GRArDrKpnE
Dqigx1vxyE5896fwHmu1z5jMK0kzx6pzgutDKqVpBxodUBUCAwEAAaNTMFEwHQYD
VR0OBBYEFB00pM6wNS3yIFERdLKviHr0l6o2MB8GA1UdIwQYMBaAFB00pM6wNS3y
IFERdLKviHr0l6o2MA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEB
ACMXKnIGKAR3teHMmsHyu9cwm+T25FWQShRoI+YRGSpVemnnmz6xpetDs6KDRVy4
nEMdq24QO03ME8Z7luCBu0VHaZCdteu4QBrd5obbDSbfkHYnPnhwBhG+FTQt6pc8
hGsHW92XNwnQiAXATKNI/kxeqzsXxoMpKgfbDTT8bnNMLIXL1JxZKpguXsxc6wOd
mx9B6Vfbh9UnNgtnxsQUu9dCO0Ukczfpq902xK0QiKjYslH5kiypBskuhWxcEY3y
+Z0K2OQmT3LfJ1s1GNj799EIlti4HX81GPMZsTi7sjHeff+lyOgj8ezAT+QtnxAP
1MNRXg3aviuwZbDS2Juguf8=
-----END CERTIFICATE-----"""


def pfx_to_pems(pfx_path, pfx_password):
    ''' Decrypts the .pfx file to be used with requests. '''
    pfx = Path(pfx_path).read_bytes()
    private_key, main_cert, add_certs = load_key_and_certificates(pfx, pfx_password.encode('utf-8'), None)

    key_file = NamedTemporaryFile(suffix='.pem', delete=False)
    key_file.write(private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8,
                                             BestAvailableEncryption(pfx_password.encode('utf-8'))))
    key_file.flush()

    cert_file = NamedTemporaryFile(suffix='.pem', delete=False)
    cert_file.write(main_cert.public_bytes(Encoding.PEM))
    cert_file.flush()

    ca_file = NamedTemporaryFile(suffix='.pem', delete=False)
    for ca in add_certs:
        ca_file.write(ca.public_bytes(Encoding.PEM))
    ca_file.flush()

    return key_file, cert_file, ca_file


def create_sslContext(p12_file, p12_pwd):
    # Loading System Defaults for TLS Client
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    p12_key_file = None
    p12_cert_file = None
    p12_ca_file = None
    if p12_file:
        if os.path.isfile(p12_file):
            # temporary files
            p12_key_file, p12_cert_file, p12_ca_file = pfx_to_pems(p12_file, p12_pwd)
            if os.stat(p12_key_file.name).st_size > 0:
                key_file = p12_key_file.name
            if os.stat(p12_cert_file.name).st_size > 0:
                cert_file = p12_cert_file.name
            if os.stat(p12_ca_file.name).st_size > 0:
                ca_file = p12_ca_file.name
            else:
                # p12_ca_file.seek(0)
                p12_ca_file.write(default_ca.encode())
                p12_ca_file.flush()
                ca_file = p12_ca_file.name
        else:
            raise ValueError(f"{p12_file} is not found.")

    if cert_file and key_file:
        # Loading of client certificate
        context.load_cert_chain(certfile=cert_file, keyfile=key_file, password=p12_pwd)

    if ca_file:
        # Loading of CA certificate.
        context.load_verify_locations(cafile=ca_file)

    # Close temporary files
    if p12_key_file:
        p12_key_file.close()
        os.unlink(p12_key_file.name)
    if p12_cert_file:
        p12_cert_file.close()
        os.unlink(p12_cert_file.name)
    if p12_ca_file:
        p12_ca_file.close()
        os.unlink(p12_ca_file.name)

    return context


class CustomWebsocketTransport(Transport):
    def __init__(
            self,
            url: str,
            p12_file: str,
            p12_pwd: str,
            protocol: Protocol,
            callback: Callable[[Message], Awaitable[None]],
            headers: Optional[Dict[str, str]] = None,
            skip_negotiation: bool = False,
            ping_interval: int = DEFAULT_PING_INTERVAL,
            connection_timeout: int = DEFAULT_CONNECTION_TIMEOUT,
            max_size: Optional[int] = DEFAULT_MAX_SIZE,
    ):
        super().__init__()
        self._url = url
        self._p12_file = p12_file
        self._p12_pwd = p12_pwd
        self._protocol = protocol
        self._callback = callback
        self._headers = headers or {}
        self._skip_negotiation = skip_negotiation
        self._ping_interval = ping_interval
        self._connection_timeout = connection_timeout
        self._max_size = max_size

        self._state = ConnectionState.disconnected
        self._connected = asyncio.Event()
        self._ws: Optional[WebSocketClientProtocol] = None
        self._open_callback: Optional[Callable[[], Awaitable[None]]] = None
        self._close_callback: Optional[Callable[[], Awaitable[None]]] = None

    def on_open(self, callback: Callable[[], Awaitable[None]]) -> None:
        self._open_callback = callback

    def on_close(self, callback: Callable[[], Awaitable[None]]) -> None:
        self._close_callback = callback

    def on_error(self, callback: Callable[[CompletionMessage], Awaitable[None]]) -> None:
        self._error_callback = callback

    async def run(self) -> None:
        while True:
            with suppress(NegotiationTimeout):
                await self._loop()
            await self._set_state(ConnectionState.disconnected)

    async def send(self, message: Message) -> None:
        conn = await self._get_connection()
        await conn.send(self._protocol.encode(message))

    async def _loop(self) -> None:
        await self._set_state(ConnectionState.connecting)

        if not self._skip_negotiation:
            try:
                await self._negotiate()
            except ServerConnectionError as e:
                raise NegotiationTimeout from e

        connection_loop = connect(
            self._url,
            extra_headers=self._headers,
            ping_interval=self._ping_interval,
            open_timeout=self._connection_timeout,
            max_size=self._max_size,
            logger=_logger,
        )

        async for conn in connection_loop:
            try:
                await self._handshake(conn)
                self._ws = conn
                await self._set_state(ConnectionState.connected)
                await asyncio.gather(
                    self._process(conn),
                    self._keepalive(conn),
                )

            except ConnectionClosed as e:
                _logger.warning('Connection closed: %s', e)
                self._ws = None
                await self._set_state(ConnectionState.reconnecting)

    async def _set_state(self, state: ConnectionState) -> None:
        if state == self._state:
            return

        _logger.info('State change: %s -> %s', self._state.name, state.name)

        if state == ConnectionState.connecting:
            if self._state != ConnectionState.disconnected:
                raise RuntimeError('Cannot connect while not disconnected')

            self._connected.clear()

        elif state == ConnectionState.connected:
            if self._state not in (ConnectionState.connecting, ConnectionState.reconnecting):
                raise RuntimeError('Cannot connect while not connecting or reconnecting')

            self._connected.set()

            if self._open_callback:
                await self._open_callback()

        elif state in (ConnectionState.reconnecting, ConnectionState.disconnected):
            self._connected.clear()

            if self._close_callback:
                await self._close_callback()

        else:
            raise NotImplementedError

        self._state = state

    async def _get_connection(self) -> WebSocketClientProtocol:
        await self._connected.wait()
        if not self._ws or self._ws.state != State.OPEN:
            raise RuntimeError('Connection is closed')
        return self._ws

    async def _process(self, conn: WebSocketClientProtocol) -> None:
        while True:
            raw_message = await conn.recv()
            await self._on_raw_message(raw_message)

    async def _keepalive(self, conn: WebSocketClientProtocol) -> None:
        while True:
            await asyncio.sleep(10)
            await conn.send(self._protocol.encode(PingMessage()))

    async def _handshake(self, conn: WebSocketClientProtocol) -> None:
        _logger.info('Sending handshake to server')
        our_handshake = self._protocol.handshake_message()
        await conn.send(self._protocol.encode(our_handshake))

        _logger.info('Awaiting handshake from server')
        raw_message = await conn.recv()
        handshake, messages = self._protocol.decode_handshake(raw_message)
        if handshake.error:
            raise ValueError(f'Handshake error: {handshake.error}')
        for message in messages:
            await self._on_message(message)

    async def _negotiate(self) -> None:
        negotiate_url = get_negotiate_url(self._url)
        _logger.info('Performing negotiation, URL: `%s`', negotiate_url)

        ssl_ctx = create_sslContext(self._p12_file, self._p12_pwd)
        conn = TCPConnector(ssl_context=ssl_ctx)
        session = ClientSession(
            timeout=ClientTimeout(connect=self._connection_timeout),
            connector=conn)

        async with session:
            async with session.post(negotiate_url, headers=self._headers) as response:
                if response.status == HTTPStatus.OK:
                    data = await response.json()
                elif response.status == HTTPStatus.UNAUTHORIZED:
                    raise exceptions.AuthorizationError
                else:
                    raise exceptions.ConnectionError(response.status)

        connection_id = data.get('connectionId')
        url = data.get('url')
        access_token = data.get('accessToken')

        if connection_id:
            _logger.info('Negotiation completed')
            self._url = get_connection_url(self._url, connection_id)
        elif url and access_token:
            _logger.info('Negotiation completed (Azure)')
            self._url = replace_scheme(url, ws=True)
            self._headers['Authorization'] = f'Bearer {access_token}'
        else:
            raise exceptions.ServerError(str(data))

    async def _on_raw_message(self, raw_message: Union[str, bytes]) -> None:
        for message in self._protocol.decode(raw_message):
            await self._on_message(message)

    async def _on_message(self, message: Message) -> None:
        await self._callback(message)
