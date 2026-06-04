#!/usr/bin/env python3
"""
Integration test: SignalR real-time events + access event simulation.

Starts a SignalR WebSocket listener, fires a simulated access event through
every reader on the server, then verifies that AccessEventArrived messages
are received back in real time.

Usage:
    python tests/run_tests_signalr.py

Optional environment variables:
    GP_HOST     GuardPoint server URL  (default: https://sensoraccess.duckdns.org)
    GP_USER     Username               (default: admin)
    GP_PASS     Password               (default: admin)
    GP_P12      Path to P12 cert       (default: tests/MobileGuardDefault.p12)
    GP_P12_PWD  P12 password           (default: test)
    GP_CARD     Card code to simulate  (default: AABB1122)
"""

import sys
import os
import time
import threading

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, _root)

import asyncio

from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError

_default_p12 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MobileGuardDefault.p12')

TEST_HOST    = os.getenv('GP_HOST',    'https://sensoraccess.duckdns.org')
TEST_USER    = os.getenv('GP_USER',    'admin')
TEST_PASS    = os.getenv('GP_PASS',    'admin')
TEST_P12     = os.getenv('GP_P12',     _default_p12)
TEST_P12_PWD = os.getenv('GP_P12_PWD', 'test')
CARD_CODE    = os.getenv('GP_CARD',    'AABB1122')

NULL_UID         = '00000000-0000-0000-0000-000000000000'
CONNECT_TIMEOUT  = 15   # seconds to wait for the WebSocket handshake
EVENT_TIMEOUT    = 15   # seconds to wait for events after firing them

W = 46


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


