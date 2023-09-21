import logging, sys
from datetime import datetime, timedelta

import pkg_resources
# Use PyPi Module
#from pyGuardPoint import GuardPoint, GuardPointError

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version


def print_class_attributes(obj):
    if not hasattr(obj, '__dict__'):
        # obj is not user defined class
        return

    for attribute_name in obj.__dict__:
        attribute = getattr(obj, attribute_name)
        if hasattr(attribute, '__dict__'):
            print(f"{attribute_name}:")
            print_class_attributes(attribute)
        else:
            print(f"\t{attribute_name:<25}" + str(attribute))


if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="https://sensoraccess.duckdns.org", pwd="admin",
                    p12_file="C:\\Users\\john_\\OneDrive\\Desktop\\MobileGuardDefault.p12",
                    p12_pwd="test")

    #if last_pass_offset < 1 else (' and lastPassDate ge ' + date_filter(time_offset=last_pass_offset))} & "

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

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")