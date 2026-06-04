#!/usr/bin/env python3
"""
Integration test runner for pyGuardPoint (async API).

Usage:
    python tests/run_tests_async.py

Required environment variable:
    GP_P12      Path to the client certificate PKCS#12 file

Optional environment variables:
    GP_HOST     GuardPoint server URL  (default: https://sensoraccess.duckdns.org)
    GP_USER     Username               (default: admin)
    GP_PASS     Password               (default: admin)
    GP_P12_PWD  Password for the P12   (default: empty string)
"""

import asyncio
import sys
import os
import time

# Resolve project root so this script works from any working directory
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, _root)

from pyGuardPoint_Build.pyGuardPoint import (
    GuardPointAsyncIO, Cardholder, EventOrder, GuardPointError, GuardPointUnauthorized
)

_default_p12 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MobileGuardDefault.p12')

TEST_HOST    = os.getenv('GP_HOST',    'https://sensoraccess.duckdns.org')
TEST_USER    = os.getenv('GP_USER',    'admin')
TEST_PASS    = os.getenv('GP_PASS',    'admin')
TEST_P12     = os.getenv('GP_P12',     _default_p12)
TEST_P12_PWD = os.getenv('GP_P12_PWD', 'test')

W = 46  # label column width


def print_header(text):
    print(f"\n{'='*75}")
    print(f"  {text}")
    print(f"{'='*75}\n")


def print_section(text):
    print(f"\n{text}")


def ok(label, detail=""):
    print(f"  ✓ {label:<{W}}{' | ' + detail if detail else ''}")


def fail(label, detail=""):
    print(f"  ✗ {label:<{W}}{' | ' + detail if detail else ''}")


def skip(label, reason=""):
    print(f"  - {label:<{W}}skipped{(' — ' + reason) if reason else ''}")


class Results:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    async def run(self, label, coro):
        try:
            return await coro
        except (GuardPointError, GuardPointUnauthorized, Exception) as e:
            fail(label, str(e)[:70])
            self.failed += 1
            return None

    def check(self, label, value, detail=""):
        if value:
            ok(label, detail)
            self.passed += 1
        else:
            fail(label, detail or "assertion failed")
            self.failed += 1
        return value


