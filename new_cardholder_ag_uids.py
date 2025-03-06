import logging, sys
from _socket import gaierror
from importlib.metadata import version

from pyGuardPoint import GuardPoint, GuardPointError, CardholderPersonalDetail, CardholderCustomizedField, Cardholder

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 181:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)

    try:
        # Delete any previously made Test Users + cards
        cardholders = gp.get_card_holders(search_terms="Test-User", threshold=80)
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
        access_groups_uid_list = []
        for access_group in access_groups:
            if access_group.uid != "22222222-2222-2222-2222-222222222222": # Ignore No Access Group
                access_groups_uid_list.append(access_group.uid)
            #print(access_group.name)

        # Create a New Cardholder
        cardholder_pd = CardholderPersonalDetail(email="john.owen@countermac.com")
        cardholder_cf = CardholderCustomizedField()
        setattr(cardholder_cf, "cF_StringField_20", "hello")
        cardholder = Cardholder(firstName="John", lastName="Test-User",
                                insideAreaUID="00000000-0000-0000-0000-100000000001",
                                cardholderPersonalDetail=cardholder_pd,
                                cardholderCustomizedField=cardholder_cf,
                                accessGroupUIDs=";".join(access_groups_uid_list))
        cardholder = gp.new_card_holder(cardholder)
        print(f"Cardholder {cardholder.firstName} {cardholder.lastName} {cardholder.cardholderCustomizedField.cF_StringField_20} Created\n")
        print("GP Multi Access Group: " + cardholder.securityGroup.name + "(" + cardholder.securityGroup.uid+ ")\n")
        print("GP Personal Door Access Groups:")
        for pag in cardholder.accessGroupUIDs.split(";"):
            print("\t" + pag)

        access_groups_uid_list = ["11111111-1111-1111-1111-111111111111"]
        cardholder.accessGroupUIDs = ";".join(access_groups_uid_list)
        if(gp.update_card_holder(cardholder)):
            print(f"Updated Cardholder:")
            updated_cardholder = gp.get_card_holder(cardholder.uid)
            print("First Name: " + updated_cardholder.firstName)
            print("AccessGroupUIDs:" + updated_cardholder.accessGroupUIDs)


    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except gaierror as e:
        print(f"Get Address Info Failed")
    except Exception as e:
        print(f"Exception: {type(e)}-{e}")
