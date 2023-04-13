import logging, sys
import pkg_resources
from pyGuardPoint import GuardPoint, GuardPointError, Cardholder, CardholderPersonalDetail, Card, \
    CardholderCustomizedField, SortAlgorithm

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 74:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

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



    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")