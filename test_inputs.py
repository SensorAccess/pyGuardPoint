import logging
import sys
from pprint import pprint
from importlib.metadata import version

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized
#from pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized

# GuardPoint
GP_HOST = 'https://sensoraccess.duckdns.org'
GP_HOST = 'http://192.168.1.103:10695'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 194:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)
    try:
        # Get all alarm zones
        inputs = gp.get_inputs()
        for input in inputs:
            #pprint(input)
            print("name: " + str(input.name))
            print("isUnderAlarm: " + str(input.isUnderAlarm))
            print(f"")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except Exception as e:
        print(f"Exception: {e}")


