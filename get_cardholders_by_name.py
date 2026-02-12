import logging, sys
from importlib.metadata import version
from pprint import pprint

#sys.path.insert(1, 'pyGuardPoint_Build')
#from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized
from pyGuardPoint import GuardPoint, GuardPointError

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
#GP_USER = 'remko'
#GP_PASS = 'remko'
#GP_USER = 'robert'
#GP_PASS = 'password'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"
#SITE_UID = "f342eade-eb43-4359-918d-d067d609fc38" # Sensor Office
#SITE_UID = "90be9b9d-c87f-44b0-9ff9-e0f8725abbad" # Force site filter
#SITE_UID = None

if __name__ == "__main__":
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 153:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD
                    )

    try:
        cardholders = gp.get_card_holders(cardholderIdNumber="10636076")
        #gp.u
        for cardholder in cardholders:
            #cardholder.firstname = "Frank "
            cardholder.status = "Validated"
            gp.update_card_holder(cardholder)
            #gp.delete_card_holder()
            print("Cardholder:")
            print(f"\tFirst Name: {cardholder.firstName}")
            print(f"\tLast Name: {cardholder.lastName}")
            print(f"\tEmail: {cardholder.cardholderPersonalDetail.email}")
            print(f"\townerSiteUID: {cardholder.ownerSiteUID}")
            print(f"\tCardholderUID: {cardholder.uid}")
            print(f"\tStatus: {cardholder.status}")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

        '''gp.get_sites()
        for site in gp.get_sites():
            print(f"Site:{site.name}\n")
            cardholders = gp.get_card_holders(ownerSiteUID=site.uid, select_ignore_list=['photo'])

            for cardholder in cardholders:
                #print("Cardholder:")
                #print(f"\t{cardholder.lastName}")
                #print(f"\t{cardholder.cardholderPersonalDetail.email}")
                #print(cardholder.dict(non_empty_only=True))
                #cardholder.pretty_print()
                cardholder = gp.get_card_holder(uid="a7628540-0a5f-4c05-8347-59913c42d27e")
                print("Cardholder:")
                print(f"\t{cardholder.uid}")
                print(f"\t{cardholder.lastName}")
                print(f"\t{cardholder.cardholderPersonalDetail.email}")'''




