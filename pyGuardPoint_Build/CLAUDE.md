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
    host='https://sensoraccess2.duckdns.org',
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
| `arm_alarm_zone(zone, …)` | `ArmAlarmZoneResult` (truthy on success, NOT a plain bool) |
| `disarm_alarm_zone(zone, …)` | `True`/`False` (bool) |
| `get_reader_alarm_zone(reader, …)` | `AlarmZone` or `None` |
| `get_alarm_zone_readers(zone, …)` | `list[Reader]` (possibly empty) |

### No-argument list methods (do NOT pass limit= or offset=)

These fetch everything and take no arguments:
`get_areas()`, `get_alarm_zones()`,
`get_alarm_states()`, `get_departments()`, `get_sites()`, `get_weekly_programs()`,
`get_controllers()`, `get_relays()`, `get_cardholder_types()`,
`get_manual_events()`, `get_infos()`, `get_scheduled_mags()`

### Methods that do accept pagination / filtering

`get_card_holders(offset, limit, search_terms, firstName, lastName, areas, …)`
`get_cards(offset=0, limit=500, count=False, **card_kwargs)` — batched in chunks of 40 like `get_readers`
`get_readers(offset, limit, **reader_kwargs)`
`get_inputs(offset=0, limit=500)` — defaults fetch everything (batched in chunks of 40)
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

### Control actions and the rest of the GP10 API

Every method below exists on `GuardPoint` and (as `async def`) on `GuardPointAsyncIO`.
Single-target actions take an object **or** its UID, or `api_key=` instead — exactly one.
Unless noted they return `True` and raise `GuardPointError` on failure.

| Area | Methods |
|---|---|
| Inputs | `bypass_input(inp, api_key=, bypass=True)`, `acknowledge_input`, `confirm_input(…, description=)`, `acknowledge_all_inputs()`, `confirm_all_inputs()` |
| Alarms | `acknowledge_alarm(alarm)`, `confirm_alarm(alarm, description=)`, `acknowledge_alarm_zone(zone)` |
| Relays | `activate_relays(relays=, api_keys=, period=0)`, `activate_relay_by_api_key`, `deactivate_relays`, `return_relays_to_normal`, `get_relay_readers(relay)` → `list[Reader]` |
| Broadcast | `activate_all_readers()`, `deactivate_all_readers()`, `return_to_normal_all_readers()`, `open_all_door_relays(period=None)`, `close_all_door_relays()`, `return_to_normal_all_door_relays()` |
| Controllers / sites | `initialize_controller(ctrl, api_key=)`, `start_site_polling(site)`, `stop_site_polling(site)`, `get_networks()`, `get_network(uid)` |
| Readers | `get_reader_last_details(reader, api_key=)` → `ReaderLastDetails` or `None` |
| Departments | `new_department(d)` → `Department`, `update_department(d)`, `delete_department(d)` |
| Scheduled MAGs | `get_scheduled_mag(uid)`, `add_scheduled_mag(sm)` → uid, `update_scheduled_mag(sm)` (changed fields only), `delete_scheduled_mag(sm)` |
| Scheduled readers | `get_scheduled_additional_readers(cardholder=)`, `get_scheduled_additional_reader(uid)`, `add_…` → uid, `update_…`, `delete_…` |
| Cardholder extras | `get_cardholder_access_groups(ch)` → `list[AccessGroup]`, `get_all_companies()` → `list[str]`, `get_card_holder_photo_image(ch)` → `(bytes, content_type)`, `get_all_photos(offset, limit)` |
| Options | `get_options_by_keys(keys)` → dict, `get_lite_options()` → dict, `get_non_editable_properties("API_Cards")` → `list[str]` |
| Events | `since=` / `until=` on every `get_*_events` and `get_*_events_count`; `insert_access_event(event)` |
| Diagnostics | `send_free_command(controllers, "hex")` (general form of `simulate_access_event`) |
| Parking | `get_parking_groups()` |
| Workstations | `get_workstations()`, `get_available_sounds()`, `workstation_login/logout`, `close_workstation`, `bring_workstation_to_front`, `display_message`, `play_sound`, `log_into_events_log`, `open_window(ws, WindowType…, uid=)` |

