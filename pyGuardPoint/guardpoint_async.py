import logging
import threading
from datetime import time, datetime
from time import sleep
from concurrent.futures import ThreadPoolExecutor

from pyGuardPoint.guardpoint import GuardPoint


class GuardPointAsync():

    def __init__(self, **kwargs):
        self.gp = GuardPoint(**kwargs)
        self.executor = ThreadPoolExecutor(max_workers=1)

    def get_card_holder(self, on_finished, uid):
        future = self.executor.submit(self.gp.get_card_holder, uid)
        future.add_done_callback(lambda f: on_finished(f.result()))

    def get_card_holders(self, on_finished, offset=0, limit=10, searchPhrase=None):
        future = self.executor.submit(self.gp.get_card_holders, offset, limit, searchPhrase)
        future.add_done_callback(lambda f: on_finished(f.result()))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPointAsync(host="sensoraccess.duckdns.org", pwd="password")

    def task_complete(resp):
        print("Response:" + str(resp))

    try:
        gp.get_card_holder(task_complete, "422edea0-589d-4224-af0d-77ed8a97ca57")
        gp.get_card_holders(task_complete, searchPhrase="john")
        gp.get_card_holders(task_complete, searchPhrase="robert")
        gp.get_card_holders(task_complete, searchPhrase="josh")
        gp.get_card_holders(task_complete, searchPhrase="frida")
    except Exception as e:
        print(e)

    print("Got to End")
