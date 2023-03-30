import logging, sys
import pkg_resources
from pyGuardPoint import GuardPoint, GuardPointError, Cardholder, CardholderPersonalDetail, Card, \
    CardholderCustomizedField
import jwt
import pprint

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 59:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")
    gp_token = gp.get_token()
    decoded_token = jwt.decode(gp_token, options={"verify_signature": False}, algorithms=["HS256"])
    pprint.pprint(decoded_token)
    print('\n\n\n')
    # New GuardPoint Connection using the token
    print("--- Logging in with token\n")
    gp = GuardPoint(host="sensoraccess.duckdns.org", username=None, pwd=None, token=gp_token)
    cardholder_count = gp.get_card_holders(count=True)
    print(f"Total Cardholders: {cardholder_count}")