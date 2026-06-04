import logging, sys
from datetime import datetime, timedelta

import pkg_resources

# Use PyPi Module
from pyGuardPoint import GuardPoint, GuardPointError


py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 52:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    # if last_pass_offset < 1 else (' and lastPassDate ge ' + date_filter(time_offset=last_pass_offset))} & "

    offsite_area_names = ['Not located', 'Offsite']
    try:
        areas = gp.get_areas()
        offsite_areas = []
        onsite_areas = []
        for area in areas:
            if area.name in offsite_area_names:
                offsite_areas.append(area)
            else:
                onsite_areas.append(area)

        print("Offsite Areas:")
        for area in offsite_areas:
            print(f"\t{area.name:<20}{area.uid}")

        print("Onsite Areas:")
        for area in onsite_areas:
            print(f"\t{area.name:<20}{area.uid}")

        last_pass = datetime.now() - timedelta(weeks=900)
        num_onsite_active_users = gp.get_card_holders(earliest_last_pass=last_pass, areas=onsite_areas, count=True)
        print(f"Active Onsite Cardholders: {num_onsite_active_users}")

        num_offsite_active_users = gp.get_card_holders(earliest_last_pass=last_pass, areas=offsite_areas, count=True)
        print(f"Active Offsite Cardholders: {num_offsite_active_users}")

        offsite_cardholders = gp.get_card_holders(earliest_last_pass=last_pass, areas=offsite_areas)
        for cardholder in offsite_cardholders:
            print(f"Cardholder: {cardholder.lastName} was last active at {cardholder.lastPassDate}")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")