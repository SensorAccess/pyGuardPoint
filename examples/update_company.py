import logging, sys
import pkg_resources
from pyGuardPoint import GuardPoint, GuardPointError, Cardholder

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 73:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        cardholder = gp.get_card_holder(card_code='1B1A1B1C')
        print(f"\tcompany: {cardholder.cardholderPersonalDetail.company}")

        cardholder.cardholderPersonalDetail.company = "New Company"

        if gp.update_card_holder(cardholder):
            updated_cardholder = gp.get_card_holder(uid=cardholder.uid)
            print(f"\tcompany: {cardholder.cardholderPersonalDetail.company}")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")