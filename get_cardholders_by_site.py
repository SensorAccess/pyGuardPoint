import logging, sys

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized

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
                    site_uid="11111111-1111-1111-1111-111111111111")

    try:
        cardholder = gp.get_card_holder(uid="a7628540-0a5f-4c05-8347-59913c42d27e")
        if cardholder is not None:
            print("Cardholder:")
            print(f"\t{cardholder.uid}")
            print(f"\t{cardholder.lastName}")
            print(f"\t{cardholder.cardholderPersonalDetail.email}")


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



    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
