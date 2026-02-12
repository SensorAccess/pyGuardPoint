import logging, sys
from pprint import pprint

# Force to use pyGuardPoint from pyGuardPoint_Build directory
#sys.path.insert(1, 'pyGuardPoint_Build')
#from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm

# Use release version of PyGuardPoint from PiPy
from pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
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
        manual_events = gp.get_manual_events()
        if len(manual_events) < 1:
            print("No Manual Events Found")
        else:
            # Print the Manual Events
            for event in manual_events:
                pprint(event)
                print("\n")

            # Try and Activate all of the Manual Events
            print("Activating all Manual Events.....\n")
            for event in manual_events:
                print(f"Activating .. {event.name} ....")
                if gp.activate_manual_event(event):
                    print("Event Activated\n")
                else:
                    print("Event Failed To Activate\n")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
