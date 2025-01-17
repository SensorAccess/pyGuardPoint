import logging
from importlib.metadata import version
from pyGuardPoint import GuardPoint, GuardPointError, EventOrder

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"
SITE_UID = None # All Sties
#SITE_UID = "f342eade-eb43-4359-918d-d067d609fc38" # Sensor Office

if __name__ == "__main__":
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 173:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD,
                    site_uid=SITE_UID)

    try:
        access_events = gp.get_access_events(orderby=EventOrder.DATETIME_ASC)
        for access_event in access_events:
            print("Access Event:")
            print(f"\tlogID: {access_event.logID}")
            print(f"\tdateTime: {access_event.dateTime}")
            print(f"\tcardCode: {access_event.cardCode}")

        access_event_count = gp.get_access_events_count()
        print(f"Total Events Count: {access_event_count}")

        '''card_code = "00001234"
        # Cycle through all Readers + fire event
        readers = gp.get_readers()
        for reader in readers:
            controller = gp.get_controller(reader.controllerUID)
            print(controller.isActivated)
            print(controller.isConnected)
            if gp.simulate_access_event(
                    controller_uid=reader.controllerUID,
                    reader_num=reader.number,
                    card_code=card_code):
                print("Event Fired Successfully")'''


    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")






