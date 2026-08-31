# pyGuardPoint — Claude Code Reference

## What this package does

pyGuardPoint is a Python wrapper for the **GuardPoint 10** access control REST API (OData-based). It manages cardholders, cards, readers, controllers, alarm zones, access events, and real-time event streaming over SignalR (WebSocket).

---

## Project layout

```
pyGuardPoint_Build/          ← pip-installable package (run python -m build here)
├── setup.py
├── CLAUDE.md                ← this file
├── llms.txt                 ← machine-readable package summary
├── pyGuardPoint/            ← main library
│   ├── guardpoint.py        ← GuardPoint (sync) class + get/start/stop_listening
│   ├── guardpoint_asyncio.py← GuardPointAsyncIO class
│   ├── guardpoint_threaded.py← GuardPointThreaded (callback-based)
│   ├── guardpoint_connection.py ← sync HTTP connection, SSL/mTLS setup, token mgmt
│   ├── guardpoint_dataclasses.py← all dataclasses (Cardholder, Card, Area, …)
│   ├── guardpoint_error.py  ← GuardPointError, GuardPointUnauthorized
│   ├── guardpoint_utils.py  ← url_parser, ConvertBase64, GuardPointResponse
│   ├── _guardpoint_*.py     ← one file per API area (cardholders, cards, events…)
│   ├── CustomWebsocketTransport.py ← custom pysignalr transport
│   └── gp_asyncio/          ← async equivalents of every _guardpoint_*.py
├── tests/                   ← integration test suite (see tests/README.md)
│   ├── MobileGuardDefault.p12  ← bundled mTLS client certificate (pwd: test)
│   ├── run_tests.py         ← sync runner  — python tests/run_tests.py
│   ├── run_tests_async.py   ← async runner — python tests/run_tests_async.py
│   ├── run_tests_signalr.py ← SignalR + event simulation test
│   ├── conftest.py          ← pytest fixtures (gp_sync, gp_async, cleanup_*)
│   └── test_*.py            ← pytest test files
└── examples/                ← real-world usage scripts (read-only reference)
    ├── 01_basics/           ← connection, areas, simple cardholder print
    ├── 02_cardholders/      ← CRUD, search, photos, custom fields
    ├── 03_async/            ← async patterns, token reuse, parallel requests
    ├── 04_utilities/        ← bulk export/import, CSV events, reader list
    ├── 05_integration/      ← SignalR, simulate access events
    └── 06_tests/            ← per-feature smoke tests
```

---

## Three client classes

| Class | Transport | Use when |
|---|---|---|
| `GuardPoint` | `http.client` (sync, blocking) | scripts, simple integrations |
| `GuardPointAsyncIO` | `aiohttp` (async) | high-throughput / concurrent requests |
| `GuardPointThreaded` | callback-based wrapper around sync | GUI / threaded apps |

All three share the same API surface. Every method in `GuardPoint` has an `async def` equivalent in `GuardPointAsyncIO`. `GuardPointThreaded` exposes a small subset with `on_finished` callbacks.

### Constructing a client

```python
from pyGuardPoint import GuardPoint, GuardPointAsyncIO

# Sync — for the public test server (requires mTLS)
gp = GuardPoint(
    host='https://sensoraccess.duckdns.org',
    username='admin',
    pwd='admin',
    p12_file='tests/MobileGuardDefault.p12',
    p12_pwd='test',
)

# Async
gp = GuardPointAsyncIO(host=..., username=..., pwd=..., p12_file=..., p12_pwd=...)
# Always call await gp.close() when done.

# Local server without mTLS
gp = GuardPoint(host='http://192.168.1.100:10695', username='admin', pwd='admin')

# Bearer-token auth (API key)
from pyGuardPoint import GuardPointAuthType
gp = GuardPoint(host=..., auth=GuardPointAuthType.BEARER_TOKEN,
                key='<api-key-uuid>')

# Scope to a single site
gp = GuardPoint(host=..., site_uid='11111111-1111-1111-1111-111111111111', ...)
```

---

## API method conventions

### Return types — critical, non-obvious

| Method | Returns |
|---|---|
| `new_card_holder(ch)` | `Cardholder` object (NOT a UID string) |
| `new_card(card)` | `Card` object (NOT a UID string) |
| `update_card_holder(ch)` | `True` (bool) |
| `update_card(card)` | `True` (bool) |
| `delete_card_holder(ch)` | `True` (bool) |
| `delete_card(card)` | `True` (bool) |
| `get_card_holder(uid=…)` | `Cardholder` or `None` |
| `get_card_holders(…)` | `list[Cardholder]` |

### No-argument list methods (do NOT pass limit= or offset=)

These fetch everything and take no arguments:
`get_areas()`, `get_alarm_zones()`,
`get_alarm_states()`, `get_departments()`, `get_sites()`, `get_weekly_programs()`,
`get_controllers()`, `get_inputs()`, `get_relays()`, `get_cardholder_types()`,
`get_manual_events()`, `get_infos()`, `get_scheduled_mags()`

### Methods that do accept pagination / filtering

