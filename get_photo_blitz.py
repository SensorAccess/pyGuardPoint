import asyncio
import datetime, sys
import logging
from pprint import pprint

from pyGuardPoint import GuardPoint, CardholderPersonalDetail, GuardPointError, GuardPointAsyncIO, \
    GuardPointUnauthorized

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"


async def test():
    gp = GuardPointAsyncIO(host=GP_HOST,
                           username=GP_USER,
                           pwd=GP_PASS,
                           p12_file=TLS_P12,
                           p12_pwd=TLS_P12_PWD,
                           site_uid='11111111-1111-1111-1111-111111111111')
    try:
        async def get_photo():
            print(".", end="")
            photo = await gp.get_card_holder_photo("1b65694a-0490-4641-92ab-d8c656065a0c")


        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(get_photo()) for i in range(100)]

        results = await asyncio.gather(*tasks)
        print(f"{len(results)}\n\n")

        await gp.close()



    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except Exception as e:
        print(f"Exception: {e}")


asyncio.run(test())