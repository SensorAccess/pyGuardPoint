"""
Interactive CLI to arm/disarm an AlarmZone on a GuardPoint10 server.

Usage:
    python alarm_zone_control.py

Env overrides (defaults target the bundled test server):
    GP_HOST, GP_USER, GP_PASS, GP_P12, GP_P12_PWD
"""
import os
import sys
from importlib.metadata import version, PackageNotFoundError

REQUIRED_VERSION = (2, 5, 1)


def check_version():
    """Warn if the installed pyGuardPoint is older than REQUIRED_VERSION.

    The arm/disarm mode parameters (armBypassMode, disarm_type, ...) were added
    in 2.4.9, and arm_alarm_zone()'s triggered-inputs result in 2.5.1. Must run
    before importing them, since older installs don't have those names to
    import at all.
    """
    try:
        installed = version("pyGuardPoint")
    except PackageNotFoundError:
        print("Warning: could not determine installed pyGuardPoint version.")
        return

    installed_tuple = tuple(int(p) for p in installed.split('.')[:3] if p.isdigit())
    if installed_tuple < REQUIRED_VERSION:
        required_str = '.'.join(str(p) for p in REQUIRED_VERSION)
        print(f"Warning: pyGuardPoint {installed} is installed, but this script requires "
              f"{required_str} or above (arm/disarm mode + triggered-inputs support). "
              f"Run 'pip install pyGuardPoint --upgrade'.")
        sys.exit(1)


check_version()

from pyGuardPoint import (GuardPoint, GuardPointError, GuardPointUnauthorized,
                           AlarmZoneOption, AlarmZoneArmType, ArmBypassMode, AlarmZoneDisarmType)

_default_p12 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tests', 'MobileGuardDefault.p12')

GP_HOST = os.getenv('GP_HOST', 'https://sensoraccess2.duckdns.org')
GP_USER = os.getenv('GP_USER', 'admin')
GP_PASS = os.getenv('GP_PASS', 'admin')
GP_P12 = os.getenv('GP_P12', _default_p12)
GP_P12_PWD = os.getenv('GP_P12_PWD', 'test')


def choose_from_menu(prompt, options):
    """options: list of (label, value). Returns the chosen value, or None if cancelled."""
    while True:
        print(f"\n{prompt}")
        for i, (label, _) in enumerate(options, start=1):
            print(f"  {i}) {label}")
        print(f"  0) Cancel")
        choice = input("Choice: ").strip()
        if choice == '0':
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1][1]
        print("Invalid choice, try again.")


def choose_period():
    while True:
        raw = input("Duration value (e.g. 5): ").strip()
        if raw.isdigit():
            period = int(raw)
            break
        print("Please enter a whole number.")
    unit = choose_from_menu("Duration unit:", [("Minutes", True), ("Seconds", False)])
    return period, unit


def zone_status(zone):
    return "ARMED" if zone.isRealTimeStatusArm else "disarmed"


def list_zones(gp):
    zones = gp.get_alarm_zones()
    print("\nAlarm Zones:")
    for i, z in enumerate(zones, start=1):
        print(f"  {i}) {z.name.strip():<30} [{zone_status(z)}]  (WP-armed: {z.iswpStatusArm})")
    return zones


def do_arm(gp, zone):
    arm_type = choose_from_menu("Arm type:", [
        ("Arm Constantly", AlarmZoneArmType.ArmConstantly),
        ("Arm For Duration", AlarmZoneArmType.ArmForDuration),
        ("Arm Until Next Interval In Weekly Program", AlarmZoneArmType.ArmUntilNextIntervalInWP),
    ])
    if arm_type is None:
        return

    period, is_minute = (0, True)
    if arm_type == AlarmZoneArmType.ArmForDuration:
        period, is_minute = choose_period()

    bypass_mode = choose_from_menu("Bypass mode (how to handle currently-triggered inputs):", [
        ("Arm anyway", ArmBypassMode.Arm),
        ("Bypass the triggered inputs and arm", ArmBypassMode.Bypass),
        ("Cancel arming if any input is triggered", ArmBypassMode.Cancel),
    ])
    if bypass_mode is None:
        return

    result = gp.arm_alarm_zone(zone, option=AlarmZoneOption.Arm,
                                arm_type=arm_type, period=period, is_minute=is_minute,
                                bypass_mode=bypass_mode)
    print(f"\nArm {'succeeded' if result else 'FAILED'}")
    if result.triggered_inputs:
        verb = "bypassed" if bypass_mode == ArmBypassMode.Bypass else "blocking"
        print(f"{len(result.triggered_inputs)} input(s) in alarm ({verb}):")
        for i in result.triggered_inputs:
            print(f"  - {i.name.strip()}  uid={i.uid}")
    for msg in result.error_messages:
        print(f"  error: {msg}")


def do_disarm(gp, zone):
    disarm_type = choose_from_menu("Disarm type:", [
        ("Disarm Constantly", AlarmZoneDisarmType.DisarmConstantly),
        ("Disarm For Duration", AlarmZoneDisarmType.DisarmForDuration),
        ("Disarm Until Next Interval In Weekly Program", AlarmZoneDisarmType.DisarmUntilNextIntervalInWP),
    ])
    if disarm_type is None:
        return

    period, is_minute = (1, True)
    if disarm_type == AlarmZoneDisarmType.DisarmForDuration:
        period, is_minute = choose_period()

    result = gp.disarm_alarm_zone(zone, disarm_type=disarm_type, period=period, is_minute=is_minute)
    print(f"\nDisarm command sent: {result}")


def main():
    gp = GuardPoint(host=GP_HOST, username=GP_USER, pwd=GP_PASS, p12_file=GP_P12, p12_pwd=GP_P12_PWD)

    while True:
        zones = list_zones(gp)
        if not zones:
            print("No alarm zones found.")
            return

        choice = input("\nSelect zone number (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return
        if not (choice.isdigit() and 1 <= int(choice) <= len(zones)):
            print("Invalid selection.")
            continue
        zone = zones[int(choice) - 1]

        action = choose_from_menu(f"Selected '{zone.name.strip()}' [{zone_status(zone)}]. Action:", [
            ("Arm", 'arm'),
            ("Disarm", 'disarm'),
        ])
        if action == 'arm':
            do_arm(gp, zone)
        elif action == 'disarm':
            do_disarm(gp, zone)

        again = input("\nPerform another action? (y/N): ").strip().lower()
        if again != 'y':
            return


if __name__ == "__main__":
    try:
        main()
    except (GuardPointError, GuardPointUnauthorized) as e:
        print(f"GuardPoint error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
