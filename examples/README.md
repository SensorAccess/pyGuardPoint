# pyGuardPoint Examples

This directory contains organized examples and tests for the pyGuardPoint SDK, demonstrating how to interact with the Sensor Access GuardPoint (GP10) access control system.

## Directory Structure

### 01_basics/
**Basic introduction and setup examples**

- `examples.py` - General overview of pyGuardPoint usage
- `tutorial.py` - Step-by-step tutorial for getting started
- `token_login.py` - Token-based authentication example
- `simple_print_areas.py` - List all access areas
- `simple_print_cardholder.py` - Retrieve and display cardholder info

**Getting Started:** Start with `tutorial.py` or `examples.py` to understand basic usage.

### 02_cardholders/
**Cardholder management operations**

- `new_cardholder.py` - Create a new cardholder
- `new_cardholder_ag_uids.py` - Create cardholder with access group UIDs
- `get_all_cardholders.py` - Retrieve all cardholders with pagination
- `get_cardholder_by_uid.py` - Fetch by unique ID
- `get_cardholder_by_number.py` - Fetch by employee number
- `get_cardholders_by_name.py` - Search by name
- `get_cardholders_by_email.py` - Search by email address
- `get_cardholders_by_cardcode.py` - Search by card code
- `get_cardholders_by_site.py` - Filter by site
- `get_cardholder_types.py` - List cardholder types
- `get_photo_blitz.py` - Retrieve cardholder photos
- `update_isToActive.py` - Update active status
- `update_custom_field.py` - Modify custom fields
- `filter_cardholders.py` - Advanced filtering/searching
- `test_customizedFields.py` - Working with custom fields
- `test_enroll_photo.py` - Photo enrollment

### 03_async/
**Asynchronous (asyncio) examples using GuardPointAsyncIO**

- `asyncio_test.py` - Basic async usage
- `asyncio_cardholder_valid.py` - Async cardholder operations
- `asyncio_events.py` - Real-time event listening (async)
- `asyncio_alarmstates.py` - Alarm state monitoring (async)
- `asyncio_weekly_programs.py` - Weekly schedule management (async)
- `test_getinfo_async.py` - System info retrieval (async)
- `test_events_async.py` - Event processing (async)
- `test_securitygroups_asyncio.py` - Security groups (async)
- `test_sigR_async.py` - SignalR WebSocket integration (async)

**Note:** These use `GuardPointAsyncIO` for non-blocking I/O. Best for high-concurrency applications.

### 04_utilities/
**Utility and import/export scripts**

- `import.py` - Bulk import cardholders/data
- `export.py` - Bulk export cardholders/data
- `get_cards.py` - List all cards
- `get_readers.py` - List all readers/readers
- `get_access_events_csv.py` - Export access events to CSV
- `update_areas.py` - Bulk update areas
- `multithread_it.py` - Multi-threaded operations example

### 05_integration/
**External system integrations and real-time features**

- `test_sigR.py` - SignalR WebSocket connection (sync)
- `test_sigR_async.py` - SignalR WebSocket connection (async)
- `sigR_connection_blitz.py` - High-performance SignalR event processing
- `sigR_whatsApp.py` - WhatsApp integration example
- `test_simAccessEv.py` - Simulated access event testing

### 06_tests/
**Unit and integration tests**

**Area & Security:**
- `test_alarmzones.py` - Alarm zone operations
- `test_alarmzones_arm_fields.py` - Alarm arming fields
- `test_alarmstates.py` - Real-time alarm state monitoring
- `test_securitygroups.py` - Security group management

**Access Control:**
- `test_accessgroups.py` - Access group operations
- `test_events.py` - Event retrieval and filtering
- `test_events_async.py` - Async event operations

**Facility Management:**
- `test_sites.py` - Site management
- `test_departments.py` - Department operations
- `test_weeklyprograms.py` - Weekly schedule programs
- `test_scheduledmags.py` - Scheduled access (mags)

