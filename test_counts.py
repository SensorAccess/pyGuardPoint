import logging
import sys

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

import pkg_resources

from pyGuardPoint_Build.pyGuardPoint import SortAlgorithm

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        areas = gp.get_areas()
        for area in areas:
            cardholder_count = gp.get_card_holders(count=True, areas=area)
            print(f"Cardholders in {area.name} = {str(cardholder_count)}")


    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

    try:
        card_count = gp.get_cards(count=True)
        print("Card Count: " + str(card_count))

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")