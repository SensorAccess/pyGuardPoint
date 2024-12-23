import logging, sys
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, CardholderPersonalDetail

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
        personalDetails = CardholderPersonalDetail(email="john.owen@countermac.com")
        cardholders = gp.get_card_holders(offset=10, limit=99)

        print(len(cardholders))

        '''for cardholder in cardholders:
            print("Cardholder:")
            print(f"\t{cardholder.lastName}")
            print(f"\t{cardholder.cardholderPersonalDetail.email}")
            print(cardholder.dict(non_empty_only=True))
            #cardholder.pretty_print()'''



    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")