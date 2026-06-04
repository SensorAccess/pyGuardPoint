import logging, csv
import os
import random
from importlib.metadata import version

from pyGuardPoint import GuardPoint, GuardPointError, EventOrder

GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"
SITE_UID = None  # All Sites
#SITE_UID = "f342eade-eb43-4359-918d-d067d609fc38" # Sensor Office
CSV_FILENAME = "access_events.csv"


# A function to trigger extra access events
def simulate_access_events(cardCodes):
    online_readers = []
    # Cycle through all Readers + fire event
    readers = gp.get_readers()
    for reader in readers:
        controller = gp.get_controller(reader.controllerUID)
        if controller.isActivated and controller.isConnected:
            online_readers.append((reader.controllerUID, reader.number))
    if len(online_readers) > 0:
        for online_reader in online_readers:
            if gp.simulate_access_event(
                    controller_uid=online_reader[0],
                    reader_num=online_reader[1],
                    card_code=random.choice(cardCodes)):
                print(f"Access Event Fired on reader:{online_reader[1]}, controller:{online_reader[0]}")
    else:
        print("No online readers found")


def get_last_row(filename):
    with open(filename, 'r+') as file:
        reader = csv.reader(file)
        last_row = None
        for row in reader:
            last_row = row
        return last_row


if __name__ == "__main__":
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 174:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD,
                    site_uid=SITE_UID)

    try:
        # Comment out/in to add extra events
        cardCodes = ["00001235","12345678"]
        simulate_access_events(cardCodes)

        # Create the CSV_FILE if it does not exist
        if not os.path.isfile(CSV_FILENAME):
            f = open(CSV_FILENAME, "a+")
            f.close()

        # Get the last LogID entry
        last_row = get_last_row(CSV_FILENAME)
        if last_row is not None:
            last_logID = last_row[0]
        else:
            last_logID = 0
        print("Last logID in CSV:", last_logID)

        # Get all remaining Access Events - We can only get events in batches of 50
        access_events = []
        access_events_batch = gp.get_access_events(orderby=EventOrder.LOG_ID_ASC,
                                                   offset=len(access_events), limit=50,
                                                   min_log_id=int(last_logID))
        while len(access_events_batch) > 0:
            access_events = access_events + access_events_batch
            access_events_batch = gp.get_access_events(orderby=EventOrder.LOG_ID_ASC,
                                                       offset=len(access_events), limit=50,
                                                       min_log_id=int(last_logID))

        # Write the Access Event into a local CSV file
        with open(CSV_FILENAME, 'a+') as csvfile:
            writer = csv.writer(csvfile)
            for access_event in access_events:
                writer.writerow([access_event.logID, access_event.dateTime, access_event.accessDeniedCode, access_event.cardCode])
                '''print("Access Event:")
                print(f"\tlogID: {access_event.logID}")
                print(f"\tdateTime: {access_event.dateTime}")
                print(f"\tcardCode: {access_event.cardCode}")'''

        # Check number of entries match within CSV and GuardPoint
        gp_access_event_count = gp.get_access_events_count()
        print(f"\nGP Events Count: {gp_access_event_count}")
        with open(CSV_FILENAME) as f:
            row_count = sum(1 for line in f)
        print(f"\nCSV Events Count: {row_count}\n\n")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")
