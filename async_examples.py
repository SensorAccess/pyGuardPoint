import json
import logging, sys

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPointAsync, GuardPointError, Cardholder, Area, Card

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
            for entry in resp:
                if isinstance(entry, Cardholder):
                    cardholder = entry
                    print("Cardholder:")
                    print("\tUID: " + cardholder.uid)
                    print("\tFirstname: " + cardholder.firstName)
                    print("\tLastname: " + cardholder.lastName)
                if isinstance(entry, Area):
                    area = entry
                    print("Area:")
                    print("\tUID: " + area.uid)
                    print("\tName: " + area.name)
                if isinstance(entry, Card):
                    card = entry
                    print("Card:")
                    print("\tCode: " + card.cardCode)
                    print("\tType: " + card.cardType)

    try:
        #gp.get_card_holder(task_complete, uid="422edea0-589d-4224-af0d-77ed8a97ca57")
        #gp.get_card_holder(task_complete, card_code="1B1A1B1C")
        #gp.get_card_holders(task_complete, search_terms="john owen")
        #gp.get_card_holders(task_complete, search_terms="robert")
        #gp.get_card_holders(task_complete, search_terms="josh")
        #gp.get_card_holders(task_complete, search_terms="frida")
        #gp.get_areas(task_complete)
        #gp.get_cards(task_complete)
        area_list = []
        area_list.append(Area({'uid': '00000000-0000-0000-0000-100000000001', 'area': "Offsite"}))
        gp.get_card_holders(task_complete, search_terms="john owen john.owen@countermac.com", areas=area_list, filter_expired=False)
    except Exception as e:
        print(e)

    print("Got to End")