import logging, sys
from importlib.metadata import version
from strgen import StringGenerator # pip install StringGenerator

# Use PyPi Module
#from pyGuardPoint import GuardPoint, GuardPointError

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

py_gp_version = version("pyGuardPoint")

GP_HOST = 'https://sensoraccess.duckdns.org'
# GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD,
                    site_uid='11111111-1111-1111-1111-111111111111')

    try:
        cardholder = gp.get_card_holder(card_code='1B1A1B1C')

        print("Updating the following fields:")
        print(f"\tcF_StringField_20: {cardholder.cardholderCustomizedField.cF_StringField_20}")
        print(f"\tdescription: {cardholder.description}")
        print(f"\tcityOrDistrict: {cardholder.cardholderPersonalDetail.cityOrDistrict}")

        cardholder.cardholderCustomizedField.cF_StringField_20 = "cf20:" + StringGenerator(r"[\w]{30}").render()
        cardholder.description = "D:" + StringGenerator(r"[\w]{30}").render()
        cardholder.cardholderPersonalDetail.cityOrDistrict = "cOrD:" + StringGenerator(r"[\w]{30}").render()
        cardholder.cardholderPersonalDetail.email = ""

        print("Detected the following changes:")
        print(cardholder.dict(editable_only=True, changed_only=True))
        print(cardholder.cardholderCustomizedField.dict(changed_only=True))
        print(cardholder.cardholderPersonalDetail.dict(changed_only=True))

        if gp.update_card_holder(cardholder):
            updated_cardholder = gp.get_card_holder(uid=cardholder.uid)
            #updated_cardholder.pretty_print()
            print("updated_cardholder:")
            print(f"\tcF_StringField_20: {updated_cardholder.cardholderCustomizedField.cF_StringField_20}")
            print(f"\tdescription: {updated_cardholder.description}")
            print(f"\tcityOrDistrict: {updated_cardholder.cardholderPersonalDetail.cityOrDistrict}")
            print(f"\temail: {updated_cardholder.cardholderPersonalDetail.email}")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")