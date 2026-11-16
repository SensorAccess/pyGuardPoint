"""
List which AlarmZone each Input belongs to.

Input.inputGroupUID is, despite its name, the parent AlarmZone's uid.
There is no OData $expand between API_Inputs and API_AlarmZones, so the
join has to be done client-side.

Usage:
    python inputs_by_alarmzone.py

Env overrides (defaults target the bundled test server):
    GP_HOST, GP_USER, GP_PASS, GP_P12, GP_P12_PWD
"""
import os
from collections import defaultdict

from pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized

_default_p12 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tests', 'MobileGuardDefault.p12')

GP_HOST = os.getenv('GP_HOST', 'https://sensoraccess2.duckdns.org')
GP_USER = os.getenv('GP_USER', 'admin')
GP_PASS = os.getenv('GP_PASS', 'admin')
GP_P12 = os.getenv('GP_P12', _default_p12)
GP_P12_PWD = os.getenv('GP_P12_PWD', 'test')

if __name__ == "__main__":
    gp = GuardPoint(host=GP_HOST,
                     username=GP_USER,
                     pwd=GP_PASS,
                     p12_file=GP_P12,
                     p12_pwd=GP_P12_PWD)
    try:
        zones = {z.uid: z.name.strip() for z in gp.get_alarm_zones()}
        inputs = gp.get_inputs()

        by_zone = defaultdict(list)
        unassigned = []
        for i in inputs:
            if i.inputGroupUID:
                by_zone[i.inputGroupUID].append(i)
            else:
                unassigned.append(i)

        for zone_uid, zone_inputs in by_zone.items():
            zone_name = zones.get(zone_uid, f"(unknown zone {zone_uid})")
            print(f"\n{zone_name}")
            for i in zone_inputs:
                print(f"  {i.name.strip():<30} triggered={i.isUnderAlarm}")

        if unassigned:
            print(f"\nNot assigned to any AlarmZone ({len(unassigned)}):")
            for i in unassigned:
                print(f"  {i.name.strip()}")

    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except GuardPointError as e:
        print(f"GuardPointError: {e}")
