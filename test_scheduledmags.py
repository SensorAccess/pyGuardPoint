import logging, sys
from datetime import datetime, timedelta

import pkg_resources
from strgen import StringGenerator # pip install StringGenerator

from pyGuardPoint_Build.pyGuardPoint.guardpoint_dataclasses import ScheduledMag

# Use PyPi Module
#from pyGuardPoint import GuardPoint, GuardPointError

# Force to use pyGuardPoint from pyGuardPoint_Build directory
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version

if __name__ == "__main__":
    print("pyGuardPoint Version:" + py_gp_version)
    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")

    try:
        sec_groups = gp.get_security_groups()
        #for sec_group in sec_groups:
        #    print(sec_group)

        # Get a cardholder
        cardholder = gp.get_card_holder(card_code='1B1A1B1C')

        '''
        fromDateValid = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:00Z')
        toDateValid = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:00Z')
        sm = ScheduledMag(scheduledSecurityGroupUID=sec_groups[0].uid,
                          cardholderUID=cardholder.uid,
                          fromDateValid=fromDateValid,
                          toDateValid=toDateValid)
        gp.add_scheduled_mag(sm)
        '''

        scheduled_mags = gp.get_scheduled_mags()
        for scheduled_mag in scheduled_mags:
            print(scheduled_mag)

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")