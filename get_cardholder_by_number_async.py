import asyncio
import logging, sys
from importlib.metadata import version
from pprint import pprint

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized, SortAlgorithm, \
    GuardPointAsyncIO

from pyGuardPoint import GuardPointAsyncIO, GuardPointError, SortAlgorithm

GP_HOST = 'https://sensoraccess.duckdns.org'
#GP_HOST = 'http://192.168.1.111:10695'
GP_USER = 'admin'
GP_PASS = 'admin'
#GP_USER = 'remko'
#GP_PASS = 'remko'
#GP_USER = 'robert'
#GP_PASS = 'password'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"
#SITE_UID = "f342eade-eb43-4359-918d-d067d609fc38" # Sensor Office
#SITE_UID = "90be9b9d-c87f-44b0-9ff9-e0f8725abbad" # Force site filter
#SITE_UID = None

if __name__ == "__main__":
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 197:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    logging.basicConfig(level=logging.DEBUG)


    async def main():
        gp = GuardPointAsyncIO(host=GP_HOST,
                               username=GP_USER,
                               pwd=GP_PASS,
                               p12_file=TLS_P12,
                               p12_pwd=TLS_P12_PWD
                               )

        try:
            areas = await gp.get_areas()
            manev = await gp.get_manual_events()
            areas = await gp.get_areas()
            cardholders = await gp.get_card_holders(count=True, areas=areas,
                                                    cardholder_type_name="Visitor",
                                                    search_terms="john owen john_owen",
                                                    sort_algorithm=SortAlgorithm.FUZZY_MATCH)

            print(cardholders)

            #for cardholder in cardholders:
            #    print(f"\tFirst Name: {cardholder.firstName}")
            #    print(f"\tLast Name: {cardholder.lastName}")
            #    print(f"\tEmail: {cardholder.cardholderPersonalDetail.email}")
            #print(f"\townerSiteUID: {cardholder.ownerSiteUID}")
            #    print(f"\tCardholderUID: {cardholder.uid}")
            #    print(f"\tPin Code: {cardholder.pinCode}")
            #print(f"\tStatus: {cardholder.status}")

            await gp.close()

        except GuardPointError as e:
            print(f"GuardPointError: {e}")
        except Exception as e:
            print(f"Exception: {e}")


    asyncio.run(main())
