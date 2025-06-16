import datetime, sys
import logging
from pyGuardPoint import GuardPoint, CardholderPersonalDetail, GuardPointError

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm, GuardPointAuthType, Area

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD,
                    site_uid="11111111-1111-1111-1111-111111111111")

    try:
        personalDetails = CardholderPersonalDetail(email="john.owen@countermac.com")
        numOfCardholders = gp.get_cardholder_count()
        print(f"Total Cardholders: {numOfCardholders}")

        print(f"\nGet first 10 Cardholders:")
        cardholders = gp.get_card_holders(offset=0, limit=10)
        for cardholder in cardholders:
            print("Cardholder:")
            print(f"\tFirstName: {cardholder.firstName}")
            print(f"\tLastName: {cardholder.lastName}")
            print(f"\tEmail: {cardholder.cardholderPersonalDetail.email}")

        searchTerm = "Test"
        print(f"\nSearch for a Cardholders with the term '{searchTerm}'")
        cardholders = gp.get_card_holders(search_terms=searchTerm, limit=100)
        print(f"Search found {len(cardholders)} cardholders")


        areas = gp.get_areas()
        for area in areas:
            if area.name == "Offsite":
                cardholders = gp.get_card_holders(search_terms="piotr",
                                          limit=100,
                                          areas=area,
                                          earliest_last_pass=datetime.datetime.now()
                                                             - datetime.timedelta(days=365),
                                          select_include_list=['uid', 'lastName', 'firstName',
                                                               'lastPassDate',
                                                               'insideArea'],
                                          )
        print(f"Last Pass search found {len(cardholders)} cardholders")
        for cardholder in cardholders:
            print("Cardholder:")
            print(f"\tFirstName: {cardholder.firstName}")
            print(f"\tLastName: {cardholder.lastName}")
            print(f"\tArea: {cardholder.insideArea.name}")
            print(f"\tLastPassDate: {cardholder.lastPassDate}")
            #print(f"\tLastSigninDate: {cardholder.cardholderCustomizedField.cF_DateTimeField_5}")

        # Further functionality and documentation can be found at:
        # https://pyguardpoint.readthedocs.io/en/latest/
        # https://pypi.org/project/pyGuardPoint/

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
