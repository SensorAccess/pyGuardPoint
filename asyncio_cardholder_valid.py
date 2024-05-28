import asyncio
import logging
import sys
from importlib.metadata import version
from pprint import pprint

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPointAsyncIO, GuardPoint, GuardPointError, GuardPointUnauthorized
#from pyGuardPoint import GuardPoint, GuardPointAsyncIO, GuardPointError, GuardPointUnauthorized



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
    if py_gp_version_int < 138:
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
        try:
            cardholders = await gp.get_card_holders(search_terms="john owen", threshold=100, limit=1)
            for cardholder in cardholders:
                print(f"firstName: {cardholder.firstName}")
                print(f"lastName: {cardholder.lastName}")
                print(f"email: {cardholder.cardholderPersonalDetail.email}")
                print(f"securityGroup: {cardholder.securityGroup.name}")
                print(f"accessGroupUIDs: {cardholder.accessGroupUIDs}")
                print(f"status: {cardholder.status}")

                if cardholder.isFromDateActive:
                    print(f"fromDateValid: {cardholder.fromDateValid}")
                if cardholder.isToDateActive:
                    print(f"toDateValid: {cardholder.toDateValid}")


            await gp.close()
        except GuardPointError as e:
            print(f"GuardPointError: {e}")
        except GuardPointUnauthorized as e:
            print(f"GuardPointUnauthorized: {e}")
        except Exception as e:
            print(f"Exception: {e}")

    asyncio.run(main())