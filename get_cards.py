import logging, sys
from pprint import pprint
#import pkg_resources

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm

#py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

if __name__ == "__main__":
    #print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)

    try:
        cards = gp.get_cards(cardCode="1A1B1C8C")
        print("Cards:")
        for card in cards:
            pprint(card.dict())
            if card.cardholderUID is not None:
                print(card.cardholderUID)
            else:
                print("No cardholderUID")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