**Infrastructure:**
- `test_inputs.py` - Input device testing
- `test_outputs.py` - Output/relay testing
- `test_getinfo.py` - System information

**Miscellaneous:**
- `test_counts.py` - Counting operations
- `test_manual_events.py` - Manual event generation
- `test_customizedFields.py` - Custom field operations

### _deNovo/
**Experimental and deprecated examples**

- `examples_deNovo.py` - Experimental features (use with caution)

## Quick Start

### Basic Example (Sync)
```python
import sys
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint

gp = GuardPoint(
    host='https://sensoraccess.example.com',
    username='admin',
    pwd='password',
    p12_file='/path/to/cert.p12',
    p12_pwd='cert_password'
)

# Get a cardholder
cardholder = gp.get_card_holder(lastName='Smith')
print(f"Found: {cardholder.firstName} {cardholder.lastName}")
```

### Async Example
```python
import asyncio
import sys
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPointAsyncIO

async def main():
    gp = GuardPointAsyncIO(
        host='https://sensoraccess.example.com',
        username='admin',
        pwd='password'
    )
    
    cardholders = await gp.get_card_holders(limit=10)
    for ch in cardholders:
        print(f"{ch.firstName} {ch.lastName}")

asyncio.run(main())
```

## Configuration

Most examples expect the following environment variables or hardcoded configuration:

- `GP_HOST` - GuardPoint server URL (e.g., `https://sensoraccess.duckdns.org`)
- `GP_USER` - Admin username
- `GP_PASS` - Admin password
- `TLS_P12` - Path to PKCS#12 certificate file (optional)
- `TLS_P12_PWD` - Certificate password (optional)

Update these in each script before running, or set environment variables.

## Running Examples

```bash
# Make sure you're in the project root
cd /path/to/pyGuardPoint

# Run a basic example
python examples/01_basics/tutorial.py

# Run an async example
python examples/03_async/asyncio_test.py

# Run tests
python examples/06_tests/test_events.py
```

## Recent Bug Fixes

These examples benefit from recent critical bug fixes in v2.0.8+:
- ✅ Fixed Observable state corruption (thread-safe now)
- ✅ Fixed async exception handling (proper error returns)
- ✅ Fixed token renewal logic (correct expiry checks)
- ✅ Added exception handling to all HTTP methods
- ✅ Fixed bare except clause

## Authentication Methods

### Bearer Token
```python
gp = GuardPoint(host='...', username='user', pwd='pass')
token = gp.get_token()
```

### Certificate-Based (PKCS#12)
```python
gp = GuardPoint(
    host='...',
    username='user',
    pwd='pass',
    p12_file='/path/to/cert.p12',
    p12_pwd='password'
)
```

### Basic Auth
```python
from pyGuardPoint.guardpoint_connection import GuardPointAuthType
gp = GuardPoint(
    host='...',
    auth=GuardPointAuthType.BASIC,
    username='user',
    pwd='password'
)
```

## API Reference

For detailed API documentation, see:
- `pyGuardPoint_Build/pyGuardPoint/guardpoint.py` - Main sync API
- `pyGuardPoint_Build/pyGuardPoint/gp_asyncio/guardpoint_asyncio.py` - Async API
- `pyGuardPoint_Build/pyGuardPoint/guardpoint_dataclasses.py` - Data models

## Troubleshooting

**"Module not found" errors:**
```python
import sys
sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint
```

**SSL Certificate errors:**
- Ensure `TLS_P12` file path is correct
- Verify certificate password in `TLS_P12_PWD`

**Authentication failures:**
- Check username and password
- Verify token expiry and renewal

**Async issues:**
- Use `GuardPointAsyncIO` for async examples
- Always `await` async methods
- Use `asyncio.run()` or proper event loop

## Contributing

To add new examples:
1. Place in appropriate category directory
2. Include docstrings and comments
3. Add to this README
4. Test before committing
