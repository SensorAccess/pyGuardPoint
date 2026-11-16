"""
Offline tests for the newer endpoints (inputs/alarm actions, relay broadcast
commands, departments CRUD, scheduled readers, workstations, options, event date filters...).

A fake transport records each request and returns a canned response, so these check the exact
URL / method / body sent and how responses are parsed - no server needed.
"""
import asyncio
from datetime import datetime, timezone, timedelta

import pytest

from pyGuardPoint_Build.pyGuardPoint import (
    GuardPoint, GuardPointAsyncIO, GuardPointError, GuardPointUnauthorized, Department, ScheduledMag,
    ScheduledAdditionalReader, Relay, WindowType, PeriodType, LogEventType, ReaderLastDetails,
)
from pyGuardPoint_Build.pyGuardPoint import _action_helpers as h

U1 = "11111111-2222-3333-4444-555555555555"
U2 = "66666666-7777-8888-9999-000000000000"


class FakeSync(GuardPoint):
    """GuardPoint with the network replaced by a request recorder."""

    def __init__(self, responses=None):
        # Deliberately skip GuardPoint.__init__ - no connection is opened.
        self.site_uid = None
        self.baseurl = "https://fake"
        self.requests = []
        self.responses = list(responses or [])

    def _next(self):
        return self.responses.pop(0) if self.responses else (200, None)

    def gp_json_query(self, method, url, json_body='', headers=None):
        self.requests.append((method, url, json_body or None))
        return self._next()

    def gp_binary_query(self, url, accept='*/*'):
        self.requests.append(("GET", url, None))
        return self._next()


class FakeAsync(GuardPointAsyncIO):
    def __init__(self, responses=None):
        self.site_uid = None
        self.baseurl = "https://fake"
        self.requests = []
        self.responses = list(responses or [])

    async def gp_json_query(self, method, url, json_body='', headers=None):
        self.requests.append((method, url, json_body or None))
        return self.responses.pop(0) if self.responses else (200, None)


# --------------------------------------------------------------------------- helpers

class TestHelpers:
    def test_uid_or_api_key_requires_exactly_one(self):
        with pytest.raises(ValueError):
            h.uid_or_api_key_body(None, None)
        with pytest.raises(ValueError):
            h.uid_or_api_key_body(U1, "K1")
        assert h.uid_or_api_key_body(U1) == {'uid': U1}
        assert h.uid_or_api_key_body(api_key="R5") == {'apiKey': "R5"}

    def test_resolve_uid_accepts_objects_and_rejects_garbage(self):
        assert h.resolve_uid(Relay(uid=U1)) == U1
        with pytest.raises(ValueError):
            h.resolve_uid("not-a-uid")

    def test_uids_or_api_keys(self):
        assert h.uids_or_api_keys_body(U1) == {'uids': [U1]}
        assert h.uids_or_api_keys_body([U1, U2], "R1") == {'uids': [U1, U2], 'apiKeys': ["R1"]}
        with pytest.raises(ValueError):
            h.uids_or_api_keys_body()

    def test_raise_for_error(self):
        h.raise_for_error(204, None)
        with pytest.raises(GuardPointUnauthorized):
            h.raise_for_error(401, {})
        with pytest.raises(GuardPointError, match="Input Not Found"):
            h.raise_for_error(404, {"message": "NotFound"}, "Input Not Found")
        with pytest.raises(GuardPointError, match="API_Key_Not_Found"):
            h.raise_for_error(400, {"message": "API_Key_Not_Found"})
        with pytest.raises(GuardPointError, match="nope"):
            h.raise_for_error(200, {"success": False, "errorMessages": ["nope"]})

    def test_parse_options_handles_json_text_value(self):
        # What the server really returns for GetOptionsByKeys / GetLiteOptions
        body = {"@odata.context": "x", "value": '{\r\n  "UniqueCardholderNumberRequired": false,\r\n  "X": null\r\n}'}
        assert h.parse_options(body) == {"UniqueCardholderNumberRequired": False, "X": None}
        assert h.parse_options({"value": {"A": 1}}) == {"A": 1}

    def test_parse_string_list(self):
        assert h.parse_string_list({"stringValues": ["a", "b"]}) == ["a", "b"]
        assert h.parse_string_list(None) == []

    def test_parse_output_result(self):
        assert h.parse_output_result({"keys": [U1], "values": ["OK"]}) == {U1: "OK"}
        assert h.parse_output_result(None) == {}

    def test_odata_datetime(self):
        assert h.odata_datetime(datetime(2026, 11, 1)) == "2026-11-01T00:00:00Z"
        plus1 = datetime(2026, 11, 1, 9, 30, tzinfo=timezone(timedelta(hours=1)))
        assert h.odata_datetime(plus1) == "2026-11-01T09:30:00%2B01:00"
        assert h.odata_datetime("2026-11-01T00:00:00Z") == "2026-11-01T00:00:00Z"
        with pytest.raises(ValueError):
            h.odata_datetime("yesterday")

    def test_single_entity_accepts_wrapped_and_bare(self):
        assert h.single_entity({"value": [{"uid": U1}]}) == {"uid": U1}
        assert h.single_entity({"@odata.context": "x", "uid": U1}) == {"uid": U1}
        assert h.single_entity({"value": []}) is None


