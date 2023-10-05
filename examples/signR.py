import asyncio
import sys
from contextlib import suppress
from typing import Any
from typing import Dict
from typing import List

from pysignalr.client import SignalRClient
from pysignalr.messages import CompletionMessage
from pysignalr.transport.websocket import DEFAULT_PING_INTERVAL, DEFAULT_CONNECTION_TIMEOUT, DEFAULT_MAX_SIZE
from CustomWebsocketTransport import CustomWebsocketTransport

# GuardPoint
GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "C:\\Users\\john_\\OneDrive\\Desktop\\MobGuardDefault\\MobileGuardDefault.p12"
TLS_P12_PWD = "test"

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError


async def on_open() -> None:
    print('Connected to the server')


async def on_close() -> None:
    print('Disconnected from the server')


async def on_message(message: List[Dict[str, Any]]) -> None:
    print(f'Received message: {message}')


async def on_error(message: CompletionMessage) -> None:
    print(f'Received error: {message.error}')


def get_client():
    #client = SignalRClient('https://api.tzkt.io/v1/ws')
    #client = SignalRClient('https://sensoraccess.duckdns.org/Hub/EventsHub')
    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)
    headers = {}
    token = gp.get_token()
    auth_str = f"Bearer {token}"
    headers['Authorization'] = auth_str
    client = SignalRClient('http://localhost/Hub/EventsHub', headers=headers)

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
    return client


def attach_signal_client(client:SignalRClient):
    async def run_signal_client() -> None:
        await asyncio.gather(
            client.run(),
            #client.send('IOEventArrived', [{}]),
        )

    asyncio.run(run_signal_client())


# with suppress(KeyboardInterrupt, asyncio.CancelledError):
#    asyncio.run(main())
client = get_client()
client.on_open(on_open)
client.on_close(on_close)
client.on_error(on_error)
client.on("IOEventArrived", on_message)
client.on("GeneralEventArrived", on_message)
client.on("StatusUpdate", on_message)
client.on("TechnicalEventArrived", on_message)
attach_signal_client(client)
