import logging
from typing import List, Dict, Any

from pyGuardPoint import GuardPoint, GuardPointError
from pysignalr.exceptions import AuthorizationError
from pysignalr.messages import CompletionMessage

# GuardPoint Connection Parameters
GP_HOST     = 'https://sensoraccess.duckdns.org'
GP_USER     = 'admin'
GP_PASS     = 'admin'
TLS_P12     = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"
# Hik Connection Parameters
HIK_HOST    = "http://sensoraccess.duckdns.org:85"
HIK_USER    = "admin"
HIK_PWD     = "TempisPro12"

logging.basicConfig(level=logging.DEBUG)

def hik_sync():
    dev_gateway = HikDeviceGateway(host=, username="admin", password="TempisPro12")

    # Talk to the Server, and get a list of all the cameras connected
    dev_list = dev_gateway.list_devices()

    # Go through each device and send to requests!
    for device in dev_list:
        #dev_gateway.delete_person(device, "123466")
        #dev_gateway.delete_card(device, "12345678")
        #dev_gateway.add_person(device, "123466", "test", datetime.now(), (datetime.now() + relativedelta(years=1)))
        #dev_gateway.add_card(device, "123466", "12345678")
        dev_gateway.delete_face(device, employee_num="123466")
        dev_gateway.add_face(device, employee_num="123466", face_img_filepath=None, face_img_base64=b64_image)


async def on_open() -> None:
    print('Connected to the server')


async def on_close() -> None:
    print('Disconnected from the server')


async def on_message(gp, message: List[Dict[str, Any]]) -> None:
    # Looking for a particular message - when a Card is created.
    if not isinstance(message, list):
        return
    if not isinstance(message[0], dict):
        return
    if 'objectName' not in message[0]:
        return
    if 'type' not in message[0]:
        return
    if 'data' not in message[0]:
        return

    if message[0]['objectName'] == 'Card' and message[0]['type'] == 1:
        card_code = message[0]['data']
        print(f"Access Card Created, CardCode: ({card_code})")
        card_holder = gp.get_cardholder_by_card_code(card_code=card_code)
        if card_holder is None:
            print("No Cardholder associated with this Access Card.")
        if card_holder.photo is None:
            print("Cardholder has no Photo.")
        for card in card_holder.cards:
            if card.description == 'BIOMETRIC':
                print("Found BIOMETRIC card.")
                print("Attempting to sync Photo with Hik Devices .....")
                #print(f"PHOTO:\n {card_holder.photo}\n")



async def on_error(message: CompletionMessage) -> None:
    print(f'Received error: {message.error}')


if __name__ == "__main__":
    try:
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
        signal_client.on("AuditEventArrived", lambda msg: on_message(gp, msg))

        gp.start_listening(signal_client)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except AuthorizationError as e:
        print(f"SignalR AuthorizationError")
    except Exception as e:
        print(f"Exception: {str(e)}")
