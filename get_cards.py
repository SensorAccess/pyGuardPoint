import logging, sys
from pprint import pprint
#import pkg_resources

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm

#py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    #print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        cards = gp.get_cards(cardCode="1A1B1C8C")
        print("Cards:")
        for card in cards:
            pprint(card.dict())

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
