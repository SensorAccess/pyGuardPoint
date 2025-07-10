import asyncio
import datetime, sys
import logging
from pprint import pprint

from pyGuardPoint import GuardPoint, CardholderPersonalDetail, GuardPointError, GuardPointAsyncIO, \
    GuardPointUnauthorized

#GP_HOST = 'https://sensoraccess.duckdns.org'
GP_HOST = 'http://192.168.1.103:10695'
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
        uid=""

        cardholders = await gp.get_card_holders(search_terms="john")
        for cardholder in cardholders:
            if cardholder.photo:
                uid = cardholder.uid
                break

        if len(uid) == 0:
            print("No Cardholders with Photos Found!!")
            await gp.close()
            return

        async def get_photo():
            print(".", end="")
            try:
                photo = await gp.get_card_holder_photo(uid)
            except Exception as e:
                print(e)

        # Run all at once very fast
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(get_photo()) for i in range(200)]

        results = await asyncio.gather(*tasks)



        tasks = []
        for i in range(100):
            tasks.append(get_photo())

        await asyncio.gather(*tasks)

        await gp.close()



    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except Exception as e:
        print(f"Exception: {e}")


asyncio.run(test())