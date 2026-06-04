# pyGuardPoint Test Suite

Two styles of test are provided:

| Style | Files | Purpose |
|---|---|---|
| **Script runners** | `run_tests.py`, `run_tests_async.py` | Human-readable output, quick sanity check, good first read for new users |
| **pytest suite** | `test_*.py` | Structured assertions, CI integration, per-feature isolation |

---

## Prerequisites

```bash
pip install pytest
```

The test server at `https://sensoraccess.duckdns.org` requires **mutual TLS (mTLS)** — you must supply a client certificate in PKCS#12 format.

---

## Configuration

All settings are driven by environment variables. The client certificate (`MobileGuardDefault.p12`, password `test`) is bundled in this directory and used by default, so no extra setup is needed to run against the public test server.

| Variable | Default | Description |
|---|---|---|
| `GP_HOST` | `https://sensoraccess.duckdns.org` | GuardPoint server URL |
| `GP_USER` | `admin` | Username |
| `GP_PASS` | `admin` | Password |
| `GP_P12` | `tests/MobileGuardDefault.p12` | Path to the client certificate (mTLS) |
| `GP_P12_PWD` | `test` | Password for the P12 file |

Override any of these to run against a different server:

```bash
export GP_HOST="https://my-server.example.com"
export GP_P12="/path/to/my-cert.p12"
export GP_P12_PWD="mypassword"
```

---

## Script runners

These scripts print a clear pass/fail for every API call and are the fastest way to verify a working setup.

```bash
# Synchronous API
python tests/run_tests.py

# Async API (GuardPointAsyncIO)
python tests/run_tests_async.py
```

Both scripts can also be run from the project root:

```bash
python tests/run_tests.py
```

### Example output

```
===========================================================================
  PyGuardPoint Integration Test Suite
===========================================================================

  Server : https://sensoraccess.duckdns.org
  User   : admin
  P12    : /path/to/MobileGuardDefault.p12

1. AUTHENTICATION & CONNECTION
  ✓ Connect to server                              | https://sensoraccess.duckdns.org

2. CARDHOLDERS
  ✓ Get cardholders (limit 5)                      | 5 returned
  ✓ Get cardholder count                           | total=493
  ...

  PASSED  : 36/36
  SUCCESS : 100.0%
```

---

## pytest suite

```bash
# Run all tests from the project root
pytest

# Run only read-only tests (no data created or deleted)
pytest -m "integration and not destructive"

# Run only destructive tests (creates/modifies/deletes data)
pytest -m destructive

# Run a single file
pytest tests/test_cardholders.py

# Run a single test
pytest tests/test_cardholders.py::TestCardholderCRUD::test_create_cardholder

# Verbose output
pytest -v
```

### Test files

| File | What it covers |
|---|---|
| `test_cardholders.py` | Cardholder CRUD, search, pagination, edge cases |
| `test_cards.py` | Card CRUD, field validation, cardholder linkage |
| `test_api_endpoints.py` | Read-only checks across every resource type |
| `test_error_handling.py` | Auth errors, missing resources, data validation |

### Markers

| Marker | Meaning |
|---|---|
| `integration` | Requires a live GuardPoint server |
| `destructive` | Creates, modifies, or deletes data on the server |
| `slow` | Takes longer than a few seconds |

---

## What the tests cover

- **Connection** — mTLS handshake, bearer-token authentication
- **Cardholders** — create, read, update, delete, search, pagination, personal details
- **Cards** — create, read, update, delete, type validation, cardholder linkage
- **Access control** — security groups, access groups, scheduled mags
- **Areas / Sites / Departments** — list and fetch by UID
- **Alarms** — alarm states, alarm zones (list and fetch by UID)
- **Hardware** — readers, controllers, inputs, relays
- **Events** — access events, alarm events, audit events (counts + paginated lists)
- **Scheduling** — weekly programs (list and fetch by UID)
- **System info** — generic info entries, SignalR status, manual events, cardholder types

---

## Notes

- The server **soft-deletes** cardholders — a fetch immediately after deletion may still return the record. Tests rely on the HTTP 204 response rather than a post-delete re-fetch to confirm deletion.
- `run_tests_async.py` does not test `get_inputs` because that endpoint is not yet implemented in `GuardPointAsyncIO`.
- Tests are self-cleaning: the pytest `cleanup_cardholders` and `cleanup_cards` fixtures delete any data created during a test, even on failure.
