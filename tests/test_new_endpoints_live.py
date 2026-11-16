"""
Live integration tests for the newer endpoints (inputs/alarm actions, relay commands, departments
CRUD, scheduled MAGs / additional readers, options, photos, event date filters...).

Safety: nothing here operates real doors, inputs, alarms, controllers or polling. Those actions
are only called against a *nonexistent* UID/API key - the server must answer with a specific
"not found" error, which proves the endpoint and request body are accepted without side effects.
CRUD tests only touch records they create, and delete them afterwards.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from pyGuardPoint_Build.pyGuardPoint import (
    GuardPointError, Cardholder, Department, ScheduledMag, ScheduledAdditionalReader, WindowType,
)

NOPE = "00000000-0000-0000-0000-0000000000ab"
WP_ALWAYS = "11111111-1111-1111-1111-111111111111"


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0)


@pytest.fixture
def throwaway_cardholder(gp_sync):
    ch = gp_sync.new_card_holder(Cardholder(firstName="pyGP", lastName=f"Live{uuid.uuid4().hex[:6]}"))
    yield ch
    try:
        gp_sync.delete_card_holder(ch)
    except GuardPointError:
        pass


# --------------------------------------------------------------------------- reads

@pytest.mark.integration
class TestReads:
    def test_cardholder_access_groups(self, gp_sync):
        ch = gp_sync.get_card_holders(limit=1)[0]
        assert isinstance(gp_sync.get_cardholder_access_groups(ch), list)

    def test_companies_and_options(self, gp_sync):
        assert isinstance(gp_sync.get_all_companies(), list)
        opts = gp_sync.get_options_by_keys(["UniqueCardholderNumberRequired"])
        assert "UniqueCardholderNumberRequired" in opts
        assert isinstance(gp_sync.get_lite_options(), dict)
        assert isinstance(gp_sync.get_non_editable_properties("API_Cards"), list)

    def test_photos(self, gp_sync):
        photos = gp_sync.get_all_photos(limit=2)
        assert isinstance(photos, list)
        assert gp_sync.get_card_holder_photo_image(NOPE) == (None, None)

    def test_misc_entity_sets(self, gp_sync):
        assert isinstance(gp_sync.get_parking_groups(), list)
        assert isinstance(gp_sync.get_workstations(), list)
        assert isinstance(gp_sync.get_scheduled_additional_readers(), list)
        networks = gp_sync.get_networks()
        if networks:
            assert gp_sync.get_network(networks[0].uid).uid == networks[0].uid

    def test_reader_last_details(self, gp_sync):
        reader = gp_sync.get_readers(limit=1)[0]
        result = gp_sync.get_reader_last_details(reader)   # None is fine (no pass recorded)
        assert result is None or result.readerUID
        with pytest.raises(GuardPointError, match="API_Key_Not_Found"):
            gp_sync.get_reader_last_details(api_key="NO_SUCH_KEY")

    def test_relay_readers(self, gp_sync):
        relays = gp_sync.get_relays()
        if relays:
            assert isinstance(gp_sync.get_relay_readers(relays[0]), list)

    def test_event_date_window(self, gp_sync):
        since = _now() - timedelta(days=7)
        events = gp_sync.get_access_events(limit=5, since=since)
        for e in events:
            assert datetime.fromisoformat(e.dateTime.replace('Z', '+00:00')) >= since
        windowed = gp_sync.get_access_events_count(since=since)
        assert 0 <= windowed <= gp_sync.get_access_events_count()


# --------------------------------------------------------------------------- actions, no side effects

@pytest.mark.integration
class TestActionsAgainstNonexistentTargets:
    @pytest.mark.parametrize("call", [
        lambda gp: gp.bypass_input(NOPE),
        lambda gp: gp.bypass_input(api_key="NO_SUCH_KEY"),
        lambda gp: gp.acknowledge_input(NOPE),
        lambda gp: gp.confirm_input(NOPE),
        lambda gp: gp.acknowledge_alarm(NOPE),
        lambda gp: gp.confirm_alarm(NOPE),
        lambda gp: gp.acknowledge_alarm_zone(NOPE),
        lambda gp: gp.activate_relays(NOPE, period=1),
        lambda gp: gp.activate_relay_by_api_key("NO_SUCH_KEY", 1),
        lambda gp: gp.deactivate_relays(NOPE),
        lambda gp: gp.return_relays_to_normal(NOPE),
        lambda gp: gp.initialize_controller(NOPE),
        lambda gp: gp.initialize_controller(api_key="NO_SUCH_KEY"),
        lambda gp: gp.start_site_polling(NOPE),
        lambda gp: gp.stop_site_polling(NOPE),
        lambda gp: gp.send_free_command(NOPE, "00"),
        lambda gp: gp.display_message("NO_SUCH_WORKSTATION", "test", "test"),
        lambda gp: gp.open_window("NO_SUCH_WORKSTATION", WindowType.DiagnosticView),
    ])
    def test_rejected_as_not_found(self, gp_sync, call):
        with pytest.raises(GuardPointError) as exc:
            call(gp_sync)
        msg = str(exc.value).lower()
        # A schema problem would be "The input was not valid." - we want a lookup failure.
        assert "not valid" not in msg
        assert any(s in msg for s in ("not_found", "not found", "cannot find", "wrong", "were found"))


# --------------------------------------------------------------------------- CRUD on own records

@pytest.mark.integration
@pytest.mark.destructive
class TestCrud:
    def test_department_lifecycle(self, gp_sync):
        dept = gp_sync.new_department(Department(name=f"pyGP test {uuid.uuid4().hex[:6]}", description="a"))
        assert dept.uid
        try:
            dept.description = "b"
            assert gp_sync.update_department(dept) is True
            assert gp_sync.get_department(dept.uid).description == "b"
        finally:
            assert gp_sync.delete_department(dept) is True
        with pytest.raises(GuardPointError):
            gp_sync.get_department(dept.uid)

    def test_scheduled_mag_lifecycle(self, gp_sync, throwaway_cardholder):
        sg = next((s for s in gp_sync.get_security_groups() if s.apiKey), None)
        if sg is None:
            pytest.skip("no security group with an API key")
        now = _now()
        uid = gp_sync.add_scheduled_mag(ScheduledMag(
            securityGroupAPIKey=sg.apiKey, cardholderUID=throwaway_cardholder.uid,
            fromDateValid=(now + timedelta(days=1)).isoformat(), toDateValid=(now + timedelta(days=2)).isoformat()))
        sm = gp_sync.get_scheduled_mag(uid)
        sm.toDateValid = (now + timedelta(days=3)).isoformat()
        assert gp_sync.update_scheduled_mag(sm) is True
        assert gp_sync.get_scheduled_mag(uid).toDateValid.startswith((now + timedelta(days=3)).strftime('%Y-%m-%d'))
        assert gp_sync.delete_scheduled_mag(uid) is True
        assert gp_sync.get_scheduled_mag(uid).status == "AskToDelete"   # queued for the controllers

    def test_scheduled_additional_reader_lifecycle(self, gp_sync, throwaway_cardholder):
        reader = gp_sync.get_readers(limit=1)[0]
        now = _now()
        uid = gp_sync.add_scheduled_additional_reader(ScheduledAdditionalReader(
            cardholderUID=throwaway_cardholder.uid, readerUID=reader.uid, wpuid=WP_ALWAYS,
            fromDateValid=(now + timedelta(days=1)).isoformat(), toDateValid=(now + timedelta(days=2)).isoformat()))
        assert uid
        listed = gp_sync.get_scheduled_additional_readers(cardholder=throwaway_cardholder)
        assert [s.uid for s in listed] == [uid]
        sar = gp_sync.get_scheduled_additional_reader(uid)
        sar.toDateValid = (now + timedelta(days=5)).isoformat()
        assert gp_sync.update_scheduled_additional_reader(sar) is True
        assert gp_sync.get_scheduled_additional_reader(uid).toDateValid.startswith(
            (now + timedelta(days=5)).strftime('%Y-%m-%d'))
        assert gp_sync.delete_scheduled_additional_reader(uid) is True
        assert gp_sync.get_scheduled_additional_reader(uid).status == "AskToDelete"