`get_card_holders(offset, limit, search_terms, firstName, lastName, areas, …)`
`get_cards(offset=0, limit=500, count=False, **card_kwargs)` — batched in chunks of 40 like `get_readers`
`get_readers(offset, limit, **reader_kwargs)`
`get_access_events(limit, offset, orderby, min_log_id)`
`get_alarm_events(limit, offset, orderby)`
`get_audit_events(limit, offset, orderby, min_log_id)`
`get_comm_events(limit, offset, orderby, min_log_id)`
`get_general_events(limit, offset, orderby, min_log_id)`
`get_technical_events(limit, offset, orderby, min_log_id)`
`get_user_manual_events(limit, offset, orderby, min_log_id)`
`get_extended_union_events(limit, offset, orderby, min_log_id)` — merged feed of all event log types, discriminated by `eventType`
`get_security_groups(offset=0, limit=500, **sg_kwargs)` — defaults fetch everything (batched in chunks of 40)
`get_access_groups(offset=0, limit=500, **ag_kwargs)` — defaults fetch everything (batched in chunks of 40)

### Count-only queries

```python
total = gp.get_cardholder_count()          # dedicated endpoint
total = gp.get_cards(count=True)           # returns int
total = gp.get_access_events_count()       # returns int
total = gp.get_alarm_events_count()        # returns int
total = gp.get_audit_events_count()        # returns int
total = gp.get_comm_events_count()         # returns int
total = gp.get_general_events_count()      # returns int
total = gp.get_technical_events_count()    # returns int
total = gp.get_user_manual_events_count()  # returns int
total = gp.get_extended_union_events_count()  # returns int
```

### Event logs — which one to use

GuardPoint10 exposes 8 separate event-log entity sets, each covering a different kind of event:

| Log | What it records |
|---|---|
| `get_access_events()` | card reads / access grants / denials |
| `get_alarm_events()` | input/alarm triggers (start/end of alarm) — NOT zone arm/disarm |
| `get_audit_events()` | administrative changes, incl. **AlarmZone arm/disarm** (`objectName='AlarmZone'`, `type='UpdateOperation'` via API, or `AlarmZoneArmedByKeypad`/`AlarmZoneDisarmedByKeypad` if triggered from a physical keypad) |
| `get_comm_events()` | controller/reader connect-disconnect |
| `get_general_events()` | system-level events (log purges, backups, DB maintenance) |
| `get_technical_events()` | controller technical faults (power up/down, tamper, table errors) |
| `get_user_manual_events()` | user-acknowledged/confirmed alarms |
| `get_extended_union_events()` | all of the above merged into one feed, discriminated by `eventType` |

A **failed** action (e.g. arming with no Weekly Program defined) writes to none of these — the server rejects the request before any state change, so failures only surface as a raised `GuardPointError`, never as a log entry.

---

## The Observable / change-tracking pattern

`Cardholder`, `Card`, `Relay`, `ScheduledMag`, `CardholderCustomizedField`,
and `CardholderPersonalDetail` all inherit from `Observable`.

After you modify fields and call `update_*`, only changed fields are sent in the PATCH request:

```python
ch = gp.get_card_holder(uid='...')
ch.description = 'Updated'   # tracked in ch.changed_attributes
ch.pinCode = '9999'
gp.update_card_holder(ch)    # sends only {description, pinCode}
```

Cards can be added to a cardholder before the initial create:
```python
card = Card(cardType='Magnetic', cardCode='1A2B3C4D')
cardholder.cards.append(card)
gp.update_card_holder(cardholder)   # creates the card server-side
```

---

## Cardholder sub-objects

```python
from pyGuardPoint import CardholderPersonalDetail, CardholderCustomizedField

pd = CardholderPersonalDetail()
pd.company = 'Acme'
pd.email = 'user@acme.com'

cf = CardholderCustomizedField()
setattr(cf, 'cF_StringField_1', 'custom value')

ch = Cardholder(firstName='Jane', lastName='Doe',
                cardholderPersonalDetail=pd,
                cardholderCustomizedField=cf)
created = gp.new_card_holder(ch)   # returns Cardholder with uid set
```

---

## Real-time events (SignalR)

```python
from pyGuardPoint.guardpoint import stop_listening   # module-level function

client = gp.get_signal_client()

async def on_access_event(message): ...

client.on_open(on_open_coroutine)
client.on('AccessEventArrived',    on_access_event)
client.on('AlarmEventArrived',     handler)
client.on('AuditEventArrived',     handler)
client.on('IOEventArrived',        handler)
client.on('StatusUpdate',          handler)
client.on('TechnicalEventArrived', handler)

gp.start_listening(client)   # BLOCKS — run in a daemon thread
```

### Stopping the listener cleanly

`stop_listening(client)` calls `client._transport.close()` but **`CustomWebsocketTransport`
has no `close()` method** — it will always raise. Instead, manage the event loop yourself:

