import logging, sys
import pkg_resources
from strgen import StringGenerator # pip install StringGenerator

from pyGuardPoint_Build.pyGuardPoint.guardpoint_dataclasses import ScheduledMag

# Use PyPi Module
#from pyGuardPoint import GuardPoint, GuardPointError

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        # Get a cardholder
        cardholder = gp.get_card_holder(card_code='1B1A1B1C')

        sm = ScheduledMag(cardholdsdfsfserUID=cardholder.uid)
        gp.add_scheduled_mag(sm)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")