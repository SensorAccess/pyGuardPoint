import logging, sys
import pkg_resources
from pyGuardPoint import GuardPoint, GuardPointError, Cardholder, CardholderPersonalDetail, Card, \
    CardholderCustomizedField, SortAlgorithm

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 61:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        #cardholder = gp.get_card_holder(card_code='1B1A1B1C')
        #print("Cardholder:")
        #cardholder.pretty_print()

        cardholders = gp.get_card_holders(search_terms="Ada Lovelace",
                                          sort_algorithm=SortAlgorithm.FUZZY_MATCH,
                                          threshold=100,
                                          select_include_list=['uid', 'firstName', 'lastName', 'photo',
                                                               'cardholderPersonalDetail', 'cardholderType',
                                                               'cardholderCustomizedField'],
                                          select_ignore_list=['cardholderCustomizedField','ownerSiteUID',
                                                              'photo'])
        for cardholder in cardholders:
            print("Cardholder:")
            cardholder.pretty_print()
            photo = gp.get_card_holder_photo(uid=cardholder.uid)
            print(f"Photo:{photo}")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")