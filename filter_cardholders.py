import logging, sys
from pprint import pprint
import pkg_resources

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:

        cardholders = gp.get_card_holders(cardholderTypeUID="22222222-2222-2222-2222-222222222222",
                                          sort_algorithm=SortAlgorithm.FUZZY_MATCH,
                                          lastName="Owen", limit=20)
        if len(cardholders) > 0:
            print("Cardholder:")
            # cardholders[0].pretty_print()
            pprint(cardholders[0].dict())

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
