import logging, sys
from pprint import pprint

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
        #print("Cardholder:")
        #cardholder.pretty_print()

        cardholders = gp.get_card_holders(search_terms="Ada Lovelace",
                                          sort_algorithm=SortAlgorithm.FUZZY_MATCH,
                                          select_include_list=['uid', 'firstName', 'lastName', 'photo',
                                                               'cardholderPersonalDetail', 'cardholderType',
                                                               'cardholderCustomizedField'],
                                          select_ignore_list=['cardholderCustomizedField', 'ownerSiteUID',
                                                              'photo'])
        print("Cardholder:")
        #cardholders[0].pretty_print()
        pprint(cardholders[0].dict())

        photo = gp.get_card_holder_photo(uid=cardholders[0].uid)
        print(f"Photo:{photo}")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
