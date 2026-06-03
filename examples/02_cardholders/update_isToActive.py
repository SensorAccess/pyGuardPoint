import logging, sys
import pkg_resources


# Use PyPi Module
#from pyGuardPoint import GuardPoint, GuardPointError

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="https://sensoraccess.duckdns.org", pwd="admin",
                    p12_file="C:\\Users\\john_\\OneDrive\\Desktop\\MobileGuardDefault.p12",
                    p12_pwd="test")

    try:
        cardholders = gp.get_card_holders(lastName="Nighthawk")

        cardholder = cardholders[0]
        print(f"\tisToDateActive: {cardholder.isToDateActive}")
        cardholder.isToDateActive = False
        cardholder.toDateValid = None

        gp.update_card_holder(cardholder)
        cardholder = gp.get_card_holder(uid=cardholder.uid)
        print(f"\tisToDateActive: {cardholder.isToDateActive}")



    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")