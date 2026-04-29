import asyncio
import logging, sys
import pprint

#from pyGuardPoint import GuardPoint, GuardPointError, Cardholder, CardholderPersonalDetail, Card, \
#    CardholderCustomizedField, SortAlgorithm

from pyGuardPoint_Build.pyGuardPoint import GuardPointUnauthorized, GuardPointAsyncIO, GuardPoint,GuardPointError

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host=GP_HOST,
                           username=GP_USER,
                           pwd=GP_PASS,
                           p12_file=TLS_P12,
                           p12_pwd=TLS_P12_PWD)

    try:
        print("\nTrying to get Cardholder from cardCode")
        cardholder = gp.get_card_holder(card_code="0A092780")
        cardholder.pretty_print()
    except GuardPointError as e:
        print(f"GuardPointError: {e}")

    # Alternative way
    try:
        print("\nTrying Alternative way of getting Cardholder from cardCode")
        cards = gp.get_cards(cardCode="0A092780")
        if len(cards) == 1:
            card = cards[0]
            if card.cardholderUID is not None:
                cardholder = gp.get_card_holder(uid=card.cardholderUID)
                cardholder.pretty_print()


    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