# --------------------------------------------------------------------------- inputs / alarms

class TestInputAndAlarmActions:
    def test_bypass_input_by_uid_and_api_key(self):
        gp = FakeSync()
        assert gp.bypass_input(U1) is True
        assert gp.bypass_input(api_key="R5", bypass=False) is True
        assert gp.requests == [
            ("POST", "/odata/API_Inputs/BypassInput", {'uid': U1, 'bypass': True}),
            ("POST", "/odata/API_Inputs/BypassInput", {'apiKey': "R5", 'bypass': False}),
        ]

    def test_ack_confirm(self):
        gp = FakeSync()
        gp.acknowledge_input(U1)
        gp.confirm_input(api_key="R5", description="checked")
        gp.acknowledge_all_inputs()
        gp.confirm_all_inputs()
        gp.acknowledge_alarm(U1)
        gp.confirm_alarm(U2, "ok")
        gp.acknowledge_alarm_zone(U1)
        assert gp.requests == [
            ("POST", "/odata/API_Inputs/AcknowledgeInput", {'uid': U1}),
            ("POST", "/odata/API_Inputs/ConfirmInput", {'apiKey': "R5", 'description': "checked"}),
            ("POST", "/odata/API_Inputs/AcknowledgeAll", None),
            ("POST", "/odata/API_Inputs/ConfirmAll", None),
            ("POST", "/odata/API_AlarmStates/AcknowledgeAlarm", {'uid': U1}),
            ("POST", "/odata/API_AlarmStates/ConfirmAlarm", {'uid': U2, 'description': "ok"}),
            ("POST", "/odata/API_AlarmZones/AcknowledgeAlarmZone", {'uid': U1}),
        ]

    def test_not_found_maps_to_error(self):
        gp = FakeSync([(404, {"message": "NotFound"})])
        with pytest.raises(GuardPointError, match="Input Not Found"):
            gp.acknowledge_input(U1)


# --------------------------------------------------------------------------- outputs

class TestOutputActions:
    def test_activate_variants(self):
        gp = FakeSync()
        gp.activate_relays([Relay(uid=U1), U2], period=5)
        gp.activate_relay_by_api_key("R1")
        gp.deactivate_relays(U1)
        gp.return_relays_to_normal(api_keys=["R1", "R2"])
        assert gp.requests == [
            ("POST", "/odata/API_Outputs/Activate", {'uids': [U1, U2], 'period': 5}),
            ("POST", "/odata/API_Outputs/Activate", {'apiKeys': ["R1"], 'period': 0}),
            ("POST", "/odata/API_Outputs/Deactivate", {'uids': [U1]}),
            ("POST", "/odata/API_Outputs/ReturnToNormal", {'apiKeys': ["R1", "R2"]}),
        ]

    def test_broadcasts(self):
        gp = FakeSync()
        gp.activate_all_readers()
        gp.deactivate_all_readers()
        gp.return_to_normal_all_readers()
        gp.open_all_door_relays()
        gp.open_all_door_relays(period=7)
        gp.close_all_door_relays()
        gp.return_to_normal_all_door_relays()
        assert [r[1].rsplit('/', 1)[1] for r in gp.requests] == [
            "ActivateAllReaders", "DeactivateAllReaders", "ReturnToNormalAllReaders", "OpenAllDoorRelays",
            "OpenAllDoorRelaysWithPeriod", "CloseAllDoorRelays", "ReturnToNormalAllDoorRelays"]
        assert gp.requests[4][2] == {'period': 7}

    def test_per_relay_error_is_surfaced(self):
        body = {U1: {"item1": {"message": "Relay_Offline"}, "item2": None}}
        gp = FakeSync([(400, body)])
        with pytest.raises(GuardPointError, match="Relay_Offline"):
            gp.activate_relays(U1)


# --------------------------------------------------------------------------- infrastructure

