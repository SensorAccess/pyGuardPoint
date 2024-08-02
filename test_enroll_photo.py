import logging, sys
from importlib.metadata import version
from strgen import StringGenerator  # pip install StringGenerator

# Use PyPi Module
#from pyGuardPoint import GuardPoint, GuardPointError

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, CardholderPersonalDetail, \
    CardholderCustomizedField, Cardholder

py_gp_version = version("pyGuardPoint")

GP_HOST = 'https://sensoraccess.duckdns.org'
# GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"

photo = "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"

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD,
                    site_uid='f342eade-eb43-4359-918d-d067d609fc38')

    try:
        cardholder_pd = CardholderPersonalDetail(email="john.owen@eml.cc")
        cardholder_cf = CardholderCustomizedField()
        setattr(cardholder_cf, "cF_StringField_20", "hello")
        cardholder = Cardholder(firstName="John", lastName="Owen87",
                                insideAreaUID="00000000-0000-0000-0000-100000000001",
                                photo=photo,
                                cardholderPersonalDetail=cardholder_pd,
                                cardholderCustomizedField=cardholder_cf)

        cardholder = gp.new_card_holder(cardholder, enroll_face_from_photo=True)

        cardholder = gp.get_card_holder(cardholder.uid)

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

        if gp.update_card_holder(cardholder, enroll_face_from_photo=True):
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
