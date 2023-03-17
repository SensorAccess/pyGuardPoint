import logging, sys
import pkg_resources
#from pyGuardPoint import GuardPoint, GuardPointError
sys.path.insert(1, '../pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 50:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        cardholders = gp.get_card_holders(search_terms="John9700")
        for cardholder in cardholders:
            if gp.delete_card_holder(cardholder):
                print(f"Cardholder {cardholder.firstName} {cardholder.lastName} Deleted")

        cardholder = Cardholder(lastName="John9700")
        cardholder = gp.new_card_holder(cardholder)
        print(f"Cardholder {cardholder.firstName} {cardholder.lastName} Created")
        #cardholder.pretty_print()


        cardholder.firstName = "Frank100"
        if gp.update_card_holder(cardholder):
            print(f"Cardholder {cardholder.firstName} {cardholder.lastName} Updated")
            # cardholder.pretty_print()



    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")