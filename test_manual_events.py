import logging
from pprint import pprint
from importlib.metadata import version

# Force to use pyGuardPoint from pyGuardPoint_Build directory
#sys.path.insert(1, 'pyGuardPoint_Build')
#from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm

# Use release version of PyGuardPoint from PiPy
from pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm, GuardPointAuthType

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 196:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)

    try:
        gp.connection.authType = GuardPointAuthType.BASIC
        gp.connection.key = "open"
        manual_events = gp.get_manual_events()
        if len(manual_events) < 1:
            print("No Manual Events Found")
        else:
            # Print the Manual Events
            for event in manual_events:
                pprint(event)
                print("\n")

            api_key = 'open'
            if gp.activate_manual_event_by_api_key(api_key):
                print(f"Manual Event({api_key}) Activated")

            # Loop over the Manual Events
            '''for event in manual_events:
                # When we get a event name which matches
                if event.name == "TheNameOfTheManualEvent":
                    print(f"Activating .. {event.name} ....")
                    if gp.activate_manual_event(event):
                        print("Event Activated\n")
                    else:
                        print("Event Failed To Activate\n")'''

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
