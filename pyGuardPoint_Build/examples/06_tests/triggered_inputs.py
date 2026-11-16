"""
List currently-triggered inputs on a GuardPoint10 server.

Usage:
    python triggered_inputs.py

Env overrides (defaults target the bundled test server):
    GP_HOST, GP_USER, GP_PASS, GP_P12, GP_P12_PWD
"""
import os

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
        inputs = gp.get_inputs()
        triggered = [i for i in inputs if i.isUnderAlarm]

        print(f"{len(inputs)} inputs total, {len(triggered)} currently triggered\n")
        for i in triggered:
            print(f"  {i.name.strip():<30} state={i.inputPhysicalState:<10} "
                  f"bypassed={i.isBypassed}  armed={i.isArm}  uid={i.uid}")

        if not triggered:
            print("  (none)")

    except GuardPointUnauthorized as e:
        print(f"GuardPointUnauthorized: {e}")
    except GuardPointError as e:
        print(f"GuardPointError: {e}")
