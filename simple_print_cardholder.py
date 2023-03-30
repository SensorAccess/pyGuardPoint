import logging, sys
import pkg_resources
# Use PyPi Module
#from pyGuardPoint import GuardPoint, GuardPointError

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        #cardholder = gp.get_card_holder(card_code='1B1A1B1C')
        #cardholder = gp.get_card_holder(uid='0eb37f82-829a-425c-9a37-48f45a350600')
        cardholders = gp.get_card_holders(search_terms="Ada Lovelace",
                                          sort_algorithm=SortAlgorithm.FUZZY_MATCH,
                                          property_ignore_list=['firstName', 'ownerSiteUID', 'photo'])
        print("Cardholder:")
        cardholders[0].pretty_print()

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
