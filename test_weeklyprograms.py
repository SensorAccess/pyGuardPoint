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
# GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    #py_gp_version = version("pyGuardPoint")
    #print("pyGuardPoint Version:" + py_gp_version)
    #py_gp_version_int = int(py_gp_version.replace('.', ''))
    #if py_gp_version_int < 179:
    #    print("Please Update pyGuardPoint")
    #    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
     #   exit()

    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)
    try:
        # Get all alarm zones
        weekly_programs = gp.get_weekly_programs()
        for wp in weekly_programs:
            print("Zone Name: " + wp.name)
            print("Zone uid: " + wp.uid)
            print("Zone Description: " + str(wp.description))
            print(f"\n\n")

        wp = gp.get_weekly_program('11111111-1111-1111-1111-111111111111')
        pprint(wp)


    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except Exception as e:
        print(f"Exception: {e}")


