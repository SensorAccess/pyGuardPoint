import json

from pyGuardPoint.guardpoint import GuardPointError, GuardPoint
from tqdm import tqdm


EXPORT_FILENAME = '../cardholder_export.json'
GP_HOST = 'sensoraccess.duckdns.org'
GP_USER = 'Admin'
GP_PASS = 'password'

try:
    gp = GuardPoint(host=GP_HOST, username=GP_USER, pwd=GP_PASS)
    count = gp.get_cardholder_count()
    print(f"Total Cardholders: {str(count)}")
    count = 1
    #all_cardholders = []
    f = open(EXPORT_FILENAME, "w")
    f.write("[\n")
    for i in tqdm(range(0, count)):
        batch_of_cardholders = gp.get_card_holders(limit=1, offset=i) # Get a batch of 1 cardholder!
        if len(batch_of_cardholders) < 1:
            break;
        f.write(json.dumps(batch_of_cardholders[0].dict(), indent=4))
        # Check is last cardholder
        if i == (count -1):
            f.write("\n") # No comma after last entry
        else:
            f.write(",\n")
        #all_cardholders.extend(batch_of_cardholders)

    #print(f"Got back {len(all_cardholders)} cardholders")
    f.write("]\n")
    f.close()
    print(f"File {EXPORT_FILENAME} written.")

except GuardPointError as e:
    print(f"GuardPointError: {e}")
except Exception as e:
    print(f"Exception: {e}")