def main():
    print_header("PyGuardPoint SignalR Integration Test")
    print(f"  Server : {TEST_HOST}")
    print(f"  P12    : {TEST_P12}")
    print(f"  Card   : {CARD_CODE}\n")

    passed = 0
    failed = 0

    # ------------------------------------------------------------------ #
    # 1. Connect
    # ------------------------------------------------------------------ #
    print_section("1. CONNECTION")
    try:
        gp = GuardPoint(
            host=TEST_HOST,
            username=TEST_USER,
            pwd=TEST_PASS,
            p12_file=TEST_P12,
            p12_pwd=TEST_P12_PWD,
            timeout=30,
        )
        ok("Connect to server", TEST_HOST)
        passed += 1
    except Exception as e:
        fail("Connect to server", str(e)[:70])
        return 1

    try:
        if not gp.is_sigr_enabled():
            fail("SignalR enabled", "server reports SignalR is disabled")
            return 1
        ok("SignalR enabled on server")
        passed += 1
    except Exception as e:
        fail("SignalR enabled", str(e)[:70])
        return 1

    # ------------------------------------------------------------------ #
    # 2. Discover readers
    # ------------------------------------------------------------------ #
    print_section("2. READERS")
    try:
        all_readers = gp.get_readers()
        valid_readers = [
            r for r in all_readers
            if r.controllerUID and r.controllerUID != NULL_UID
        ]
        ok("Get readers", f"{len(valid_readers)} with valid controller UIDs "
                          f"(of {len(all_readers)} total)")
        passed += 1
    except Exception as e:
        fail("Get readers", str(e)[:70])
        return 1

    if not valid_readers:
        fail("Readers available", "no readers with valid controller UIDs")
        return 1

    # ------------------------------------------------------------------ #
    # 3. Set up SignalR listener
    # ------------------------------------------------------------------ #
    print_section("3. SIGNALR LISTENER")

    connected        = threading.Event()
    received_events  = []
    received_lock    = threading.Lock()

    async def on_open():
        connected.set()

    async def on_close():
        pass

    async def on_error(message):
        pass

    async def on_access_event(message):
        with received_lock:
            received_events.append(message)

    async def on_other_event(message):
        pass

    # Run client.run() in its own event loop so we can cancel the task
    # cleanly via loop.call_soon_threadsafe — without relying on the
    # transport having a close() method.
    listener_loop = asyncio.new_event_loop()
    listener_task = [None]   # filled once the coroutine starts

    try:
        client = gp.get_signal_client()
        client.on_open(on_open)
        client.on_close(on_close)
        client.on_error(on_error)
        client.on('AccessEventArrived',   on_access_event)
        client.on('AlarmEventArrived',    on_other_event)
        client.on('AuditEventArrived',    on_other_event)
        client.on('CommEventArrived',     on_other_event)
        client.on('GeneralEventArrived',  on_other_event)
        client.on('IOEventArrived',       on_other_event)
        client.on('StatusUpdate',         on_other_event)
        client.on('TechnicalEventArrived',on_other_event)
        ok("SignalR client created")
        passed += 1
    except Exception as e:
        fail("SignalR client created", str(e)[:70])
        return 1

    def run_listener():
        asyncio.set_event_loop(listener_loop)

        async def _run():
            t = asyncio.ensure_future(client.run())
            listener_task[0] = t
            try:
                await t
            except asyncio.CancelledError:
                pass

        listener_loop.run_until_complete(_run())

    listener = threading.Thread(target=run_listener, daemon=True, name="signalr-listener")
    listener.start()

    print(f"  Waiting for WebSocket connection (up to {CONNECT_TIMEOUT}s)...")
    if connected.wait(timeout=CONNECT_TIMEOUT):
        ok("WebSocket connected")
        passed += 1
    else:
        fail("WebSocket connected", f"no connection within {CONNECT_TIMEOUT}s")
        failed += 1
        gp.stop_listening(client)
        return 1

    # ------------------------------------------------------------------ #
    # 4. Simulate access events on every valid reader
    # ------------------------------------------------------------------ #
    print_section("4. SIMULATING ACCESS EVENTS")

    fired = 0
    errors = 0
    for reader in valid_readers:
        try:
            if gp.simulate_access_event(
                controller_uid=reader.controllerUID,
                reader_num=reader.number,
                card_code=CARD_CODE,
            ):
                fired += 1
        except (GuardPointError, ValueError):
            errors += 1

    if fired > 0:
        detail = f"fired {fired}/{len(valid_readers)} readers"
        if errors:
            detail += f", {errors} skipped"
        ok("Simulate access events", detail)
        passed += 1
    else:
        fail("Simulate access events", "no events could be fired")
        failed += 1

    # ------------------------------------------------------------------ #
    # 5. Wait for AccessEventArrived messages
    # ------------------------------------------------------------------ #
    print_section("5. RECEIVING EVENTS")

    print(f"  Waiting up to {EVENT_TIMEOUT}s for AccessEventArrived messages...")
    deadline = time.time() + EVENT_TIMEOUT
    while time.time() < deadline:
        with received_lock:
            if len(received_events) >= fired:
                break
        time.sleep(0.2)

    with received_lock:
        final_count = len(received_events)

    if final_count > 0:
        ok("AccessEventArrived received", f"{final_count} event(s) "
                                          f"(fired {fired})")
        passed += 1
    else:
        fail("AccessEventArrived received",
             f"0 events within {EVENT_TIMEOUT}s (fired {fired})")
        failed += 1

    # ------------------------------------------------------------------ #
    # 6. Stop listener
    # ------------------------------------------------------------------ #
    print_section("6. CLEANUP")
    try:
        if listener_task[0] is not None:
            listener_loop.call_soon_threadsafe(listener_task[0].cancel)
        listener.join(timeout=5)
        # Cancel any residual tasks (e.g. websocket keepalive) so the loop
        # shuts down without "Task was destroyed but pending" warnings.
        remaining = asyncio.all_tasks(listener_loop)
        for t in remaining:
            t.cancel()
        if remaining:
            listener_loop.run_until_complete(
                asyncio.gather(*remaining, return_exceptions=True)
            )
        listener_loop.close()
        ok("Listener stopped cleanly")
        passed += 1
    except Exception as e:
        fail("Listener stopped cleanly", str(e)[:70])
        failed += 1

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    total = passed + failed
    print_header("Test Results")
    print(f"  PASSED  : {passed}/{total}")
    print(f"  FAILED  : {failed}/{total}")
    print(f"  SUCCESS : {100 * passed / total:.1f}%\n")

    if failed == 0:
        print("  ✓ All tests passed!")
        return 0
    else:
        print(f"  ✗ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
