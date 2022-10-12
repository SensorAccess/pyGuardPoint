import json
import logging

from pyGuardPoint.guardpoint import GuardPointError, GuardPoint
from tqdm import tqdm

from pyGuardPoint.guardpoint_dataclasses import Cardholder

EXPORT_FILENAME = 'cardholder_export.json'
GP_HOST = 'sensoraccess.duckdns.org'
GP_USER = 'Admin'
GP_PASS = 'password'

log = logging.getLogger(__name__)

try:
    gp = GuardPoint(host=GP_HOST, username=GP_USER, pwd=GP_PASS)

    # Load the JSON file
    with open(EXPORT_FILENAME) as f:
        entries = json.load(f)

    count = len(entries)
    print(f"Importing {str(count)} entries from {EXPORT_FILENAME}.")
    for i in tqdm(range(0, count)):
        cardholder = Cardholder(entries[i])
        gp.delete_card_holder(cardholder)
        gp.add_card_holder(cardholder)


except GuardPointError as e:
    print(f"GuardPointError: {e}")
except Exception as e:
    print(f"Exception: {e}")
