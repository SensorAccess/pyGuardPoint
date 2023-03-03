import logging, sys
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
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        areas = gp.get_areas()
        for area in areas:
            print(f"\t{area.name:<35}" + area.uid);

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")