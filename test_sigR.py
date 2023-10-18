import logging
import sys
from typing import List, Dict, Any

import pkg_resources
from pyGuardPoint import GuardPoint, GuardPointError
from pysignalr.exceptions import AuthorizationError
from pysignalr.messages import CompletionMessage

# GuardPoint
GP_HOST = 'https://sensoraccess.duckdns.org'
#GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "C:\\Users\\john_\\OneDrive\\Desktop\\MobGuardDefault\\MobileGuardDefault.p12"
TLS_P12_PWD = "test"

#sys.path.insert(1, 'pyGuardPoint_Build')
#from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

#_logger = logging.getLogger('pysignalr.transport')
#_logger.setLevel(logging.DEBUG)
logging.basicConfig(level = logging.DEBUG)
async def on_open() -> None:
    print('Connected to the server')


async def on_close() -> None:
    print('Disconnected from the server')


async def on_message(message: List[Dict[str, Any]]) -> None:
    print(f'Received message: {message}')


async def on_error(message: CompletionMessage) -> None:
    print(f'Received error: {message.error}')


if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    try:
        gp = GuardPoint(host=GP_HOST,
                        username=GP_USER,
                        pwd=GP_PASS,
                        p12_file=TLS_P12,
                        p12_pwd=TLS_P12_PWD)

        signal_client = gp.get_signal_client()

        signal_client.on_open(on_open)
        signal_client.on_close(on_close)
        signal_client.on_error(on_error)
        signal_client.on('AccessEventArrived', on_message)
        signal_client.on("AlarmEventArrived", on_message)
        signal_client.on("AuditEventArrived", on_message)
        signal_client.on("CommEventArrived", on_message)
        signal_client.on("GenaralEventArrived", on_message)
        signal_client.on("IOEventArrived", on_message)
        signal_client.on("StatusUpdate", on_message)
        signal_client.on("TechnicalEventArrived", on_message)

        gp.run_signal_client(signal_client)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except AuthorizationError as e:
        print(f"SignalR AuthorizationError")
    except Exception as e:
        print(f"Exception: {str(e)}")