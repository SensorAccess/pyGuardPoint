import asyncio
import logging
import sys
from pprint import pprint

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

    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD,
                    site_uid='11111111-1111-1111-1111-111111111111')
    try:
        access_events = gp.get_access_events(limit=1, orderby=EventOrder.LOG_ID_ASC)
        for access_event in access_events:
            pprint(access_event)
            print(f"\n\n")

        alarm_events = gp.get_alarm_events(limit=1)
        for alarm_event in alarm_events:
            pprint(alarm_event)
            print(f"\n\n")

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


