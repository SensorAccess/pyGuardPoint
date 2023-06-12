import logging, sys
import pkg_resources
from pyGuardPoint import GuardPoint, GuardPointError, Cardholder, CardholderPersonalDetail, Card, \
    CardholderCustomizedField, SortAlgorithm

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="admin")

    try:
        personalDetails = CardholderPersonalDetail(email="john.owen@countermac.com")
        cardholders = gp.get_card_holders(cardholderPersonalDetail=personalDetails,
                                          select_ignore_list=['cardholderCustomizedField', 'ownerSiteUID',
                                                              'photo']
                                          )

        for cardholder in cardholders:
            print("Cardholder:")
            print(f"\t{cardholder.lastName}")
            print(f"\t{cardholder.cardholderPersonalDetail.email}")
            print(cardholder.dict(non_empty_only=True))
            #cardholder.pretty_print()



    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")