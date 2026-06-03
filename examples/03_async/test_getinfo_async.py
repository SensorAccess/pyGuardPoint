import asyncio
import logging
import sys
from pprint import pprint

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized, GuardPointAsyncIO

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

    async def test():
        gp = GuardPointAsyncIO(host=GP_HOST,
                               username=GP_USER,
                               pwd=GP_PASS,
                               p12_file=TLS_P12,
                               p12_pwd=TLS_P12_PWD,
                               site_uid='11111111-1111-1111-1111-111111111111')

        try:
            #await gp.close()
            await gp.reopen()
            pprint("SIG-R Enabled = " + str(await gp.is_sigr_enabled()))
            print(f"\n\n")
            await gp.close()


        except GuardPointError as e:
            print(f"GuardPointError: {e}")
        except GuardPointUnauthorized as e:
            print(f"GuardPointUnauthorized: {e}")
        except Exception as e:
            print(f"Exception: {e}")

    asyncio.run(test())