async def main():
    print_header("PyGuardPoint Async Integration Test Suite")
    print(f"  Server : {TEST_HOST}")
    print(f"  User   : {TEST_USER}")
    print(f"  P12    : {TEST_P12 or '(not set — GP_P12 env var required for mTLS)'}")

    r = Results()

    # ------------------------------------------------------------------ #
    # 1. CONNECTION
    # ------------------------------------------------------------------ #
    print_section("1. AUTHENTICATION & CONNECTION")
    try:
        gp = GuardPointAsyncIO(
            host=TEST_HOST,
            username=TEST_USER,
            pwd=TEST_PASS,
            p12_file=TEST_P12,
            p12_pwd=TEST_P12_PWD,
            timeout=30,
        )
        ok("Connect to server", TEST_HOST)
        r.passed += 1
    except Exception as e:
        fail("Connect to server", str(e)[:70])
        r.failed += 1
        print_header("Cannot connect — aborting")
        return 1

    try:
        # ------------------------------------------------------------------ #
        # 2. CARDHOLDERS
        # ------------------------------------------------------------------ #
        print_section("2. CARDHOLDERS")

        cardholders = await r.run("Get cardholders (limit 5)",
                                  gp.get_card_holders(limit=5))
        r.check("Get cardholders (limit 5)", cardholders is not None,
                f"{len(cardholders)} returned" if cardholders else "none")

        count = await r.run("Get cardholder count", gp.get_cardholder_count())
        r.check("Get cardholder count", count is not None and count >= 0,
                f"total={count}")

        first = cardholders[0] if cardholders else None
        if first:
            ch = await r.run("Get cardholder by UID",
                             gp.get_card_holder(uid=first.uid))
            r.check("Get cardholder by UID", ch is not None,
                    f"{ch.firstName} {ch.lastName}" if ch else "")
        else:
            skip("Get cardholder by UID", "no cardholders")

        results = await r.run("Search cardholders",
                              gp.get_card_holders(search_terms="test", limit=5))
        r.check("Search cardholders", results is not None,
                f"{len(results)} matches" if results else "none")

        types = await r.run("Get cardholder types", gp.get_cardholder_types())
        r.check("Get cardholder types", types is not None,
                f"{len(types)} types" if types else "none")

        # ------------------------------------------------------------------ #
        # 3. CARDHOLDER CRUD
        # ------------------------------------------------------------------ #
        print_section("3. CARDHOLDER CRUD")

        test_id = int(time.time()) % 1000000
        ch_new = Cardholder()
        ch_new.firstName   = f"AsyncTest_{test_id}"
        ch_new.lastName    = "auto"
        ch_new.pinCode     = "9999"
        ch_new.description = "Created by run_tests_async.py"

        created = await r.run("Create cardholder", gp.new_card_holder(ch_new))
        if r.check("Create cardholder", created and created.uid,
                   f"UID {created.uid[:8]}..." if created and created.uid else ""):

            created.description = "Updated by run_tests_async.py"
            created.pinCode = "1234"
            updated = await r.run("Update cardholder", gp.update_card_holder(created))
            if r.check("Update cardholder", updated is not None):
                verified = await r.run("Verify update",
                                       gp.get_card_holder(uid=created.uid))
                r.check("Verify update",
                        verified and verified.description == "Updated by run_tests_async.py",
                        verified.description if verified else "")

            deleted = await r.run("Delete cardholder", gp.delete_card_holder(created))
            r.check("Delete cardholder", deleted, f"deleted {ch_new.firstName}")

        # ------------------------------------------------------------------ #
        # 4. CARDS
        # ------------------------------------------------------------------ #
        print_section("4. CARDS")

        cards = await r.run("Get cards (limit 5)", gp.get_cards(limit=5))
        r.check("Get cards (limit 5)", cards is not None,
                f"{len(cards)} returned" if cards else "none")

        card_count = await r.run("Get card count", gp.get_cards(count=True))
        r.check("Get card count", card_count is not None and card_count >= 0,
                f"total={card_count}")

        # ------------------------------------------------------------------ #
        # 5. ACCESS CONTROL
        # ------------------------------------------------------------------ #
        print_section("5. ACCESS CONTROL")

        sec_groups = await r.run("Get security groups", gp.get_security_groups())
        r.check("Get security groups", sec_groups is not None,
                f"{len(sec_groups)} groups" if sec_groups else "none")

        acc_groups = await r.run("Get access groups", gp.get_access_groups())
        r.check("Get access groups", acc_groups is not None,
                f"{len(acc_groups)} groups" if acc_groups else "none")

        sched_mags = await r.run("Get scheduled mags", gp.get_scheduled_mags())
        r.check("Get scheduled mags", sched_mags is not None,
                f"{len(sched_mags)} entries" if sched_mags else "none")

        # ------------------------------------------------------------------ #
        # 6. AREAS, SITES & DEPARTMENTS
        # ------------------------------------------------------------------ #
        print_section("6. AREAS, SITES & DEPARTMENTS")

        areas = await r.run("Get areas", gp.get_areas())
        r.check("Get areas", areas is not None,
                f"{len(areas)} areas" if areas else "none")

        sites = await r.run("Get sites", gp.get_sites())
        r.check("Get sites", sites is not None,
                f"{len(sites)} sites" if sites else "none")

        if sites:
            site = await r.run("Get site by UID",
                               gp.get_site(site_uid=sites[0].uid))
            r.check("Get site by UID", site is not None, site.name if site else "")
        else:
            skip("Get site by UID", "no sites")

        depts = await r.run("Get departments", gp.get_departments())
        r.check("Get departments", depts is not None,
                f"{len(depts)} departments" if depts else "none")

        # ------------------------------------------------------------------ #
        # 7. ALARMS & ZONES
        # ------------------------------------------------------------------ #
        print_section("7. ALARMS & ZONES")

        alarm_states = await r.run("Get alarm states", gp.get_alarm_states())
        r.check("Get alarm states", alarm_states is not None,
                f"{len(alarm_states)} states" if alarm_states else "none")

        alarm_zones = await r.run("Get alarm zones", gp.get_alarm_zones())
        r.check("Get alarm zones", alarm_zones is not None,
                f"{len(alarm_zones)} zones" if alarm_zones else "none")

        if alarm_zones:
            fetched = await r.run("Get alarm zone by UID",
                                  gp.get_alarm_zone(alarm_zones[0].uid))
            r.check("Get alarm zone by UID", fetched is not None,
                    fetched.name if fetched else "")
        else:
            skip("Get alarm zone by UID", "no alarm zones")

        # ------------------------------------------------------------------ #
        # 8. HARDWARE
        # ------------------------------------------------------------------ #
        print_section("8. HARDWARE")

        readers = await r.run("Get readers", gp.get_readers())
        r.check("Get readers", readers is not None,
                f"{len(readers)} readers" if readers else "none")

        controllers = await r.run("Get controllers", gp.get_controllers())
        r.check("Get controllers", controllers is not None,
                f"{len(controllers)} controllers" if controllers else "none")

        relays = await r.run("Get relays", gp.get_relays())
        r.check("Get relays", relays is not None,
                f"{len(relays)} relays" if relays else "none")

        # ------------------------------------------------------------------ #
        # 9. EVENTS
        # ------------------------------------------------------------------ #
        print_section("9. EVENTS")

        ev_count = await r.run("Get access event count",
                               gp.get_access_events_count())
        r.check("Get access event count", ev_count is not None and ev_count >= 0,
                f"total={ev_count}")

        events = await r.run("Get access events (limit 5)",
                             gp.get_access_events(limit=5))
        r.check("Get access events (limit 5)", events is not None,
                f"{len(events)} events" if events else "none")

        events_desc = await r.run("Get events ordered DESC",
                                  gp.get_access_events(limit=5,
                                                       orderby=EventOrder.DATETIME_DESC))
        r.check("Get events ordered DESC", events_desc is not None,
                f"{len(events_desc)} events" if events_desc else "none")

        alarm_ev_count = await r.run("Get alarm event count",
                                     gp.get_alarm_events_count())
        r.check("Get alarm event count",
                alarm_ev_count is not None and alarm_ev_count >= 0,
                f"total={alarm_ev_count}")

        audit_ev_count = await r.run("Get audit event count",
                                     gp.get_audit_events_count())
        r.check("Get audit event count",
                audit_ev_count is not None and audit_ev_count >= 0,
                f"total={audit_ev_count}")

        # ------------------------------------------------------------------ #
        # 10. SCHEDULING
        # ------------------------------------------------------------------ #
        print_section("10. SCHEDULING")

        weekly_programs = await r.run("Get weekly programs",
                                      gp.get_weekly_programs())
        r.check("Get weekly programs", weekly_programs is not None,
                f"{len(weekly_programs)} programs" if weekly_programs else "none")

        if weekly_programs:
            wp = await r.run("Get weekly program by UID",
                             gp.get_weekly_program(weekly_programs[0].uid))
            r.check("Get weekly program by UID", wp is not None, wp.name if wp else "")
        else:
            skip("Get weekly program by UID", "no weekly programs")

        # ------------------------------------------------------------------ #
        # 11. SYSTEM INFO
        # ------------------------------------------------------------------ #
        print_section("11. SYSTEM INFO")

        infos = await r.run("Get system infos", gp.get_infos())
        r.check("Get system infos", infos is not None,
                f"{len(infos)} entries" if infos else "none")

        sigr = await r.run("Check SignalR enabled", gp.is_sigr_enabled())
        r.check("Check SignalR enabled", sigr is not None, f"enabled={sigr}")

        manual_events = await r.run("Get manual events", gp.get_manual_events())
        r.check("Get manual events", manual_events is not None,
                f"{len(manual_events)} events" if manual_events else "none")

    finally:
        await gp.close()

    # ------------------------------------------------------------------ #
    # SUMMARY
    # ------------------------------------------------------------------ #
    total = r.passed + r.failed
    print_header("Test Results")
    print(f"  PASSED  : {r.passed}/{total}")
    print(f"  FAILED  : {r.failed}/{total}")
    print(f"  SUCCESS : {100 * r.passed / total:.1f}%\n")

    if r.failed == 0:
        print("  ✓ All tests passed!")
        return 0
    else:
        print(f"  ✗ {r.failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
