#!/usr/bin/env python3
"""
One-off diagnostic: does arming/disarming an AlarmZone show up in the
Alarm Event Log or Audit Event Log?

Snapshots the latest alarm/audit events, arms then disarms a zone, waits,
then re-fetches and diffs by uid to find anything new.
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

SNAPSHOT_SIZE = 20


def snapshot(gp):
    alarm = gp.get_alarm_events(limit=SNAPSHOT_SIZE, orderby=EventOrder.DATETIME_DESC)
    audit = gp.get_audit_events(limit=SNAPSHOT_SIZE, orderby=EventOrder.DATETIME_DESC)
    return {e.uid for e in alarm}, {e.uid for e in audit}


def print_new(label, events, before_uids):
    new = [e for e in events if e.uid not in before_uids]
    if not new:
        print(f"  {label}: no new entries")
        return
    print(f"  {label}: {len(new)} new entries")
    for e in new:
        print(f"    - {e.dict()}")


def main():
    gp = GuardPoint(host=TEST_HOST, username=TEST_USER, pwd=TEST_PASS,
                     p12_file=TEST_P12, p12_pwd=TEST_P12_PWD, timeout=30)
    print(f"Connected to {TEST_HOST}")

    zones = gp.get_alarm_zones()
    if not zones:
        print("No alarm zones found.")
        return 1

    zone = zones[0]
    print(f"Using zone: {zone.name.strip()!r} (uid={zone.uid})  currently "
          f"{'ARMED' if zone.isRealTimeStatusArm else 'disarmed'}")

    print("\nTaking BEFORE snapshot of alarm/audit logs...")
    before_alarm_uids, before_audit_uids = snapshot(gp)

    print("Arming zone...")
    result = gp.arm_alarm_zone(zone, option=AlarmZoneOption.Arm,
                                arm_type=AlarmZoneArmType.ArmForDuration,
                                period=5, is_minute=True)
    print(f"  arm_alarm_zone() -> {result}")
    time.sleep(3)

    print("Disarming zone...")
    result = gp.disarm_alarm_zone(zone, disarm_type=AlarmZoneDisarmType.DisarmForDuration,
                                   period=5, is_minute=True)
    print(f"  disarm_alarm_zone() -> {result}")
    time.sleep(3)

    print("\nTaking AFTER snapshot of alarm/audit logs...")
    alarm_events = gp.get_alarm_events(limit=SNAPSHOT_SIZE, orderby=EventOrder.DATETIME_DESC)
    audit_events = gp.get_audit_events(limit=SNAPSHOT_SIZE, orderby=EventOrder.DATETIME_DESC)

    print("\n=== RESULTS ===")
    print_new("Alarm Event Log", alarm_events, before_alarm_uids)
    print_new("Audit Event Log", audit_events, before_audit_uids)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (GuardPointError, GuardPointUnauthorized) as e:
        print(f"GuardPoint error: {e}")
        sys.exit(1)
