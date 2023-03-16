import logging, sys
import pkg_resources
from pyGuardPoint import GuardPoint
from strgen import StringGenerator # pip install StringGenerator

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 47:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        cardholder = gp.get_card_holder(card_code='1B1A1B1C')

        print("Updating the following fields:")
        print(f"\tcF_StringField_20: {cardholder.cardholderCustomizedField.cF_StringField_20}")
        print(f"\tdescription: {cardholder.description}")
        print(f"\tcityOrDistrict: {cardholder.cardholderPersonalDetail.cityOrDistrict}")

        cardholder.cardholderCustomizedField.cF_StringField_20 = "cf20:" + StringGenerator("[\w\d]{10}").render()
        cardholder.description = "D:" + StringGenerator("[\w\d]{10}").render()
        cardholder.cardholderPersonalDetail.cityOrDistrict = "cOrD:" + StringGenerator("[\w\d]{10}").render()

        print("\n\n Detected the following fields have changed:")
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

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")