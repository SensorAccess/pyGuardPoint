import asyncio
from contextlib import suppress
from typing import Any
from typing import Dict
from typing import List

from pysignalr.client import SignalRClient
from pysignalr.messages import CompletionMessage
from pysignalr.transport.websocket import DEFAULT_PING_INTERVAL, DEFAULT_CONNECTION_TIMEOUT, DEFAULT_MAX_SIZE
from CustomWebsocketTransport import CustomWebsocketTransport




async def on_open() -> None:
    print('Connected to the server')


async def on_close() -> None:
    print('Disconnected from the server')


async def on_message(message: List[Dict[str, Any]]) -> None:
    print(f'Received message: {message}')


async def on_error(message: CompletionMessage) -> None:
    print(f'Received error: {message.error}')

TLS_P12 = "C:\\Users\\john_\\OneDrive\\Desktop\\MobileGuardDefault.p12"
TLS_P12_PWD = "test"
async def main() -> None:
    #client = SignalRClient('https://api.tzkt.io/v1/ws')
    client = SignalRClient('https://sensoraccess.duckdns.org/Hub/EventsHub')
    client._transport = CustomWebsocketTransport(
        url=client._url,
        p12_file=TLS_P12,
        p12_pwd=TLS_P12_PWD,
        protocol=client._protocol,
        callback=client._on_message,
        headers=client._headers,
        ping_interval=DEFAULT_PING_INTERVAL,
        connection_timeout=DEFAULT_CONNECTION_TIMEOUT,
        max_size=DEFAULT_MAX_SIZE,
    )

    client.on_open(on_open)
    client.on_close(on_close)
    client.on_error(on_error)
    client.on('operations', on_message)

    await asyncio.gather(
        client.run(),
        client.send('SubscribeToOperations', [{}]),
    )


with suppress(KeyboardInterrupt, asyncio.CancelledError):
    asyncio.run(main())