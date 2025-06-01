import logging, sys
from pprint import pprint

#import pkg_resources

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm, GuardPointAuthType

#py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

GP_HOST = 'https://sensoraccess.duckdns.org:82'
GP_USER = 'admin'
GP_PASS = 'TempisPro12'
GP_API_KEY = '2b2967b0-33b5-47d8-b24c-3239b325f812'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

if __name__ == "__main__":
    #print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(
        host=GP_HOST,
        username=GP_USER,
        pwd=GP_PASS,
        key=GP_API_KEY,
        p12_file=TLS_P12,
        p12_pwd=TLS_P12_PWD,
        auth=GuardPointAuthType.BEARER_TOKEN,
        # auth=GuardPointAuthType.BASIC
    )

    try:
        readers = gp.get_readers()
        print("Readers:")
        for reader in readers:
            pprint(reader)
            if reader.name == "INNER DOOR IN":
                signin_event_fired = gp.simulate_access_event(controller_uid=reader.controllerUID,
                                                              reader_num=reader.number,
                                                              card_code="8534BE8F")
                print("Access Event Returned: " + str(signin_event_fired))

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
