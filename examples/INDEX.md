# pyGuardPoint Examples Index

Quick reference guide to all 58 example and test scripts.

## 01_basics (5 files) - START HERE

| Script | Purpose |
|--------|---------|
| `tutorial.py` | 📚 Complete beginner's tutorial |
| `examples.py` | 📖 General usage overview |
| `simple_print_areas.py` | 🗂️ List access areas |
| `simple_print_cardholder.py` | 👤 Display cardholder details |
| `token_login.py` | 🔑 Token-based authentication |

## 02_cardholders (17 files) - Core Operations

### Retrieve Cardholders
| Script | Purpose |
|--------|---------|
| `get_all_cardholders.py` | Paginated retrieval of all cardholders |
| `get_cardholder_by_uid.py` | Lookup by unique ID |
| `get_cardholder_by_number.py` | Lookup by employee number |
| `get_cardholder_by_number_async.py` | Async version of employee number lookup |
| `get_cardholders_by_name.py` | Search by first/last name |
| `get_cardholders_by_email.py` | Search by email address |
| `get_cardholders_by_cardcode.py` | Search by card code |
| `get_cardholders_by_site.py` | Filter by site location |

### Manage Cardholders
| Script | Purpose |
|--------|---------|
| `new_cardholder.py` | Create and configure new cardholder |
| `new_cardholder_ag_uids.py` | Create with access group assignments |
| `update_isToActive.py` | Enable/disable cardholder status |
| `update_custom_field.py` | Modify custom field values |
| `filter_cardholders.py` | Advanced filtering/searching |
| `get_cardholder_types.py` | List cardholder type definitions |

### Special Operations
| Script | Purpose |
|--------|---------|
| `get_photo_blitz.py` | Bulk retrieve cardholder photos |
| `test_customizedFields.py` | Work with dynamic custom fields |
| `test_enroll_photo.py` | Photo enrollment and updates |

## 03_async (9 files) - Asynchronous Operations

| Script | Purpose |
|--------|---------|
| `asyncio_test.py` | Basic async SDK usage |
| `asyncio_cardholder_valid.py` | Async cardholder operations |
| `asyncio_events.py` | Real-time event listening (async) |
| `asyncio_alarmstates.py` | Alarm state monitoring (async) |
| `asyncio_weekly_programs.py` | Schedule management (async) |
| `test_getinfo_async.py` | System info retrieval (async) |
| `test_events_async.py` | Event processing (async) |
| `test_securitygroups_asyncio.py` | Security groups (async) |
| `test_sigR_async.py` | WebSocket real-time events (async) |

**Use these for:** High-concurrency applications, non-blocking I/O, multiple simultaneous operations

## 04_utilities (7 files) - Helper Scripts

| Script | Purpose |
|--------|---------|
| `import.py` | Bulk import cardholders from file |
| `export.py` | Bulk export cardholders to file |
| `get_cards.py` | List all access cards |
| `get_readers.py` | List all readers/controllers |
| `get_access_events_csv.py` | Export access logs to CSV |
| `update_areas.py` | Bulk area configuration |
| `multithread_it.py` | Multi-threaded operations example |

## 05_integration (4 files) - Real-Time & External Systems

| Script | Purpose |
|--------|---------|
| `test_sigR.py` | WebSocket connection (sync) |
| `test_sigR_async.py` | WebSocket connection (async) |
| `sigR_connection_blitz.py` | High-performance event streaming |
| `sigR_whatsApp.py` | WhatsApp integration example |
| `test_simAccessEv.py` | Simulated access event testing |

**Use these for:** Real-time event listeners, webhook integrations, external system notifications

## 06_tests (15 files) - Unit & Integration Tests

### Alarm & Security
| Script | Purpose |
|--------|---------|
| `test_alarmzones.py` | Alarm zone configuration |
| `test_alarmzones_arm_fields.py` | Alarm arming options |
| `test_alarmstates.py` | Real-time alarm state monitoring |
| `test_securitygroups.py` | Security group management |

### Access Control
| Script | Purpose |
|--------|---------|
| `test_accessgroups.py` | Access group operations |
| `test_events.py` | Event retrieval and filtering |
| `test_events_async.py` | Async event operations |

### Facility Management
| Script | Purpose |
|--------|---------|
| `test_sites.py` | Site management |
| `test_departments.py` | Department configuration |
| `test_weeklyprograms.py` | Weekly schedule programs |
| `test_scheduledmags.py` | Scheduled access (mags) |

### Infrastructure
| Script | Purpose |
|--------|---------|
| `test_inputs.py` | Input device testing |
| `test_outputs.py` | Output/relay testing |

### Miscellaneous
| Script | Purpose |
|--------|---------|
| `test_getinfo.py` | System information |
| `test_counts.py` | Counting operations |
| `test_manual_events.py` | Manual event generation |

## _deNovo (1 file) - Experimental

| Script | Purpose |
|--------|---------|
| `examples_deNovo.py` | Experimental features (use with caution) |

---

## Recommended Learning Path

1. **Start:** `01_basics/tutorial.py` or `01_basics/examples.py`
2. **Basic CRUD:** `02_cardholders/get_all_cardholders.py` + `new_cardholder.py`
3. **Search Operations:** `02_cardholders/get_cardholders_by_*.py`
4. **Async (if needed):** `03_async/asyncio_test.py` + others
5. **Real-time:** `05_integration/test_sigR.py`
6. **Tests:** Browse `06_tests/` for your feature area

## Quick Copy-Paste Examples

### Authenticate & Get Cardholder
```bash
python examples/01_basics/token_login.py
# OR
python examples/02_cardholders/get_cardholder_by_uid.py
```

### Real-time Events
```bash
python examples/05_integration/test_sigR.py
# OR (async)
python examples/03_async/asyncio_events.py
```

### Bulk Operations
```bash
python examples/04_utilities/export.py
python examples/04_utilities/import.py
```

### Run All Tests
```bash
for test in examples/06_tests/test_*.py; do
  echo "Running $test..."
  python "$test"
done
```

---

## Statistics

- **Total Examples:** 58
- **Sync Examples:** 35
- **Async Examples:** 9
- **Integration Examples:** 4
- **Experimental:** 1
- **Categories:** 8

**Last Updated:** June 2026  
**pyGuardPoint Version:** 2.0.8+
