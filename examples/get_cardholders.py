import logging

from importlib.metadata import version
from pyGuardPoint import GuardPoint, GuardPointError, Cardholder, CardholderPersonalDetail, Card, \
    CardholderCustomizedField, SortAlgorithm

# GuardPoint
GP_HOST = 'https://sensoraccess.duckdns.org'
# GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
#TLS_P12 = None
TLS_P12_PWD = "test"

py_gp_version = version("pyGuardPoint")
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 138:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)
    try:
        # gp.get_card_holder(uid='7922a114-2f56-472c-9aeb-53903dba69cb')
        # cardholder = gp.get_card_holder(card_code='1B1A1B1C')
        # print("Cardholder:")
        # cardholder.pretty_print()
        cardholders = gp.get_card_holders(search_terms="Phil Sensor",
                                          cardholder_type_name='Visitor',
                                          filter_expired=False,
                                          select_ignore_list=['cardholderCustomizedField',
                                                              'cardholderPersonalDetail',
                                                              'securityGroup',
                                                              'photo'],
                                          select_include_list=['uid', 'lastName', 'firstName', 'lastPassDate',
                                                               'insideArea', 'fromDateTime', 'cards'],
                                          sort_algorithm=SortAlgorithm.FUZZY_MATCH,
                                          threshold=90
                                          )
        for cardholder in cardholders:
            print("Cardholder:")
            print(f"\t{cardholder.lastName}")
            cardholder.pretty_print()

        # Example Using Fuzzy Matching & select_lists
        '''
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
        '''

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
