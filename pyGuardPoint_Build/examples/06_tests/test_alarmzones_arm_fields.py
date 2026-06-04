import logging
from pprint import pprint
from pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized

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

    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)
    try:
        # Get all alarm zones
        alarm_zones = gp.get_alarm_zones()
        for zone in alarm_zones:
            print(zone.name)
            if zone.name == "zone3 ":
                #pprint(zone) #Print all fields within Zone
                print("Zone Name: " + zone.name)
                print("Zone RealTimeStatus: " + str(zone.isRealTimeStatusArm))
                print("Zone WP-Status: " + str(zone.iswpStatusArm))
                print(f"\n\n")

                if gp.disarm_alarm_zone(zone):
                    print("Disarm alarm successful")




    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except Exception as e:
        print(f"Exception: {e}")


