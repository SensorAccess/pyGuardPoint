import logging, sys
import pkg_resources
from pyGuardPoint import GuardPoint, GuardPointError, Cardholder, CardholderPersonalDetail, Card, \
    CardholderCustomizedField
import jwt
import pprint

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")
    gp_token = gp.get_token()
    decoded_token = jwt.decode(gp_token, options={"verify_signature": False}, algorithms=["HS256"])
    pprint.pprint(decoded_token)
    
    # New GuardPoint Connection using the token
    gp = GuardPoint(host="sensoraccess.duckdns.org", username=None, pwd=None, token=gp_token)
    cardholder_count = gp.get_card_holders(count=True)
    print(f"Total Cardholders: {cardholder_count}")