```python
import asyncio, threading

loop = asyncio.new_event_loop()
task_ref = [None]

def run_listener():
    asyncio.set_event_loop(loop)
    async def _run():
        task_ref[0] = asyncio.ensure_future(client.run())
        try:
            await task_ref[0]
        except asyncio.CancelledError:
            pass
    loop.run_until_complete(_run())

thread = threading.Thread(target=run_listener, daemon=True)
thread.start()

# … later, to stop:
loop.call_soon_threadsafe(task_ref[0].cancel)
thread.join(timeout=5)
# Drain residual tasks to suppress "Task was destroyed but pending" warnings:
for t in asyncio.all_tasks(loop):
    t.cancel()
loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop), return_exceptions=True))
loop.close()
```

See `tests/run_tests_signalr.py` for the full working example.

---

## Test server

| Detail | Value |
|---|---|
| URL | `https://sensoraccess.duckdns.org` |
| Auth | mTLS required — plain HTTPS without a client cert is rejected at the TLS layer |
| Client cert | `tests/MobileGuardDefault.p12` (bundled) |
| P12 password | `test` |
| Credentials | `admin` / `admin` |

### Running the tests

No environment variables needed — the bundled cert is used by default:

```bash
python tests/run_tests.py          # sync runner   (36 checks)
python tests/run_tests_async.py    # async runner  (35 checks)
python tests/run_tests_signalr.py  # SignalR test  (8 checks)
pytest                             # full pytest suite (70 tests)
```

---

## Known server quirks

### Soft delete
`delete_card_holder()` returns `True` (HTTP 204) but a subsequent `get_card_holder()`
may still return the record for a short period. Do not assert `is None` immediately after
deletion — trust the 204 response.

### Card codes
Card codes must contain **only hex characters (0-9, A-F)** and be **8 characters or fewer**.
Underscores, letters outside A-F, or longer strings are rejected with
`CardCode_Includes_Invalid_Characters_Or_Spaces`.

### Null UUID OData error
`get_card_holder(uid='00000000-0000-0000-0000-000000000000')` raises `GuardPointError`
(OData tries to expand sub-entities on a null record and crashes) rather than returning
`None`. Wrap in try/except when fetching potentially non-existent records.

### Single-item fetch returns object with empty `.uid`
`get_card(uid)`, `get_reader(uid)`, and `get_department(uid)` return objects where
`.uid` is an empty string. The `value` field in the OData response is a list; these
methods were passing the list directly to the dataclass constructor (which only handles
dicts). The fix — `value[0]` — was applied during this session. If you see empty `.uid`
on other single-item fetches, the same fix applies.

### Unpaginated queries cap at 50 results
The server silently truncates any single OData request without `$top`/`$skip` to 50 rows
(no error, no indication of truncation). `get_cards()` now paginates by default (like
`get_readers`), batching in chunks of 40 for `limit > 50`. Be wary of this cap if adding
new unpaginated list methods.

### Proximity card type
The test server rejects `cardType='Proximity'`. Use `'Magnetic'`.

### Special characters in search_terms
Single quotes and characters like `*`, `?` in `search_terms` break the OData `$filter`
query string and raise `GuardPointError`. Sanitise input before passing to
`get_card_holders(search_terms=…)`.

### `Input.inputGroupUID` is actually the AlarmZone UID
Despite the name, `Input.inputGroupUID` holds the parent `AlarmZone.uid`, not an
"input group" entity. There is no OData `$expand` between `API_Inputs` and
`API_AlarmZones` — join client-side on this field. Inputs not assigned to any
zone have `inputGroupUID = None`. See `examples/06_tests/inputs_by_alarmzone.py`.

### `get_inputs()` is sync-only
`GuardPointAsyncIO` does not have an async `get_inputs()` — there is no
`_async_guardpoint_inputs.py` in `gp_asyncio/`.

### `is_sigr_enabled()` is async in GuardPointAsyncIO
`await gp.is_sigr_enabled()` — don't forget the await.

---

## Exported symbols (`from pyGuardPoint import …`)

```python
# Clients
GuardPoint, GuardPointAsyncIO, GuardPointThreaded

# Auth
GuardPointAuthType   # .BASIC | .BEARER_TOKEN

# Errors
GuardPointError, GuardPointUnauthorized

# Dataclasses
Cardholder, Card, Area, SecurityGroup, AccessGroup, ScheduledMag
CardholderPersonalDetail, CardholderCustomizedField, CardholderType
Controller, Reader, Relay, Department, AccessEvent, AlarmEvent, AuditEvent
CommEvent, GeneralEvent, TechnicalEvent, UserManualEvent, ExtendedUnionEvent

# Enums
SortAlgorithm, EventOrder, AlarmZoneOption, CardholderOrderBy
```

---

## Build

```bash
cd pyGuardPoint_Build
python -m build          # produces dist/pyguardpoint-X.Y.Z.tar.gz and .whl
pip install dist/pyguardpoint-*.whl
```

`find_packages()` in `setup.py` auto-discovers `pyGuardPoint`, `pyGuardPoint.gp_asyncio`,
and `tests`. The `.p12` cert and `README.md` in `tests/` are included via `package_data`.
Examples are included under `examples/` as data files.
