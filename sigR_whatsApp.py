import logging
from typing import List, Dict, Any
from heyoo import WhatsApp

from pyGuardPoint import GuardPoint, GuardPointError
from pysignalr.exceptions import AuthorizationError
from pysignalr.messages import CompletionMessage
from datetime import datetime

# WhatsApp Connection Parameters
phone_numer = '+447723523322'

# GuardPoint Connection Parameters
GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

logging.basicConfig(level=logging.DEBUG)


def send_whatsapp(message: str):
    messenger = WhatsApp(
        'EAAGDWOXfXIoBO5LaPm0qPWNIj3ojyCFDZC4QFIUZCxX795WzW67YMblfCKGUi3dO0WQ2f4TxOGwBd1rpV6UbFZBdLYwF2PVcCDa3R3BzQLp1qQGlaq5yIRvEkfPIbTZABYHku2siFZBJY20nd3A30KNkxBCSuuPDBYX1AWYUlzmWNWaGHaMB8oLYoPw11QChH13X3JOPFpZCkTDfEBawZDZD',
        phone_number_id='347702945091658')
    # For sending a Text messages
    messenger.send_message(str(message), phone_numer)
    # For sending an Image
    '''messenger.send_image(
        image="https://i.imgur.com/YSJayCb.jpeg",
        recipient_id="91989155xxxx",
    )'''


async def on_open() -> None:
    print('Connected to the server')


async def on_close() -> None:
    print('Disconnected from the server')


async def on_access_event(message: List[Dict[str, Any]]) -> None:
    print(f'Access Event arrived: {message}')


async def on_error(message: CompletionMessage) -> None:
    print(f'Received error: {message.error}')


if __name__ == "__main__":
    try:
        send_whatsapp("test message")
        gp = GuardPoint(host=GP_HOST,
                        username=GP_USER,
                        pwd=GP_PASS,
                        p12_file=TLS_P12,
                        p12_pwd=TLS_P12_PWD)

        signal_client = gp.get_signal_client()

        # Set up your signal_client callbacks
        signal_client.on_open(on_open)
        signal_client.on_close(on_close)
        signal_client.on_error(on_error)
        signal_client.on('AccessEventArrived', on_access_event)

        gp.start_listening(signal_client)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except AuthorizationError as e:
        print(f"SignalR AuthorizationError")
    except Exception as e:
        print(f"Exception: {str(e)}")
