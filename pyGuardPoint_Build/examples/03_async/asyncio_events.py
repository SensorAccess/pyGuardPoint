import asyncio
import logging
import sys
from importlib.metadata import version

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')

from pyGuardPoint_Build.pyGuardPoint import GuardPointAsyncIO, GuardPointError, GuardPointUnauthorized, EventOrder

# GuardPoint
GP_HOST = 'https://sensoraccess.duckdns.org'
# GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
#TLS_P12 = "C:\\Users\\User\\OneDrive\\Desktop\\MobGuardDefault\\MobileGuardDefault.p12"
TLS_P12_PWD = "test"

import threading
from typing import Awaitable, TypeVar

T = TypeVar("T")


def _start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


_LOOP = asyncio.new_event_loop()
_LOOP_THREAD = threading.Thread(
    target=_start_background_loop, args=(_LOOP,), daemon=True
)
_LOOP_THREAD.start()


def asyncio_run(coro: Awaitable[T], timeout=30) -> T:
    """
    Runs the coroutine in an event loop running on a background thread,
    and blocks the current thread until it returns a result.
    This plays well with gevent, since it can yield on the Future result call.

    :param coro: A coroutine, typically an async method
    :param timeout: How many seconds we should wait for a result before raising an error
    """
    return asyncio.run_coroutine_threadsafe(coro, _LOOP).result(timeout=timeout)


if __name__ == "__main__":
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 170:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    logging.basicConfig(level=logging.DEBUG)

    c = (
        "\033[0m",  # End of color
        "\033[36m",  # Cyan
        "\033[91m",  # Red
        "\033[35m",  # Magenta
    )

    try:
        async def get_token():
            gp = GuardPointAsyncIO(host=GP_HOST,
                                   username=GP_USER,
                                   pwd=GP_PASS,
                                   p12_file=TLS_P12,
                                   p12_pwd=TLS_P12_PWD,
                                   site_uid="11111111-1111-1111-1111-111111111111")
            api = await gp.is_api_enabled()
            if not api:
                print("Warning API appears to be not enabled")
            token = await gp.get_token()
            await gp.close()
            return token

        async def get_access_events(gp_token, limit=3, offset=0):
            gp = GuardPointAsyncIO(host=GP_HOST,
                                   username=GP_USER,
                                   pwd=GP_PASS,
                                   p12_file=TLS_P12,
                                   p12_pwd=TLS_P12_PWD,
                                   site_uid="11111111-1111-1111-1111-111111111111")
            gp.set_token(gp_token)
            response = await gp.get_access_events(limit=limit, offset=offset, orderby=EventOrder.LOG_ID_ASC, min_log_id=991)
            await gp.close()
            return response

        async def get_access_events_count(gp_token):
            gp = GuardPointAsyncIO(host=GP_HOST,
                                   username=GP_USER,
                                   pwd=GP_PASS,
                                   p12_file=TLS_P12,
                                   p12_pwd=TLS_P12_PWD,
                                   site_uid="11111111-1111-1111-1111-111111111111")
            gp.set_token(gp_token)
            response = await gp.get_access_events_count()
            await gp.close()
            return response


        async def main():
            # Get the API Token first
            print(f"\n{c[1]}********* Login and get token **********" + c[0])
            gp_token = await get_token()
            print(f"{c[3]}Token:{gp_token}" + c[0])
            access_event_count = await get_access_events_count(gp_token)
            print(f"Access Event Count:{access_event_count}")
            # Create a list of the requests to run asynchronously
            tasks = []
            tasks.append(get_access_events(gp_token,3, 0))
            tasks.append(get_access_events(gp_token,3, 3))
            tasks.append(get_access_events(gp_token,3, 6))
            tasks.append(get_access_events(gp_token,3, 9))
            # Run sasynchronous requests
            print(f"\n{c[1]}********* Run asynchronous requests **********" + c[0])
            results = await asyncio.gather(*tasks)
            # Results is a list of lists, so we new pack into a single one
            access_events = []
            for result in results:
                access_events += result
            print("Got " + str(len(access_events)) + " access logs.")
            for event in access_events:
                print(event)


        asyncio_run(main())

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except Exception as e:
        print(f"Exception: {e}")
