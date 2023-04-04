import logging, sys
from _socket import gaierror

import pkg_resources

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, Cardholder
from pyGuardPoint_Build.pyGuardPoint.guardpoint_dataclasses import CardholderPersonalDetail, CardholderCustomizedField, \
    Card

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", port=10695, pwd="password")

    try:
        cardholders = gp.get_card_holders(search_terms="Owen9700")
        for cardholder in cardholders:
            # Delete all cardholders cards first
            for card in cardholder.cards:
                gp.delete_card(card)
                print(f"Card: {card.cardCode} Deleted")

            # Delete the cardholder
            if gp.delete_card_holder(cardholder):
                print(f"Cardholder {cardholder.firstName} {cardholder.lastName} Deleted")

        cardholder_pd = CardholderPersonalDetail(email="john.owen@eml.cc")
        cardholder_cf = CardholderCustomizedField(cF_StringField_20="hello")
        cardholder = Cardholder(firstName="John", lastName="Owen9700",
                                cardholderPersonalDetail=cardholder_pd,
                                cardholderCustomizedField=cardholder_cf)
        cardholder = gp.new_card_holder(cardholder)
        print(f"Cardholder {cardholder.firstName} {cardholder.lastName} Created")

        # New Card
        card = Card(cardType="Magnetic", cardCode="1A1B1C8B")
        # If we make a new card independently - we must set cardholderUID and status
        # card = gp.new_card(card=card)
        # card.cardholderUID = cardholder.uid
        # card.status = "Used"

        cardholder.cards.append(card)
        cardholder.firstName = "Frank100"
        print(cardholder.changed_attributes)

        if gp.update_card_holder(cardholder):
            cardholder = gp.get_card_holder(uid=cardholder.uid)
            print(f"Cardholder {cardholder.firstName} {cardholder.lastName} Updated")
            print(f"\tEmail: {cardholder.cardholderPersonalDetail.email}")
            print(f"\tCards: {cardholder.cards}")
            # cardholder.pretty_print()

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except gaierror as e:
        print(f"Get Address Info Failed")
    except Exception as e:
        print(f"Exception: {type(e)}-{e}")
