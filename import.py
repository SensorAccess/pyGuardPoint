import json
import logging

import pkg_resources
from pyGuardPoint.guardpoint import GuardPointError, GuardPoint
from tqdm import tqdm

from pyGuardPoint.guardpoint_dataclasses import Cardholder

EXPORT_FILENAME = 'cardholder_export.json'
log = logging.getLogger(__name__)

# GuardPoint
GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "C:\\Users\\john_\\OneDrive\\Desktop\\MobileGuardDefault.p12"
TLS_P12_PWD = "test"

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    try:
        gp = GuardPoint(host=GP_HOST,
                        username=GP_USER,
                        pwd=GP_PASS,
                        p12_file=TLS_P12,
                        p12_pwd=TLS_P12_PWD)

        # Delete All Cardholders
        '''count = gp.get_cardholder_count()
        print(f"Deleting All Cardholders: {str(count)}")
        for i in tqdm(range(0, count)):
            batch_of_cardholders = gp.get_card_holders(limit=1, offset=i)  # Get a batch of 1 cardholder!
            if len(batch_of_cardholders) < 1:
                break;
            for cardholder in batch_of_cardholders:
                gp.delete_card_holder(cardholder)'''


        # Load the JSON file
        with open(EXPORT_FILENAME) as f:
            entries = json.load(f)

        count = len(entries)
        print(f"Importing {str(count)} entries from {EXPORT_FILENAME}.")
        for i in tqdm(range(0, count)):
            entries[i].pop('uid')
            cardholder = Cardholder(entries[i])
            #gp.delete_card_holder(cardholder)
            gp.new_card_holder(cardholder)


    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
