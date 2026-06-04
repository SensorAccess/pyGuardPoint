"""Test API endpoints — read-only operations across all resource types."""

import pytest
from pyGuardPoint_Build.pyGuardPoint import GuardPointError, EventOrder


@pytest.mark.integration
class TestAreasAPI:

    def test_get_areas(self, gp_sync):
        areas = gp_sync.get_areas()
        assert areas is not None
        assert isinstance(areas, list)

    def test_area_has_required_fields(self, gp_sync):
        areas = gp_sync.get_areas()
        if areas:
            assert hasattr(areas[0], 'uid')
            assert hasattr(areas[0], 'name')


@pytest.mark.integration
class TestAccessEventsAPI:

    def test_get_access_events(self, gp_sync):
        events = gp_sync.get_access_events(limit=10)
        assert events is not None
        assert isinstance(events, list)

    def test_get_access_events_ordered(self, gp_sync):
        events = gp_sync.get_access_events(limit=5, orderby=EventOrder.DATETIME_DESC)
        assert events is not None
        assert isinstance(events, list)

    def test_get_access_events_with_offset(self, gp_sync):
        page1 = gp_sync.get_access_events(limit=5)
        page2 = gp_sync.get_access_events(limit=5, offset=2)
        assert page1 is not None
        assert page2 is not None

    def test_get_access_events_count(self, gp_sync):
        count = gp_sync.get_access_events_count()
        assert isinstance(count, int)
        assert count >= 0

    def test_get_alarm_events(self, gp_sync):
        events = gp_sync.get_alarm_events(limit=5)
        assert events is not None
        assert isinstance(events, list)

    def test_get_alarm_events_count(self, gp_sync):
        count = gp_sync.get_alarm_events_count()
        assert isinstance(count, int)
        assert count >= 0

    def test_get_audit_events_count(self, gp_sync):
        count = gp_sync.get_audit_events_count()
        assert isinstance(count, int)
        assert count >= 0

    def test_access_event_has_uid(self, gp_sync):
        events = gp_sync.get_access_events(limit=1)
        if events:
            assert hasattr(events[0], 'uid')


@pytest.mark.integration
class TestSecurityGroupsAPI:

    def test_get_security_groups(self, gp_sync):
        groups = gp_sync.get_security_groups()
        assert groups is not None
        assert isinstance(groups, list)

    def test_security_group_has_name(self, gp_sync):
        groups = gp_sync.get_security_groups()
        if groups:
            assert hasattr(groups[0], 'name')


@pytest.mark.integration
class TestReadersAPI:

    def test_get_readers(self, gp_sync):
        readers = gp_sync.get_readers()
        assert readers is not None
        assert isinstance(readers, list)

    def test_get_reader_by_uid(self, gp_sync):
        readers = gp_sync.get_readers()
        if readers:
            retrieved = gp_sync.get_reader(readers[0].uid)
            assert retrieved is not None


@pytest.mark.integration
class TestAlarmZonesAPI:

    def test_get_alarm_zones(self, gp_sync):
        zones = gp_sync.get_alarm_zones()
        assert zones is not None
        assert isinstance(zones, list)

    def test_get_alarm_zone_by_uid(self, gp_sync):
        zones = gp_sync.get_alarm_zones()
        if zones:
            retrieved = gp_sync.get_alarm_zone(zones[0].uid)
            assert retrieved is not None
            assert retrieved.uid == zones[0].uid

    def test_get_alarm_states(self, gp_sync):
        states = gp_sync.get_alarm_states()
        assert states is not None
        assert isinstance(states, list)


@pytest.mark.integration
class TestDepartmentsAPI:

    def test_get_departments(self, gp_sync):
        departments = gp_sync.get_departments()
        assert departments is not None
        assert isinstance(departments, list)

    def test_get_department_by_uid(self, gp_sync):
        departments = gp_sync.get_departments()
        if departments:
            retrieved = gp_sync.get_department(departments[0].uid)
            assert retrieved is not None


@pytest.mark.integration
class TestSitesAPI:

    def test_get_sites(self, gp_sync):
        sites = gp_sync.get_sites()
        assert sites is not None
        assert isinstance(sites, list)

    def test_get_site_by_uid(self, gp_sync):
        sites = gp_sync.get_sites()
        if sites:
            retrieved = gp_sync.get_site(site_uid=sites[0].uid)
            assert retrieved is not None
            assert retrieved.uid == sites[0].uid


@pytest.mark.integration
class TestAccessGroupsAPI:

    def test_get_access_groups(self, gp_sync):
        groups = gp_sync.get_access_groups()
        assert groups is not None
        assert isinstance(groups, list)


@pytest.mark.integration
class TestWeeklyProgramsAPI:

    def test_get_weekly_programs(self, gp_sync):
        programs = gp_sync.get_weekly_programs()
        assert programs is not None
        assert isinstance(programs, list)

    def test_get_weekly_program_by_uid(self, gp_sync):
        programs = gp_sync.get_weekly_programs()
        if programs:
            retrieved = gp_sync.get_weekly_program(programs[0].uid)
            assert retrieved is not None
            assert retrieved.uid == programs[0].uid


@pytest.mark.integration
class TestCardholderCountAPI:

    def test_get_cardholder_count(self, gp_sync):
        count = gp_sync.get_cardholder_count()
        assert isinstance(count, int)
        assert count >= 0

    def test_get_card_count(self, gp_sync):
        count = gp_sync.get_cards(count=True)
        assert isinstance(count, int)
        assert count >= 0


@pytest.mark.integration
class TestControllersAPI:

    def test_get_controllers(self, gp_sync):
        controllers = gp_sync.get_controllers()
        assert controllers is not None
        assert isinstance(controllers, list)


@pytest.mark.integration
class TestSystemInfoAPI:

    def test_get_infos(self, gp_sync):
        infos = gp_sync.get_infos()
        assert infos is not None

    def test_is_sigr_enabled(self, gp_sync):
        result = gp_sync.is_sigr_enabled()
        assert isinstance(result, bool)

    def test_get_manual_events(self, gp_sync):
        events = gp_sync.get_manual_events()
        assert events is not None
        assert isinstance(events, list)

    def test_get_cardholder_types(self, gp_sync):
        types = gp_sync.get_cardholder_types()
        assert types is not None
        assert isinstance(types, list)
