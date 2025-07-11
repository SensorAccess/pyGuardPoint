import logging, sys
from _socket import gaierror

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized, \
    CardholderPersonalDetail, CardholderCustomizedField, Cardholder, Card

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
                    p12_pwd=TLS_P12_PWD,
                    #site_uid="11111111-1111-1111-1111-111111111111"
    )

    try:
        # Delete any previously made Test Users + cards
        cardholders = gp.get_card_holders(search_terms="O'Neil", lastName="O'Neil", threshold=50)
        if len(cardholders) == 0:
            print("No Cardholder Found")
        for cardholder in cardholders:
            # Delete all cardholders cards first
            for card in cardholder.cards:
                gp.delete_card(card)
                print(f"Card: {card.cardCode} Deleted")

            # Delete the cardholder
            if gp.delete_card_holder(cardholder):
                print(f"Cardholder {cardholder.firstName} {cardholder.lastName} Deleted")

        # Get list of access Groups
        access_groups = gp.get_access_groups()
        print(access_groups)
        access_groups_uid_list = []
        for access_group in access_groups:
            if access_group.uid != "22222222-2222-2222-2222-222222222222":
                access_groups_uid_list.append(access_group.uid)
            #print(access_group.name)


        # Create a New Cardholder
        cardholder_pd = CardholderPersonalDetail(email="john.owen@countermac.com")
        cardholder_cf = CardholderCustomizedField()
        setattr(cardholder_cf, "cF_StringField_20", "hello")
        cardholder = Cardholder(firstName="John", lastName="O'Neil",
                                insideAreaUID="00000000-0000-0000-0000-100000000001",
                                cardholderPersonalDetail=cardholder_pd,
                                cardholderCustomizedField=cardholder_cf,
                                accessGroupUIDs=access_groups_uid_list)
        cardholder = gp.new_card_holder(cardholder)
        print(f"Cardholder {cardholder.firstName} {cardholder.lastName} {cardholder.cardholderCustomizedField.cF_StringField_20} Created")
        print("New Cardholder AccessGroups:" + cardholder.accessGroupUIDs)
        # Append Cardholder
        # New Card
        card = Card(cardType="Magnetic", cardCode="1A1B1C9D")
        # If we make a new card independently - we must set cardholderUID and status
        # card = gp.new_card(card=card)
        # card.cardholderUID = cardholder.uid
        # card.status = "Used"

        cardholder.cards.append(card)
        cardholder.firstName = "Frank100"

        #print(cardholder.changed_attributes)

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
