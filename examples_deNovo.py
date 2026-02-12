import logging
import time

from pyGuardPoint.guardpoint import GuardPoint, GuardPointError
from pyGuardPoint.guardpoint_dataclasses import Cardholder, CardholderPersonalDetail

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
                    p12_pwd=TLS_P12_PWD
                    )

    try:
        # Get a list of cardholders using filter
        cardholders = gp.get_card_holders(firstName="John", lastName='Jenkins')
        print(f"Found  {len(cardholders)} Cardholders")

        for cardholder in cardholders:
            # Delete all cardholders found
            if gp.delete_card_holder(cardholder):
                print(f"Deleted {cardholder}")

        time.sleep(1)

        # Create a New Cardholder
        cardholder_pd = CardholderPersonalDetail()
        cardholder_pd.mobile = "01234 678678"
        cardholder = Cardholder(firstName="John", lastName="Jenkins",
                                cardholderPersonalDetail=cardholder_pd)
        cardholder = gp.new_card_holder(cardholder)
        print(f"Created {cardholder.firstName}  {cardholder.lastName}")

        # Update/Change some fields
        #cardholder.securityGroupUID = '11111111-1111-1111-1111-111111111111'  # Anytime Anywhere
        cardholder.securityGroupUID = '22222222-2222-2222-2222-222222222222'  # No Access
        if gp.update_card_holder(cardholder):
            print("Cardholder Updated:")
            print("\tUID: " + cardholder.uid)
            print(f"\tFirstname: {cardholder.firstName if hasattr(cardholder, 'firstName') else ' '}")
            print("\tLastname: " + cardholder.lastName)
            print("\tCardholder Type: " + cardholder.cardholderType.typeName)
            print("\tSecurity Group: " + cardholder.securityGroup.name)


    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")




