import asyncio
import logging
import sys
from importlib.metadata import version
from pprint import pprint

#from pyGuardPoint import GuardPoint, GuardPointAsyncIO, GuardPointError, GuardPointUnauthorized

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')

from pyGuardPoint_Build.pyGuardPoint import GuardPointAsyncIO, GuardPointError, GuardPointUnauthorized

# GuardPoint
GP_HOST = 'https://sensoraccess.duckdns.org'
# GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
#TLS_P12 = "C:\\Users\\john_\\OneDrive\\Desktop\\MobGuardDefault\\MobileGuardDefault.p12"
TLS_P12_PWD = "test"

if __name__ == "__main__":
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 140:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    logging.basicConfig(level=logging.DEBUG)

    async def main():
        gp = GuardPointAsyncIO(host=GP_HOST,
                               username=GP_USER,
                               pwd=GP_PASS,
                               p12_file=TLS_P12,
                               p12_pwd=TLS_P12_PWD)

        print(f"\n********* Get Access Events **********")
        access_events = await gp.get_access_events(limit=3, offset=0)

        for access_event in access_events:
            print(f"\nAccessEvent:")
            print(f"\tType: {access_event.type}")
            print(f"\tjournalUpdateDateTime: {access_event.journalUpdateDateTime}")
            print(f"\tdateTime: {access_event.dateTime}")
            print(f"\taccessDeniedCode: {access_event.accessDeniedCode}")
            print(f"\tisPastEvent: {access_event.isPastEvent}")

        print(f"\n\n********* Get Alarm Events **********")
        alarm_events = await gp.get_alarm_events(limit=3, offset=0)

        for alarm_event in alarm_events:
            print(f"\nAlarmEvent:")
            print(f"\tType: {alarm_event.type}")
            print(f"\tjournalUpdateDateTime: {alarm_event.journalUpdateDateTime}")
            print(f"\tdateTime: {alarm_event.dateTime}")

        await gp.close()

    try:
        asyncio.run(main())
    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except Exception as e:
        print(f"Exception: {e}")
