import logging, sys
import random

import pkg_resources
from pyGuardPoint import GuardPoint, GuardPointError, Cardholder

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 48:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        areas = gp.get_areas()
        cardholders = gp.get_card_holders(search_terms="john")

        print(f"Cardholder: {cardholders[0].lastName} Area: {cardholders[0].insideAreaUID}")
        new_area = random.choice(areas)
        gp.update_card_holder_area(cardholders[0].uid, new_area)
        cardholder = gp.get_card_holder(cardholders[0].uid)
        print(f"Cardholder: {cardholder.lastName} Area: {cardholder.insideAreaUID}")


    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")