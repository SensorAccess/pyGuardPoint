import datetime
import logging
import sys
from typing import List, Dict, Any
from pyGuardPoint import GuardPoint, GuardPointError, GuardPointAuthType, GuardPointUnauthorized
from pysignalr.exceptions import AuthorizationError
from pysignalr.messages import CompletionMessage
from importlib.metadata import version

#sys.path.insert(1, 'pyGuardPoint_Build')
#from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, GuardPointAuthType, GuardPointUnauthorized

# GuardPoint Connection Parameters

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
GP_API_KEY = '2b2967b0-33b5-47d8-b24c-3239b325f812'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

logging.basicConfig(level=logging.DEBUG)


async def on_open() -> None:
    print('Connected to the server')


async def on_close() -> None:
    print('Disconnected from the server')


async def on_message(message: List[Dict[str, Any]]) -> None:
    print(f'Received message: {message}')

async def on_alarm_message(message: List[Dict[str, Any]]) -> None:
    print(f'Received ALARM message: {message}')

async def on_audit_message(message: List[Dict[str, Any]]) -> None:
    print(f'Received AUDIT message: {message}')
async def on_su_message(message: List[Dict[str, Any]]) -> None:
    print(f'Received SU message: {message}')
async def on_ac_message(message: List[Dict[str, Any]]) -> None:
    print(f'Received AC message: {message}')


async def on_error(message: CompletionMessage) -> None:
    print(f'Received error: {message.error}')


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    try:
        py_gp_version = version("pyGuardPoint")
        print("pyGuardPoint Version:" + py_gp_version)
        py_gp_version_int = int(py_gp_version.replace('.', ''))
        if py_gp_version_int < 188:
            print("Please Update pyGuardPoint")
            print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
            exit()

        py_sigR_version = version("pysignalr")
        print("pysignalr Version:" + py_sigR_version)
        py_sigR_version_int = int(py_sigR_version.replace('.', ''))
        if py_sigR_version_int < 130:
            print("Please Update pysignalr")
            print("\t (Within a Terminal Window) Run > 'pip install pysignalr --upgrade'")
            exit()

        gp = GuardPoint(
            host=GP_HOST,
            username=GP_USER,
            pwd=GP_PASS,
            key=GP_API_KEY,
            p12_file=TLS_P12,
            p12_pwd=TLS_P12_PWD,
            #auth=GuardPointAuthType.BEARER_TOKEN,
            auth=GuardPointAuthType.BASIC
        )

        print(f"GuardPoint Server Version: {gp.gp_version()}")
        print(f"Signal-R enabled: {gp.is_sigr_enabled()}")

        signal_client = gp.get_signal_client()

        # Set up your signal_client callbacks
        signal_client.on_open(on_open)
        signal_client.on_close(on_close)
        signal_client.on_error(on_error)
        signal_client.on('AccessEventArrived', on_ac_message)
        signal_client.on("AlarmEventArrived", on_alarm_message)
        signal_client.on("AuditEventArrived", on_audit_message)
        signal_client.on("CommEventArrived", on_message)
        signal_client.on("GeneralEventArrived", on_message)
        signal_client.on("IOEventArrived", on_message)
        signal_client.on("StatusUpdate", on_su_message)
        signal_client.on("TechnicalEventArrived", on_message)

        gp.start_listening(signal_client)
        start_time = datetime.datetime.now()

    except GuardPointError as e:
        print(f"GuardPointError: {e}")

    except GuardPointUnauthorized as e:
        print(f"GP AuthorizationError")

    except AuthorizationError as e:
        print(f"SignalR AuthorizationError")

    except Exception as e:
        print(f"Exception: {str(e)}")

    finally:
        end_time = datetime.datetime.now()
        print(start_time.strftime("%m/%d/%Y %H:%M:%S"))
        print(end_time.strftime("%m/%d/%Y %H:%M:%S"))