class TestInfrastructure:
    def test_controller_site_reader(self):
        gp = FakeSync([(200, None), (200, None), (200, None),
                       (200, {"readerUID": U1, "readerName": "Front", "cardholderFirstName": "Ann"}),
                       (404, {"message": "NotFound"})])
        gp.initialize_controller(api_key="C1")
        gp.start_site_polling(U1)
        gp.stop_site_polling(U1)
        details = gp.get_reader_last_details(U1)
        assert isinstance(details, ReaderLastDetails) and details.cardholderFirstName == "Ann"
        assert gp.get_reader_last_details(api_key="R9") is None
        assert gp.requests[0] == ("POST", "/odata/API_Controllers/InitializeController", {'apiKey': "C1"})
        assert gp.requests[3] == ("GET", f"/odata/API_Readers({U1})/GetReaderLastDetails", None)
        assert gp.requests[4] == ("POST", "/odata/API_Readers/GetReaderLastDetailsByApiKey", {'apiKey': "R9"})

    def test_send_free_command_validates_hex(self):
        gp = FakeSync()
        with pytest.raises(ValueError):
            gp.send_free_command(U1, "not hex!")
        gp.send_free_command([U1], "7901000000000A28")
        assert gp.requests == [("POST", "/api/Diagnostic", {'controllersUIDs': [U1], 'command': "7901000000000A28"})]


# --------------------------------------------------------------------------- CRUD

class TestCrud:
    def test_department_crud_bodies(self):
        gp = FakeSync([(201, {"uid": U1, "name": "Ops"}), (204, None), (204, None)])
        created = gp.new_department(Department(name="Ops", description="d"))
        assert created.uid == U1
        created.description = "new"
        gp.update_department(created)
        gp.delete_department(created)
        post, patch, delete = gp.requests
        assert post == ("POST", "/odata/API_Departments", {'name': "Ops", 'description': "d"})
        assert patch[0:2] == ("PATCH", f"/odata/API_Departments({U1})") and 'uid' not in patch[2]
        assert delete == ("DELETE", f"/odata/API_Departments({U1})", None)

    def test_scheduled_mag_update_sends_changes_plus_cardholder(self):
        gp = FakeSync([(204, None)])
        sm = ScheduledMag({'uid': U1, 'cardholderUID': U2, 'toDateValid': "2026-01-01T00:00:00Z", 'status': "Downloaded"})
        sm.toDateValid = "2027-01-01T00:00:00Z"
        gp.update_scheduled_mag(sm)
        assert gp.requests == [("PATCH", f"/odata/API_ScheduledMags({U1})",
                                {'toDateValid': "2027-01-01T00:00:00Z", 'cardholderUID': U2})]

    def test_scheduled_reader_crud(self):
        gp = FakeSync([(200, {"value": []}), (201, {"uid": U1}), (204, None)])
        gp.get_scheduled_additional_readers(cardholder=U2)
        sar = ScheduledAdditionalReader(cardholderUID=U2, reader_APIKey="r1", wP_APIKey="wp1",
                                        fromDateValid="2026-01-01T00:00:00Z", toDateValid="2026-02-01T00:00:00Z")
        assert gp.add_scheduled_additional_reader(sar) == U1
        gp.delete_scheduled_additional_reader(U1)
        assert f"$filter=cardholderUID%20eq%20{U2}" in gp.requests[0][1]
        assert gp.requests[1][2] == {'cardholderUID': U2, 'reader_APIKey': "r1", 'wP_APIKey': "wp1",
                                     'fromDateValid': "2026-01-01T00:00:00Z", 'toDateValid': "2026-02-01T00:00:00Z"}

    def test_scheduled_reader_update_sends_only_dates_and_wp(self):
        # Server treats readerUID/cardholderUID in a PATCH as a new overlapping schedule,
        # and rejects wP_APIKey on PATCH - so only dates + wpuid go out.
        gp = FakeSync([(201, None)])
        sar = ScheduledAdditionalReader({'uid': U1, 'cardholderUID': U2, 'readerUID': U2, 'wpuid': U2,
                                         'wP_APIKey': "Always", 'toDateValid': "2027-01-01T00:00:00Z",
                                         'status': "Downloaded"})
        gp.update_scheduled_additional_reader(sar)
        assert gp.requests == [("PATCH", f"/odata/API_ScheduledAdditionalReaders({U1})",
                                {'toDateValid': "2027-01-01T00:00:00Z", 'wpuid': U2})]

    def test_add_scheduled_mag_omits_empty_guid(self):
        gp = FakeSync([(201, {"uid": U1})])
        uid = gp.add_scheduled_mag(ScheduledMag(securityGroupAPIKey="Always", cardholderUID=U2,
                                                fromDateValid="a", toDateValid="b"))
        assert uid == U1
        assert gp.requests[0][2] == {'securityGroupAPIKey': "Always", 'cardholderUID': U2,
                                     'fromDateValid': "a", 'toDateValid': "b"}


