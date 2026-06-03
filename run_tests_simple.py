#!/usr/bin/env python3
"""Simple test runner for pyGuardPoint - testing core functionality."""

import sys
import os
import ssl
import urllib3

sys.path.insert(1, 'pyGuardPoint_Build')

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, Cardholder
import time

TEST_HOST = os.getenv('GP_HOST', 'https://sensoraccess.duckdns.org')
TEST_USER = os.getenv('GP_USER', 'admin')
TEST_PASS = os.getenv('GP_PASS', 'admin')

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_result(test_name, passed, message=""):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status:<8} | {test_name:<30} | {message}")

def main():
    print_header("PyGuardPoint Sync API Tests")
    print(f"Server: {TEST_HOST}\n")

    results = {}

    # Test 1: Connection
    print("Testing connection...")
    try:
        gp = GuardPoint(
            host=TEST_HOST,
            username=TEST_USER,
            pwd=TEST_PASS,
            timeout=20
        )
        results['01_connection'] = True
        print_result("Connection", True, f"Connected to {TEST_HOST}")
    except Exception as e:
        results['01_connection'] = False
        print_result("Connection", False, str(e)[:50])
        print_header("Test Suite Failed")
        return 1

    # Test 2: Get Cardholders
    print("\nTesting API operations...")
    try:
        cardholders = gp.get_card_holders(limit=3)
        if cardholders and isinstance(cardholders, list):
            results['02_get_cardholders'] = True
            print_result("Get Cardholders", True, f"Retrieved {len(cardholders)} cardholders")
        else:
            results['02_get_cardholders'] = False
            print_result("Get Cardholders", False, "No cardholders returned")
    except Exception as e:
        results['02_get_cardholders'] = False
        print_result("Get Cardholders", False, str(e)[:50])

    # Test 3: Get first cardholder details
    try:
        cardholders = gp.get_card_holders(limit=1)
        if cardholders and len(cardholders) > 0:
            ch = cardholders[0]
            retrieved = gp.get_card_holder(uid=ch.uid)
            if retrieved:
                results['03_get_by_uid'] = True
                print_result("Get by UID", True, f"Retrieved {retrieved.firstName} {retrieved.lastName}")
            else:
                results['03_get_by_uid'] = False
                print_result("Get by UID", False, "Failed to retrieve cardholder")
        else:
            results['03_get_by_uid'] = None
            print_result("Get by UID", None, "Skipped (no cardholders in system)")
    except Exception as e:
        results['03_get_by_uid'] = False
        print_result("Get by UID", False, str(e)[:50])

    # Test 4: Create cardholder
    print("\nTesting CRUD operations...")
    test_id = int(time.time()) % 100000
    try:
        ch = Cardholder()
        ch.firstName = f"Test_{test_id}"
        ch.lastName = "Pytest"
        ch.pinCode = "1234"
        ch.description = "Temporary - will be deleted"

        uid = gp.new_card_holder(ch)
        if uid:
            results['04_create'] = True
            print_result("Create Cardholder", True, f"Created UID: {uid[:8]}...")
            
            # Test 5: Update cardholder
            try:
                created = gp.get_card_holder(uid=uid)
                created.description = "Updated by test"
                updated = gp.update_card_holder(created)
                if updated:
                    results['05_update'] = True
                    print_result("Update Cardholder", True, "Updated description")
                else:
                    results['05_update'] = False
                    print_result("Update Cardholder", False, "Update returned False")
            except Exception as e:
                results['05_update'] = False
                print_result("Update Cardholder", False, str(e)[:50])

            # Test 6: Delete cardholder
            try:
                deleted = gp.delete_card_holder(created)
                if deleted:
                    # Verify deletion
                    check = gp.get_card_holder(uid=uid)
                    if check is None:
                        results['06_delete'] = True
                        print_result("Delete Cardholder", True, "Successfully deleted")
                    else:
                        results['06_delete'] = False
                        print_result("Delete Cardholder", False, "Cardholder still exists")
                else:
                    results['06_delete'] = False
                    print_result("Delete Cardholder", False, "Delete returned False")
            except Exception as e:
                results['06_delete'] = False
                print_result("Delete Cardholder", False, str(e)[:50])
        else:
            results['04_create'] = False
            print_result("Create Cardholder", False, "No UID returned")
    except Exception as e:
        results['04_create'] = False
        print_result("Create Cardholder", False, str(e)[:50])

    # Summary
    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)

    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed}/{total}")
    if skipped:
        print(f"Skipped: {skipped}/{total}")
    print()

    for test, result in sorted(results.items()):
        if result is True:
            print(f"  ✓ {test.split('_', 1)[1]}")
        elif result is False:
            print(f"  ✗ {test.split('_', 1)[1]}")
        else:
            print(f"  - {test.split('_', 1)[1]} (skipped)")

    print()
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
