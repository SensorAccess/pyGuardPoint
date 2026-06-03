"""Test various API endpoints."""

import pytest
from pyGuardPoint_Build.pyGuardPoint import GuardPointError


@pytest.mark.integration
class TestAreasAPI:
    """Test area-related API operations."""

    def test_get_areas(self, gp_sync):
        """Test retrieving all areas."""
        areas = gp_sync.get_areas(limit=50)
        assert areas is not None
        assert isinstance(areas, list)

    def test_get_area_by_uid(self, gp_sync):
        """Test retrieving area by UID."""
        areas = gp_sync.get_areas(limit=5)
        if areas and len(areas) > 0:
            area = areas[0]
            retrieved = gp_sync.get_area(area.uid)
            assert retrieved is not None
            assert retrieved.uid == area.uid

    def test_area_has_required_fields(self, gp_sync):
        """Test that areas have expected fields."""
        areas = gp_sync.get_areas(limit=1)
        if areas and len(areas) > 0:
            area = areas[0]
            assert hasattr(area, 'uid')
            assert hasattr(area, 'name')


@pytest.mark.integration
class TestAccessEventsAPI:
    """Test access event operations."""

    def test_get_access_events(self, gp_sync):
        """Test retrieving access events."""
        events = gp_sync.get_access_events(limit=20)
        assert events is not None
        assert isinstance(events, list)

    def test_get_access_events_with_offset(self, gp_sync):
        """Test retrieving access events with pagination."""
        events1 = gp_sync.get_access_events(limit=10)
        events2 = gp_sync.get_access_events(limit=10, offset=5)

        assert events1 is not None
        assert events2 is not None

    def test_get_alarm_events(self, gp_sync):
        """Test retrieving alarm events."""
        events = gp_sync.get_alarm_events(limit=10)
        assert events is not None
        assert isinstance(events, list)

    def test_access_event_has_fields(self, gp_sync):
        """Test that events have expected fields."""
        events = gp_sync.get_access_events(limit=1)
        if events and len(events) > 0:
            event = events[0]
            assert hasattr(event, 'uid')
            # Events may have timestamp fields


@pytest.mark.integration
class TestSecurityGroupsAPI:
    """Test security group operations."""

    def test_get_security_groups(self, gp_sync):
        """Test retrieving security groups."""
        groups = gp_sync.get_security_groups(limit=50)
        assert groups is not None
        assert isinstance(groups, list)

    def test_get_security_group_by_uid(self, gp_sync):
        """Test retrieving security group by UID."""
        groups = gp_sync.get_security_groups(limit=5)
        if groups and len(groups) > 0:
            group = groups[0]
            retrieved = gp_sync.get_security_group(group.uid)
            assert retrieved is not None
            assert retrieved.uid == group.uid


@pytest.mark.integration
class TestReadersAPI:
    """Test reader operations."""

    def test_get_readers(self, gp_sync):
        """Test retrieving all readers."""
        readers = gp_sync.get_readers(limit=50)
        assert readers is not None
        assert isinstance(readers, list)

    def test_get_reader_by_uid(self, gp_sync):
        """Test retrieving reader by UID."""
        readers = gp_sync.get_readers(limit=5)
        if readers and len(readers) > 0:
            reader = readers[0]
            retrieved = gp_sync.get_reader(reader.uid)
            assert retrieved is not None
            assert retrieved.uid == reader.uid


@pytest.mark.integration
class TestAlarmZonesAPI:
    """Test alarm zone operations."""

    def test_get_alarm_zones(self, gp_sync):
        """Test retrieving alarm zones."""
        zones = gp_sync.get_alarm_zones(limit=50)
        assert zones is not None
        assert isinstance(zones, list)

    def test_get_alarm_zone_by_uid(self, gp_sync):
        """Test retrieving alarm zone by UID."""
        zones = gp_sync.get_alarm_zones(limit=5)
        if zones and len(zones) > 0:
            zone = zones[0]
            retrieved = gp_sync.get_alarm_zone(zone.uid)
            assert retrieved is not None
            assert retrieved.uid == zone.uid

    def test_get_alarm_states(self, gp_sync):
        """Test retrieving alarm states."""
        states = gp_sync.get_alarm_states(limit=20)
        assert states is not None
        assert isinstance(states, list)


@pytest.mark.integration
class TestDepartmentsAPI:
    """Test department operations."""

    def test_get_departments(self, gp_sync):
        """Test retrieving departments."""
        departments = gp_sync.get_departments(limit=50)
        assert departments is not None
        assert isinstance(departments, list)

    def test_get_department_by_uid(self, gp_sync):
        """Test retrieving department by UID."""
        departments = gp_sync.get_departments(limit=5)
        if departments and len(departments) > 0:
            dept = departments[0]
            retrieved = gp_sync.get_department(dept.uid)
            assert retrieved is not None
            assert retrieved.uid == dept.uid


@pytest.mark.integration
class TestSitesAPI:
    """Test site operations."""

    def test_get_sites(self, gp_sync):
        """Test retrieving sites."""
        sites = gp_sync.get_sites(limit=50)
        assert sites is not None
        assert isinstance(sites, list)

    def test_get_site_by_uid(self, gp_sync):
        """Test retrieving site by UID."""
        sites = gp_sync.get_sites(limit=5)
        if sites and len(sites) > 0:
            site = sites[0]
            retrieved = gp_sync.get_site(site.uid)
            assert retrieved is not None
            assert retrieved.uid == site.uid


@pytest.mark.integration
class TestAccessGroupsAPI:
    """Test access group operations."""

    def test_get_access_groups(self, gp_sync):
        """Test retrieving access groups."""
        groups = gp_sync.get_access_groups(limit=50)
        assert groups is not None
        assert isinstance(groups, list)

    def test_get_access_group_by_uid(self, gp_sync):
        """Test retrieving access group by UID."""
        groups = gp_sync.get_access_groups(limit=5)
        if groups and len(groups) > 0:
            group = groups[0]
            retrieved = gp_sync.get_access_group(group.uid)
            assert retrieved is not None
            assert retrieved.uid == group.uid


@pytest.mark.integration
class TestCardholdersCountAPI:
    """Test cardholder counting operations."""

    def test_get_cardholders_count(self, gp_sync):
        """Test getting cardholder count."""
        count = gp_sync.get_card_holders(count=True)
        assert isinstance(count, int)
        assert count > 0

    def test_cardholder_count_type(self, gp_sync):
        """Test that count returns integer."""
        count = gp_sync.get_card_holders(count=True)
        assert type(count) in (int, float)


@pytest.mark.integration
class TestWeeklyProgramsAPI:
    """Test weekly program operations."""

    def test_get_weekly_programs(self, gp_sync):
        """Test retrieving weekly programs."""
        programs = gp_sync.get_weekly_programs(limit=50)
        assert programs is not None
        assert isinstance(programs, list)

    def test_get_weekly_program_by_uid(self, gp_sync):
        """Test retrieving weekly program by UID."""
        programs = gp_sync.get_weekly_programs(limit=5)
        if programs and len(programs) > 0:
            program = programs[0]
            retrieved = gp_sync.get_weekly_program(program.uid)
            assert retrieved is not None
            assert retrieved.uid == program.uid
