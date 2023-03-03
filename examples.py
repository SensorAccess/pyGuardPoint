import logging

from pyGuardPoint.guardpoint import GuardPoint, GuardPointError
from pyGuardPoint.guardpoint_dataclasses import Cardholder

import pkg_resources
py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        cardholder = gp.get_card_holder(card_code='1B1A1B1C')

        print("Cardholder:")
        print("\tUID: " + cardholder.uid)
        print(f"\tFirstname: {cardholder.firstName if hasattr(cardholder, 'firstName') else ' '}")
        print("\tLastname: " + cardholder.lastName)
        print("\tCardholder Type: " + cardholder.cardholderType.typeName)
        print("\tNum of Cards: " + str(len(cardholder.cards)))
        print("\tOwnerSiteUID:" + cardholder.ownerSiteUID)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

    try:
        cards = gp.get_cards()
        print("Got back a: " + str(type(cards)))
        for card in cards:
            print("Card:")
            print("\tCard UID: " + card.uid)
            print("\tCard Type: " + card.cardType)
            print("\tCard Code: " + card.cardCode)

        if gp.delete_card(card):
            uid = gp.add_card(card)
            print("New Card added and assigned with the UID:" + uid)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

    try:
        security_groups = gp.get_security_groups()
        print("Got back a: " + str(type(security_groups)))
        for security_group in security_groups:
            print("\t " + security_group.name)
    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

    try:
        # Example getting a single cardholder
        cardholder = gp.get_card_holder("87ff8a5d-ef0c-4367-b773-e10e0b031679")
        print("Got back a: " + str(type(cardholder)))
        if isinstance(cardholder, Cardholder):
            print("Cardholder:")
            print("\tUID: " + cardholder.uid)
            print("\tFirstname: " + cardholder.firstName)
            print("\tLastname: " + cardholder.lastName)
            print("\tCardholder Type: " + cardholder.cardholderType.typeName)
            print("\tNum of Cards: " + str(len(cardholder.cards)))
            print("\tOwnerSiteUID:" + cardholder.ownerSiteUID)
            for card in cardholder.cards:
                print("\t\tCard UID: " + card.uid)
                print("\t\tCard Type: " + card.cardType)
                print("\t\tCard Code: " + card.cardCode)

            # Delete all associated cards
            for card in cardholder.cards:
                gp.delete_card(cardholder.cards[0])

            # Delete the cardholder
            gp.delete_card_holder(cardholder)
            print("Cardholder: " + cardholder.firstName + " deleted.")

            # Re-add the cardholder
            uid = gp.add_card_holder(cardholder)
            print("Cardholder: " + cardholder.firstName + " added, with the new UID:" + uid)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

    try:
        # Example getting a list of cardholders
        cardholders = gp.get_card_holders(limit=1, search_terms="Frida")
        print("Got back a: " + str(type(cardholders)) + " containing: " + str(len(cardholders)) + " entry.")
        if isinstance(cardholders, list):
            for cardholder in cardholders:
                print("Cardholder: ")
                print("\tUID: " + cardholder.uid)
                print("\tFirstname: " + cardholder.firstName)
                print("\tLastname: " + cardholder.lastName)
    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

    '''try:
        # Example get all cardholders in batches of 5
        all_cardholders = []
        batch_of_cardholders = gp.get_card_holders(limit=5, offset=0)
        while len(batch_of_cardholders) > 0:
            all_cardholders.extend(batch_of_cardholders)
            batch_of_cardholders = gp.get_card_holders(limit=5, offset=(len(all_cardholders)))

        print(f"Got a list of: {len(all_cardholders)}")
        for cardholder in all_cardholders:
            print("Cardholder: ")
            print("\tUID: " + cardholder.uid)
            print("\tFirstname: " + cardholder.firstName)
            print("\tLastname: " + cardholder.lastName)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")'''

    '''try:
        # Example delete the first cardholder
        cardholder_list = gp.get_card_holders(limit=1, offset=0)
        if len(cardholder_list) > 0:
            cardholder = cardholder_list[0]
            if gp.delete_card_holder(cardholder.uid):
                print("Cardholder: " + cardholder.firstName + " deleted.")

                uid = gp.add_card_holder(cardholder)
                print("Cardholder: " + cardholder.firstName + " added, with the new UID:" + uid)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")'''