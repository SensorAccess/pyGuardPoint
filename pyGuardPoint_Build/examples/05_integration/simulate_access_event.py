"""
Find an activated, connected controller with a reader attached on the test
GuardPoint server, then simulate a single access event on it.
"""
import logging
from pathlib import Path

from pyGuardPoint import GuardPoint, GuardPointError

from pyGuardPoint_Build.pyGuardPoint import Cardholder

GP_HOST = 'https://sensoraccess2.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
TLS_P12 = Path(__file__).resolve().parents[2] / 'tests' / 'MobileGuardDefault.p12'
TLS_P12_PWD = 'test'

CARD_CODE = '11223345'

logging.basicConfig(level=logging.INFO)


def find_controller_with_reader(gp):
    controllers = gp.get_controllers()
    readers = gp.get_readers()

    for controller in controllers:
        if not (controller.isActivated and controller.isConnected):
            continue
        for reader in readers:
            if reader.controllerUID == controller.uid:
                return controller, reader

    return None, None


if __name__ == "__main__":
    gp = GuardPoint(
        host=GP_HOST,
        username=GP_USER,
        pwd=GP_PASS,
        p12_file=str(TLS_P12),
        p12_pwd=TLS_P12_PWD,
    )

    try:
        controller, reader = find_controller_with_reader(gp)

        if controller is None:
            print("No activated, connected controller with a reader attached was found.")
        else:
            print(f"Using Controller: {controller.name} ({controller.uid}) "
                  f"Reader: {reader.name} (num={reader.number})")

            if gp.simulate_access_event(controller_uid=controller.uid,
                                        reader_num=reader.number,
                                        card_code=CARD_CODE):
                print(f"Event fired successfully. Card Code: {CARD_CODE}")
            else:
                print("Event simulation reported failure.")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
