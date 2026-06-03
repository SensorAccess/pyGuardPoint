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


async def start_sigR(connection_id):
    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)

    signal_client = gp.get_signal_client()

    async def on_message(msg):
        print("Msg received on connection num:  " + str(connection_id))

    # Set up your signal_client callbacks
    signal_client.on('AccessEventArrived', on_message)
    signal_client.on("AlarmEventArrived", on_message)
    signal_client.on("AuditEventArrived", on_message)
    signal_client.on("CommEventArrived", on_message)
    signal_client.on("GeneralEventArrived", on_message)
    signal_client.on("IOEventArrived", on_message)
    signal_client.on("StatusUpdate", on_message)
    signal_client.on("TechnicalEventArrived", on_message)

    await gp.start_listening(signal_client)

asyncio.run(start_sigR(1))

start_sigR(2)
#start_sigR(3)


