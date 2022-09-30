import logging
import threading
from datetime import time, datetime
from time import sleep
from concurrent.futures import ThreadPoolExecutor

from pyGuardPoint.dataclasses.cardholder import Cardholder
from pyGuardPoint.guardpoint import GuardPoint, GuardPointError


class GuardPointAsync():

    def __init__(self, **kwargs):
        self.gp = GuardPoint(**kwargs)
        self.executor = ThreadPoolExecutor(max_workers=1)

    def get_card_holder(self, on_finished, uid):
        try:
            future = self.executor.submit(self.gp.get_card_holder, uid)
            result = future.result()
        except GuardPointError as e:
            result = e
        future.add_done_callback(on_finished(result))

    def get_card_holders(self, on_finished, offset=0, limit=10, searchPhrase=None):
        try:
            future = self.executor.submit(self.gp.get_card_holders, offset, limit, searchPhrase)
            result = future.result()
        except GuardPointError as e:
            result = e
        future.add_done_callback(on_finished(result))



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPointAsync(host="sensoraccess.duckdns.org", pwd="pasword")

    def task_complete(resp):
        if isinstance(resp, GuardPointError):
            print(f"Got back a GuardPointError: {resp}")
        if isinstance(resp, Cardholder):
            cardholder = resp
            print("Cardholder:")
            print("\tUID: " + cardholder.uid)
            print("\tFirstname: " + cardholder.firstName)
            print("\tLastname: " + cardholder.lastName)

        if isinstance(resp, list):
            cardholders = resp
            for cardholder in cardholders:
                print("Cardholder: ")
                print("\tUID: " + cardholder.uid)
                print("\tFirstname: " + cardholder.firstName)
                print("\tLastname: " + cardholder.lastName)

    try:
        gp.get_card_holder(task_complete, "422edea0-589d-4224-af0d-77ed8a97ca57")
        gp.get_card_holders(task_complete, searchPhrase="john")
        gp.get_card_holders(task_complete, searchPhrase="robert")
        gp.get_card_holders(task_complete, searchPhrase="josh")
        gp.get_card_holders(task_complete, searchPhrase="frida")
    except Exception as e:
        print(e)

    print("Got to End")
