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
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 178:
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
        '''alarm_zones = gp.get_alarm_zones()
        for zone in alarm_zones:
            #pprint(zone) #Print all fields within Zone
            print("Zone Name: " + zone.name)
            print("Zone RealTimeStatus: " + str(zone.isRealTimeStatusArm))
            print("Zone WP-Status: " + str(zone.iswpStatusArm))
            print(f"\n\n")'''

        # Get a single alarm zone by UID
        zone = gp.get_alarm_zone('210841de-e0da-4ccc-a2e6-f2519738249c')
        pprint(zone)

        # Disarm Alarm Zone
        if zone.isRealTimeStatusArm:
            if gp.disarm_alarm_zone(zone):
                print(f"{zone.name} is disarmed")
        else:
            if gp.arm_alarm_zone(zone):
                print(f"{zone.name} is armed")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except Exception as e:
        print(f"Exception: {e}")


