#!/usr/bin/env python3
"""
One-off diagnostic: what does the Alarm/Audit event log record for a
SUCCESSFUL vs a FAILED arm/disarm attempt?

Runs four cases against a live zone:
  1. Arm  - success  (explicit Arm/ArmConstantly)
  2. Arm  - failure  (ReturnAlarmZoneToWeeklyProgram with no WP defined)
  3. Disarm - success (explicit DisarmForDuration)
  4. Disarm - failure (DisarmUntilNextIntervalInWP with no WP defined)

For each, snapshots alarm/audit logs before and after and prints any new
entries, plus whether the call itself raised/returned an error.
"""

import os
import sys
import time

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, _root)

from pyGuardPoint_Build.pyGuardPoint import (
    GuardPoint, EventOrder, GuardPointError, GuardPointUnauthorized,
    AlarmZoneOption, AlarmZoneArmType, AlarmZoneDisarmType
)

TEST_HOST    = os.getenv('GP_HOST',    'https://sensoraccess.duckdns.org')
TEST_USER    = os.getenv('GP_USER',    'admin')
TEST_PASS    = os.getenv('GP_PASS',    'admin')
TEST_P12     = os.getenv('GP_P12',     os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MobileGuardDefault.p12'))
TEST_P12_PWD = os.getenv('GP_P12_PWD', 'test')

SNAPSHOT_SIZE = 10


def snapshot(gp):
    alarm = gp.get_alarm_events(limit=SNAPSHOT_SIZE, orderby=EventOrder.DATETIME_DESC)
    audit = gp.get_audit_events(limit=SNAPSHOT_SIZE, orderby=EventOrder.DATETIME_DESC)
    return alarm, audit, {e.uid for e in alarm}, {e.uid for e in audit}


def run_case(gp, label, action_fn):
    print(f"\n--- {label} ---")
    _, _, before_alarm_uids, before_audit_uids = snapshot(gp)

    call_result = None
    call_error = None
    try:
        call_result = action_fn()
        print(f"  call returned: {call_result}")
    except (GuardPointError, GuardPointUnauthorized) as e:
        call_error = str(e)
        print(f"  call raised: {call_error}")

    time.sleep(3)

    alarm_events, audit_events, _, _ = snapshot(gp)
    new_alarm = [e for e in alarm_events if e.uid not in before_alarm_uids]
    new_audit = [e for e in audit_events if e.uid not in before_audit_uids]

    if new_alarm:
        print(f"  Alarm Event Log: {len(new_alarm)} new entries")
        for e in new_alarm:
            print(f"    - {e.dict()}")
    else:
        print("  Alarm Event Log: no new entries")

    if new_audit:
        print(f"  Audit Event Log: {len(new_audit)} new entries")
        for e in new_audit:
            print(f"    - {e.dict()}")
    else:
        print("  Audit Event Log: no new entries")


def main():
    gp = GuardPoint(host=TEST_HOST, username=TEST_USER, pwd=TEST_PASS,
                     p12_file=TEST_P12, p12_pwd=TEST_P12_PWD, timeout=30)
    print(f"Connected to {TEST_HOST}")

    zone = gp.get_alarm_zone('cf16300c-53f3-4dc8-83ad-20db7030f139')  # zone2
    print(f"Using zone: {zone.name.strip()!r}  currently "
          f"{'ARMED' if zone.isRealTimeStatusArm else 'disarmed'}")

    run_case(gp, "1. ARM - success (explicit ArmConstantly)",
              lambda: gp.arm_alarm_zone(zone, option=AlarmZoneOption.Arm,
                                         arm_type=AlarmZoneArmType.ArmConstantly))

    run_case(gp, "2. ARM - failure (ReturnAlarmZoneToWeeklyProgram, no WP defined)",
              lambda: gp.arm_alarm_zone(zone, option=AlarmZoneOption.ReturnAlarmZoneToWeeklyProgram))

    run_case(gp, "3. DISARM - success (explicit DisarmForDuration)",
              lambda: gp.disarm_alarm_zone(zone, disarm_type=AlarmZoneDisarmType.DisarmForDuration,
                                            period=5, is_minute=True))

    run_case(gp, "4. DISARM - failure (DisarmUntilNextIntervalInWP, no WP defined)",
              lambda: gp.disarm_alarm_zone(zone, disarm_type=AlarmZoneDisarmType.DisarmUntilNextIntervalInWP))

    # Restore to armed, matching original state
    print("\nRestoring zone to ARMED (ArmConstantly)...")
    gp.arm_alarm_zone(zone, option=AlarmZoneOption.Arm, arm_type=AlarmZoneArmType.ArmConstantly)
    zone = gp.get_alarm_zone('cf16300c-53f3-4dc8-83ad-20db7030f139')
    print(f"Final state: {'ARMED' if zone.isRealTimeStatusArm else 'disarmed'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