# --------------------------------------------------------------------------- misc reads

class TestMiscReads:
    def test_options_companies_photos(self):
        gp = FakeSync([(200, {"value": '{"A": true}'}), (200, {"value": '{"B": 1}'}),
                       (200, {"stringValues": ["Acme"]}), (200, b"\x89PNG", "image/png"), (404, b"", None)])
        assert gp.get_options_by_keys("A") == {"A": True}
        assert gp.get_lite_options() == {"B": 1}
        assert gp.get_all_companies() == ["Acme"]
        assert gp.get_card_holder_photo_image(U1) == (b"\x89PNG", "image/png")
        assert gp.get_card_holder_photo_image(U1) == (None, None)
        assert gp.requests[0] == ("POST", "/odata/GetOptionsByKeys", {'keys': ["A"]})
        assert gp.requests[3] == ("GET", f"/Photos/{U1}", None)

    def test_access_groups_for_cardholder(self):
        gp = FakeSync([(200, {"value": [{"uid": U1, "name": "Visitor Exit"}]})])
        ags = gp.get_cardholder_access_groups(U2)
        assert ags[0].name == "Visitor Exit"
        assert gp.requests[0][1] == f"/odata/GetAGsForCardholder(uid={U2})"


# --------------------------------------------------------------------------- workstations

class TestWorkstations:
    def test_actions(self):
        gp = FakeSync()
        gp.display_message("WS1", "Hello", "Title")
        gp.close_workstation(["WS1", "WS2"], period=2, period_type=PeriodType.Minutes)
        gp.log_into_events_log("WS1", "note", LogEventType.Alarm)
        gp.open_window("WS1", WindowType.CardholderPopupView, uid=U1)
        assert gp.requests[0][2] == {'workstations': ["WS1"], 'message': "Hello", 'title': "Title"}
        assert gp.requests[1][2] == {'workstations': ["WS1", "WS2"], 'period': 2, 'periodType': "Minutes"}
        assert gp.requests[2][2]['logType'] == "Alarm"
        assert gp.requests[3][2]['windowData'] == {'window': "CardholderPopupView", 'isFloating': False, 'uid': U1}

    def test_requires_workstation(self):
        with pytest.raises(ValueError):
            FakeSync().workstation_logout(None)


# --------------------------------------------------------------------------- event date filters

class TestEventDateFilter:
    def test_since_until_in_url(self):
        gp = FakeSync([(200, {"value": []})])
        gp.get_access_events(limit=5, since=datetime(2026, 11, 1), until="2026-11-02T00:00:00Z")
        url = gp.requests[0][1]
        assert "$filter=((dateTime%20ge%202026-11-01T00:00:00Z)%20and%20(dateTime%20lt%202026-11-02T00:00:00Z))&" in url

    def test_combined_with_min_log_id_and_site(self):
        gp = FakeSync([(200, {"value": []})])
        gp.site_uid = U1
        gp.get_audit_events(limit=5, min_log_id=10, since=datetime(2026, 11, 1))
        url = gp.requests[0][1].replace('%20', ' ')
        assert "(logID gt 10)" in url and f"(ownerSiteUID eq {U1})" in url
        assert "(dateTime ge 2026-11-01T00:00:00Z)" in url

    def test_count_accepts_window(self):
        gp = FakeSync([(200, {"value": [], "@odata.count": 3})])
        assert gp.get_alarm_events_count(since=datetime(2026, 11, 1)) == 3
        assert "dateTime%20ge" in gp.requests[0][1]


# --------------------------------------------------------------------------- async parity

class TestAsyncParity:
    def test_async_bodies_match_sync(self):
        async def run():
            gp = FakeAsync([(200, None)] * 4 + [(200, {"value": []})])
            await gp.bypass_input(U1)
            await gp.activate_relays(api_keys="R1", period=3)
            await gp.open_all_door_relays(period=4)
            await gp.delete_department(U1)
            await gp.get_access_events(limit=1, since=datetime(2026, 11, 1))
            return gp.requests
        reqs = asyncio.run(run())
        assert reqs[0] == ("POST", "/odata/API_Inputs/BypassInput", {'uid': U1, 'bypass': True})
        assert reqs[1] == ("POST", "/odata/API_Outputs/Activate", {'apiKeys': ["R1"], 'period': 3})
        assert reqs[2] == ("POST", "/odata/API_Outputs/OpenAllDoorRelaysWithPeriod", {'period': 4})
        assert reqs[3] == ("DELETE", f"/odata/API_Departments({U1})", None)
        assert "dateTime%20ge%202026-11-01T00:00:00Z" in reqs[4][1]