Relay methods return `{relay_uid: message}` (the server's per-relay map; usually empty).
`open_all_door_relays()` with no period holds every door open until
`return_to_normal_all_door_relays()` — treat as an evacuation-level action.

Request bodies follow the server's live `$metadata` (actions/functions), which is
authoritative over the Postman collection where they disagree.

The shared, I/O-free request/response logic lives in `pyGuardPoint/_action_helpers.py`;
`_gp_call()` on each connection class sends a request and raises on failure.

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

### `AuditEvent.auditChanges` is the field-level diff

`get_audit_events()` carries two fields the other event types don't have:

| Field | What it holds |
|---|---|
| `entityUID` | uid of the object the entry is about — join back to the Cardholder/Card/etc. |
| `auditChanges` | free-text diff, `"PIN code: '1111' -> '2222' \| Status: 'Invalidated' -> 'Validated'"` |

Both were **added to the dataclass in 2.5.4**. Before that they were undeclared: attribute
access happened to work (`sanitise_args` doesn't filter positional dicts) but `.dict()` uses
`asdict()`, which only sees declared fields — so any `.dict()`-based scan silently lost them.
`AuditEvent` was the only event dataclass with a gap; the other seven match the server schema.

`auditChanges` is empty for operations the server records without detail — notably the
automated nightly cardholder purge (`02:50`, `DeleteOperation`), which dominates the newest
rows. Page back with `offset` before concluding a log has no diffs.

`objectName` is a free-text `Edm.String`, **not** an enum, so the set of values is open-ended.
Observed over 3000 rows: `Cardholder`, `Card`, `Controller`, `Reader`, `Input`, `Output`,
`AlarmZone`, `AccessGroup`, `AccessGroupUnit`, `SecurityGroup`, `CustomizedField`, `Network`,
`ManualEvent`, `SmartDevice`, `Profile`, `Options`, `GR_Reflex`, and **`User`**. Don't assume a
small sample is exhaustive.

### Operator password changes are audited only as a bare `User` update

`objectName='User'` rows track GP10 operator accounts (`NewOperation`/`UpdateOperation`/
`DeleteOperation`), with `userName` as the actor and `data` as the target account. Field edits
get a diff (`Profile: 'reception' -> 'Administrator'`, `Allow API: 'False' -> 'True'`).

A **password change is never named**: filtering `contains(auditChanges, …)` for `password`,
`Password`, `PASSWORD`, `pwd`, `Pwd` over the whole log returns zero rows, as does the same
against `data`. What you get is a `User`/`UpdateOperation` with `auditChanges` **empty** — so
you can prove an account was modified, when, and by whom, but not that it was the password.
A self-edit (actor == target) with a blank diff is the strongest available signal.

Cardholder PINs, by contrast, are logged **in clear text** — both old and new value — so
audit-log read access is enough to recover current PINs.

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
| URL | `https://sensoraccess2.duckdns.org` |
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
pytest                             # full pytest suite
pytest tests/test_new_endpoints_offline.py   # no server needed
pytest tests/test_new_endpoints_live.py      # never operates real doors/inputs/alarms
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
`get_card(uid)`, `get_reader(uid)`, and `get_department(uid)` used to return objects where
`.uid` is an empty string. The `value` field in the OData response is a list; these
methods were passing the list directly to the dataclass constructor (which only handles
dicts). The fix — `value[0]` — is applied in both the sync and async clients. If you see
empty `.uid` on other single-item fetches, the same fix applies.

Not every entity set wraps single fetches in `value`: `API_AlarmStates(uid)` returns the
entity itself at the top level (with `@odata.context`, and without honouring
`$expand=Input`). `get_alarm_state()` accepts either shape.

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

### `ArmAlarmZone` returns the inputs that are in alarm
Newer GuardPoint10 releases return `ACS.API.ArmAlarmZoneResponse` from
`/odata/API_AlarmZones/ArmAlarmZone`:

```json
{"success": true, "errorMessages": [], "triggeredInputs": [{"name": "…", "uid": "…"}]}
```

`arm_alarm_zone()` therefore returns an `ArmAlarmZoneResult`, not a bool. It
defines `__bool__`, so `if gp.arm_alarm_zone(zone):` still works — but
`result == True` and `result is True` do not. Use the object for detail:

```python
result = gp.arm_alarm_zone(zone, option=AlarmZoneOption.Arm,
                           arm_type=AlarmZoneArmType.ArmConstantly,
                           bypass_mode=ArmBypassMode.Cancel)
if not result:
    for i in result.triggered_inputs:      # list[TriggeredInput] — name + uid only
        print(f"arming blocked by {i.name}")
```

`triggeredInputs` only comes back from `ArmAlarmZone`. `DisarmAlarmZone` and
`ReturnAlarmZoneToWeeklyProgram` still return a plain `ResponseObject`, so
`disarm_alarm_zone()` stays a bool and `triggered_inputs` is `[]` for the
`ReturnAlarmZoneToWeeklyProgram` option — as it also is against older servers
that predate the response change.

`TriggeredInput` carries only `name` and `uid`; use `get_input(uid)` for the
full `Input` record.

### `Input.inputGroupUID` is actually the AlarmZone UID
Despite the name, `Input.inputGroupUID` holds the parent `AlarmZone.uid`, not an
"input group" entity. There is no OData `$expand` between `API_Inputs` and
`API_AlarmZones` — join client-side on this field. Inputs not assigned to any
zone have `inputGroupUID = None`. See `examples/06_tests/inputs_by_alarmzone.py`.

### Access rights cannot be linked to an AlarmZone
`API_SecurityGroup` and `API_AccessGroup` carry only `uid`/`name`/`description`
(+`accessGroupType`) and have **no navigation properties at all** — which readers an
access group contains is not exposed, so `$expand=readers` and friends return HTTP 400.
`API_AlarmZone`'s only navigation property is `weeklyProgram`. There is therefore no
configuration path from a cardholder's rights to a zone.

On the Cardholder, `accessGroupUIDs` and `liftAccessGroupUIDs` are `Edm.String`
(a delimited UID list), not navigation properties — only `securityGroup` is a real
relationship.

What *does* exist is a door-level join, via the reader's door inputs:

```
Reader.doorAlarmInputUID ──▶ Input.uid ;  Input.inputGroupUID ──▶ AlarmZone.uid
```

`get_reader_alarm_zone(reader)` and `get_alarm_zone_readers(zone)` wrap it (sync and
async). They fall back through `doorControlInput1UID`, `doorControlInput2UID`,
`doorRemoteInputUID`, `motorizedReaderInputUID` — see `READER_INPUT_UID_FIELDS` in
`guardpoint_utils.py`. Both take optional pre-fetched `readers`/`inputs`/`alarm_zones`;
pass them when looping, or each call re-fetches.

```python
readers, inputs, zones = gp.get_readers(), gp.get_inputs(), gp.get_alarm_zones()
for r in readers:
    z = gp.get_reader_alarm_zone(r, inputs=inputs, alarm_zones=zones)
```

A reader returns `None` whenever none of its door inputs is assigned to a zone — the
common case, since inputs default to no zone. A coarser fallback, not implemented
because it can span zones: match `Reader.controllerUID` against the controllers of the
zone's inputs.

To tie a *cardholder* to a zone you must go through observed behaviour, since
`AccessEvent` carries both `cardholderUID` and `readerUID`:
`Cardholder → AccessEvent.readerUID → Reader → door input → AlarmZone`. That reports
zones a person has actually entered, not what they are entitled to.


### Scheduled MAG / additional reader deletes are queued
`delete_scheduled_mag()` / `delete_scheduled_additional_reader()` return `True` (204), but a
GET straight afterwards still returns the record with `status == "AskToDelete"` until the
controllers confirm. Check `status`, not existence.

### Scheduled additional reader PATCH
Only `fromDateValid`, `toDateValid` and `wpuid` can be patched. Including `readerUID` /
`cardholderUID` makes the server treat it as a new overlapping schedule
(`Error_ScheduleAdditionalReaderOverlapOlderOne`), and `wP_APIKey` is rejected on PATCH even
though the Postman collection uses it. `update_scheduled_additional_reader()` sends only the
allowed fields. To move a schedule to another reader, delete and re-add.

### Empty Guid strings are rejected
Unset Guid fields serialise as `""`, which the server rejects with "The input was not valid."
This is why `add_scheduled_mag()` failed on every call before this fix (it sent
`scheduledSecurityGroupUID: ""`). `dict(editable_only=True)` on `ScheduledMag`, `Department`
and the newer dataclasses now drops `""`/`None` values.

### Responses that don't match `$metadata`
- `GetOptionsByKeys` / `GetLiteOptions` return `{"value": "<JSON text>"}` — parsed for you.
- `GetAllCompanies` returns `{"stringValues": [...]}`.
- `/Photos/{uid}` returns raw image bytes (not JSON) — hence `gp_binary_query()`.
- `GetReaderLastDetails` returns 404 for a reader with no recorded pass → `None`.
- `BypassInput` / `AcknowledgeInput` / `ConfirmInput` with an unknown **UID** answer
  `API_Key_Not_Found`, not `UID_Not_Found`.

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
AlarmZone, TriggeredInput, ArmAlarmZoneResult
Input, AlarmState, Site, ParkingGroup, Network, ReaderLastDetails
CardholderPhoto, Workstation, ScheduledAdditionalReader

# Enums
SortAlgorithm, EventOrder, CardholderOrderBy, CardType
AlarmZoneOption, AlarmZoneArmType, AlarmZoneDisarmType, ArmBypassMode
PeriodType, LogEventType, WindowType
```

---

## Build

```bash
cd pyGuardPoint_Build
python -m build          # produces dist/pyguardpoint-X.Y.Z.tar.gz and .whl
pip install dist/pyguardpoint-*.whl
```

`find_packages(exclude=['tests', 'tests.*'])` installs only `pyGuardPoint` and
`pyGuardPoint.gp_asyncio`. `tests/` (including the `.p12` cert) and `examples/` ship in the
**sdist only**, via `MANIFEST.in` — they are not installed, because a top-level `tests`
package shadows other projects' and its `pyGuardPoint_Build.pyGuardPoint` imports only
resolve from a source checkout.

- `python_requires='>=3.10'` — `pysignalr>=1.3.0` needs 3.10+, so 3.9 cannot install it.
- `aiohttp` is declared explicitly (the async client imports it directly).
- `README.rst` is Markdown-compatible, **not valid reStructuredText** — keep
  `long_description_content_type='text/markdown'`; switching to `text/x-rst` would make PyPI
  reject the upload ("description failed to render").
