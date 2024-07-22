import logging
from importlib.metadata import version
from pyGuardPoint import GuardPoint, GuardPointError

# GuardPoint
GP_HOST = 'https://sensoraccess.duckdns.org'
# GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
#TLS_P12 = "C:\\Users\\john_\\OneDrive\\Desktop\\MobGuardDefault\\MobileGuardDefault.p12"
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

py_gp_version = version("pyGuardPoint")

# _logger = logging.getLogger('pysignalr.transport')
# _logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    try:
        # Provide Credentials for encrypted session with GuardPoint ACS Server
        gp = GuardPoint(host=GP_HOST,
                        username=GP_USER,
                        pwd=GP_PASS,
                        p12_file=TLS_P12,
                        p12_pwd=TLS_P12_PWD)

        # Robot would have his own Access Card
        card_code = "AABB1122"

        # Fire Event on known Reader/Controller
        controller_uid = "3b019330-32f1-48d9-8d0e-c61303263eb5"
        reader_num = 1
        if gp.simulate_access_event(controller_uid=controller_uid,
                                    reader_num=reader_num,
                                    card_code=card_code):
            print("Event Fired Successfully")

        # Extra useful commands ....

        # Find out the available Readers
        '''readers = gp.get_readers()
        for reader in readers:
            print(reader.number)
            print(reader.controllerUID)
            controller = gp.get_controller(reader.controllerUID)
            print("Connected = " + str(controller.isConnected))'''

        # View last 5 Access Events
        '''access_events = gp.get_access_events(limit=5)
        for access_event in access_events:
            print(access_event)'''

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {str(e)}")
