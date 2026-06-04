import logging, sys
from importlib.metadata import version
from pyGuardPoint import GuardPoint, GuardPointError, Cardholder, CardholderPersonalDetail, Card, \
    CardholderCustomizedField

py_gp_version = version("pyGuardPoint")
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 150:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()

GP_HOST = 'https://sensoraccess.duckdns.org'
# GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
#TLS_P12 = None
TLS_P12_PWD = "test"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host=GP_HOST,
                         username=GP_USER,
                         pwd=GP_PASS,
                         p12_file=TLS_P12,
                         p12_pwd=TLS_P12_PWD)

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

        card = Card(cardType="Magnetic", cardCode="1B1A1B1C")
        cardholder_pd = CardholderPersonalDetail(email="john.owen@eml.cc")
        cardholder_cf = CardholderCustomizedField(cF_StringField_20="hello")
        cardholder = Cardholder(firstName="John", lastName="Owen9700",
                                cardholderPersonalDetail=cardholder_pd,
                                cardholderCustomizedField=cardholder_cf,
                                cards=[card])
        cardholder = gp.new_card_holder(cardholder)
        print(f"Cardholder {cardholder.firstName} {cardholder.lastName} Created")

        # New Card
        card = Card(cardType="Magnetic", cardCode="1B1A1B1C")
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
            print(f"\tcF_StringField_20: {cardholder.cardholderCustomizedField.cF_StringField_20}")
            print(f"\tCards: {cardholder.cards}")
            # cardholder.pretty_print()



    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
