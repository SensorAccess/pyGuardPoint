import logging
import sys
from pprint import pprint
from importlib.metadata import version

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized, EventOrder

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
    if py_gp_version_int < 177:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD,
                    site_uid='11111111-1111-1111-1111-111111111111')
    try:
        print("Num Access Events: " + str(gp.get_access_events_count()))
        access_events = gp.get_access_events(limit=1, orderby=EventOrder.LOG_ID_ASC)
        for access_event in access_events:
            pprint(access_event)
            print(f"\n\n")

        print("Num Alarm Events: " + str(gp.get_alarm_events_count()))
        alarm_events = gp.get_alarm_events(limit=1)
        for alarm_event in alarm_events:
            pprint(alarm_event)
            print(f"\n\n")

        print("Num Audit Events: " + str(gp.get_audit_events_count()))
        audit_events = gp.get_audit_events(limit=1)
        for audit_event in audit_events:
            pprint(audit_event)
            print(f"\n\n")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except Exception as e:
        print(f"Exception: {e}")


