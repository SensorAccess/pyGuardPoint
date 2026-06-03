#!/usr/bin/env python3
"""Simple test runner for pyGuardPoint using sync API only."""

import sys
import os

# Add build path
sys.path.insert(1, 'pyGuardPoint_Build')

from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, Cardholder, Card
import time

# Test server configuration
TEST_HOST = os.getenv('GP_HOST', 'https://sensoraccess.duckdns.org')
TEST_USER = os.getenv('GP_USER', 'admin')
TEST_PASS = os.getenv('GP_PASS', 'admin')

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_result(test_name, passed, message=""):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} | {test_name}")
    if message:
        print(f"       {message}")

def test_connection():
    """Test basic connection to GuardPoint server."""
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        gp = GuardPoint(
            host=TEST_HOST,
            username=TEST_USER,
            pwd=TEST_PASS,
            timeout=15
        )
        print_result("Connection", True, f"Connected to {TEST_HOST}")
        return gp
    except Exception as e:
        print_result("Connection", False, f"Error: {str(e)}")
        return None

def test_get_cardholders(gp):
    """Test retrieving cardholders."""
    try:
        result = gp.get_card_holders(limit=5)
        passed = result is not None and isinstance(result, list)
        count = len(result) if passed else 0
        print_result("Get Cardholders", passed, f"Retrieved {count} cardholders")
        return passed
    except Exception as e:
        print_result("Get Cardholders", False, str(e))
        return False

def test_get_areas(gp):
    """Test retrieving areas."""
    try:
        result = gp.get_areas()
        passed = result is not None and isinstance(result, list)
        count = len(result) if passed else 0
        print_result("Get Areas", passed, f"Retrieved {count} areas")
        return passed
    except Exception as e:
        print_result("Get Areas", False, str(e))
        return False

def test_create_delete_cardholder(gp):
    """Test creating and deleting a cardholder."""
    test_id = int(time.time()) % 100000
    try:
        # Create
        ch = Cardholder()
        ch.firstName = f"TestCH_{test_id}"
        ch.lastName = "pytest"
        ch.description = "Temporary test cardholder"

        uid = gp.new_card_holder(ch)
        if not uid:
            print_result("Create/Delete Cardholder", False, "Failed to create cardholder")
            return False

        # Verify
        created = gp.get_card_holder(uid=uid)
        if not created:
            print_result("Create/Delete Cardholder", False, "Created cardholder not found")
            return False

        # Delete
        deleted = gp.delete_card_holder(created)
        if not deleted:
            print_result("Create/Delete Cardholder", False, "Failed to delete cardholder")
            return False

        # Verify deletion
        check = gp.get_card_holder(uid=uid)
        passed = check is None
        print_result("Create/Delete Cardholder", passed, f"Created and deleted {ch.firstName}")
        return passed

    except Exception as e:
        print_result("Create/Delete Cardholder", False, str(e))
        return False

def test_get_readers(gp):
    """Test retrieving readers."""
    try:
        result = gp.get_readers(limit=5)
        passed = result is not None and isinstance(result, list)
        count = len(result) if passed else 0
        print_result("Get Readers", passed, f"Retrieved {count} readers")
        return passed
    except Exception as e:
        print_result("Get Readers", False, str(e))
        return False

def test_get_access_events(gp):
    """Test retrieving access events."""
    try:
        result = gp.get_access_events(limit=5)
        passed = result is not None and isinstance(result, list)
        count = len(result) if passed else 0
        print_result("Get Access Events", passed, f"Retrieved {count} events")
        return passed
    except Exception as e:
        print_result("Get Access Events", False, str(e))
        return False

def test_get_security_groups(gp):
    """Test retrieving security groups."""
    try:
        result = gp.get_security_groups()
        passed = result is not None and isinstance(result, list)
        count = len(result) if passed else 0
        print_result("Get Security Groups", passed, f"Retrieved {count} security groups")
        return passed
    except Exception as e:
        print_result("Get Security Groups", False, str(e))
        return False

def main():
    """Run all tests."""
    print_header("PyGuardPoint Integration Test Suite")
    print(f"Test Server: {TEST_HOST}")
    print(f"User: {TEST_USER}\n")

    results = {}

    # Connection test
    gp = test_connection()
    if not gp:
        print_header("Test Suite Failed - Cannot connect to server")
        return 1

    # Run tests
    print_header("API Endpoint Tests")
    results['cardholders'] = test_get_cardholders(gp)
    results['areas'] = test_get_areas(gp)
    results['readers'] = test_get_readers(gp)
    results['access_events'] = test_get_access_events(gp)
    results['security_groups'] = test_get_security_groups(gp)

    print_header("CRUD Operation Tests")
    results['create_delete'] = test_create_delete_cardholder(gp)

    # Summary
    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed\n")

    for test, result in results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {test}")

    print()

    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
