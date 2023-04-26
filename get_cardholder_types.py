import logging
import sys

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

import pkg_resources

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        cardholder_types = gp.get_cardholder_types()
        for cardholder_type in cardholder_types:
            print(cardholder_type.dict())

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
