import logging
import pkg_resources
from pyGuardPoint import GuardPoint, GuardPointError

# GuardPoint
GP_HOST = 'https://sensoraccess.duckdns.org'
# GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "C:\\Users\\john_\\OneDrive\\Desktop\\MobGuardDefault\\MobileGuardDefault.p12"
#TLS_P12 = None
TLS_P12_PWD = "test"

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

# _logger = logging.getLogger('pysignalr.transport')
# _logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    try:
        gp = GuardPoint(host=GP_HOST,
                        username=GP_USER,
                        pwd=GP_PASS,
                        p12_file=TLS_P12,
                        p12_pwd=TLS_P12_PWD)

        # Fire Event on known Reader/Controller
        controller_uid = "a403264f-d546-4424-92a4-125108c7fd48"
        #controller_uid = "7b0bb0fc-86c4-412a-ac17-ad2381f46b07"
        reader_num = 1
        card_code = "AABB1122"

        if gp.simulate_access_event(controller_uid=controller_uid, reader_num=reader_num, card_code=card_code):
            print("Event Fired Successfully")

        # Cycle through all Readers + fire event
        readers = gp.get_readers()
        for reader in readers:
            print(reader.controllerUID)
            '''if gp.simulate_access_event(
                    controller_uid=reader.controllerUID,
                    reader_num=reader.number,
                    card_code=card_code):
                print("Event Fired Successfully")'''

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {str(e)}")
