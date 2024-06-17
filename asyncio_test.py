import asyncio
import logging
import sys
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
    logging.basicConfig(level=logging.DEBUG)

    async def test():
        gp = GuardPointAsyncIO(host=GP_HOST,
                        username=GP_USER,
                        pwd=GP_PASS,
                        p12_file=TLS_P12,
                        p12_pwd=TLS_P12_PWD)
        try:
            cardholders = await gp.get_card_holders(offset=0, limit=10)
            for cardholder in cardholders:
                print(f"Firstname: {cardholder.firstName}")

            relays = await gp.get_relays()
            for relay in relays:
                pprint(relay.dict())

                '''try:
                    await gp.activate_relay(relay, period=1)
                except GuardPointError as e:
                    print(f"\n\tRelay Failed to activate: {e}")

                print(f"\n\n")'''
            await gp.close()
        except GuardPointError as e:
            print(f"GuardPointError: {e}")
        except GuardPointUnauthorized as e:
            print(f"GuardPointUnauthorized: {e}")
        except Exception as e:
            print(f"Exception: {e}")

    asyncio.run(test())