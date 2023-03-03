import logging

from pyGuardPoint import GuardPointAsync, Cardholder, GuardPointError

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPointAsync(host="sensoraccess.duckdns.org", pwd="password")

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
        gp.get_card_holder(task_complete, uid="422edea0-589d-4224-af0d-77ed8a97ca57")
        gp.get_card_holder(task_complete, card_code="1B1A1B1C")
        gp.get_card_holders(task_complete, search_terms="john")
        gp.get_card_holders(task_complete, search_terms="robert")
        gp.get_card_holders(task_complete, search_terms="josh")
        gp.get_card_holders(task_complete, search_terms="frida")
    except Exception as e:
        print(e)

    print("Got to End")