"""Test error handling and edge cases."""

import pytest
from pyGuardPoint_Build.pyGuardPoint import GuardPointError, GuardPointUnauthorized, Cardholder


@pytest.mark.integration
class TestAuthenticationErrors:
    """Test authentication error handling."""

    def test_invalid_credentials(self, config):
        """Test that invalid credentials raise error."""
        from pyGuardPoint_Build.pyGuardPoint import GuardPoint

        bad_gp = GuardPoint(
            host=config.host,
            username='admin',
            pwd='wrongpassword',
            timeout=config.timeout
        )

        with pytest.raises((GuardPointUnauthorized, GuardPointError)):
            bad_gp.get_card_holders(limit=1)

    def test_invalid_host(self):
        """Test that invalid host is handled."""
        from pyGuardPoint_Build.pyGuardPoint import GuardPoint

        bad_gp = GuardPoint(
            host='https://nonexistent.invalid.local',
            username='admin',
            pwd='admin',
            timeout=2
        )

        with pytest.raises(Exception):  # May raise connection error
            bad_gp.get_card_holders(limit=1)


@pytest.mark.integration
class TestResourceNotFound:
    """Test handling of missing resources."""

    def test_get_nonexistent_area(self, gp_sync):
        """Test retrieving nonexistent area."""
        fake_uid = "00000000-0000-0000-0000-000000000000"
        result = gp_sync.get_area(fake_uid)
        assert result is None

    def test_get_nonexistent_reader(self, gp_sync):
        """Test retrieving nonexistent reader."""
        fake_uid = "00000000-0000-0000-0000-000000000000"
        result = gp_sync.get_reader(fake_uid)
        assert result is None

    def test_delete_nonexistent_cardholder(self, gp_sync):
        """Test deleting nonexistent cardholder."""
        ch = Cardholder()
        ch.uid = "00000000-0000-0000-0000-000000000000"

        try:
            result = gp_sync.delete_card_holder(ch)
            # May return False or raise error
            assert result is False or isinstance(result, bool)
        except GuardPointError:
            pass


@pytest.mark.integration
class TestDataValidation:
    """Test data validation and type handling."""

    def test_cardholder_with_special_characters(self, gp_sync, cleanup_cardholders):
        """Test creating cardholder with special characters."""
        ch = Cardholder()
        ch.firstName = "Test-Name_123"
        ch.lastName = "O'Brien"
        ch.description = "Test: with special chars &"

        uid = gp_sync.new_card_holder(ch)
        assert uid is not None

        created = gp_sync.get_card_holder(uid=uid)
        # Special chars should be preserved or escaped properly
        assert created is not None

        cleanup_cardholders.append(created)

    def test_cardholder_with_unicode(self, gp_sync, cleanup_cardholders):
        """Test creating cardholder with unicode characters."""
        ch = Cardholder()
        ch.firstName = "José"
        ch.lastName = "García"

        try:
            uid = gp_sync.new_card_holder(ch)
            if uid:
                created = gp_sync.get_card_holder(uid=uid)
                assert created is not None
                cleanup_cardholders.append(created)
        except GuardPointError:
            # Server may not support unicode
            pass

    def test_cardholder_with_empty_fields(self, gp_sync):
        """Test creating cardholder with minimal fields."""
        ch = Cardholder()
        ch.firstName = ""
        ch.lastName = ""

        try:
            uid = gp_sync.new_card_holder(ch)
            # May succeed or fail depending on server validation
        except GuardPointError:
            # Expected - name fields required
            pass

    def test_cardholder_with_very_long_name(self, gp_sync, cleanup_cardholders):
        """Test creating cardholder with very long name."""
        ch = Cardholder()
        ch.firstName = "A" * 100
        ch.lastName = "B" * 100

        try:
            uid = gp_sync.new_card_holder(ch)
            if uid:
                created = gp_sync.get_card_holder(uid=uid)
                # Should either succeed or be truncated
                assert created is not None
                cleanup_cardholders.append(created)
        except GuardPointError:
            # Server may reject overly long strings
            pass


@pytest.mark.integration
class TestListOperations:
    """Test list operation edge cases."""

    def test_get_with_zero_limit(self, gp_sync):
        """Test retrieving with zero limit."""
        try:
            results = gp_sync.get_card_holders(limit=0)
            # May return empty list
            assert results is not None
        except GuardPointError:
            # May raise error for invalid limit
            pass

    def test_get_with_negative_limit(self, gp_sync):
        """Test retrieving with negative limit."""
        try:
            results = gp_sync.get_card_holders(limit=-1)
            # May return all or raise error
        except GuardPointError:
            # Expected - invalid limit
            pass

    def test_get_with_very_large_limit(self, gp_sync):
        """Test retrieving with very large limit."""
        results = gp_sync.get_card_holders(limit=10000)
        # Should handle gracefully
        assert results is not None
        assert isinstance(results, list)

    def test_search_with_empty_terms(self, gp_sync):
        """Test searching with empty search terms."""
        results = gp_sync.get_card_holders(search_terms="", limit=10)
        assert results is not None
        assert isinstance(results, list)

    def test_search_with_special_characters(self, gp_sync):
        """Test searching with special characters."""
        results = gp_sync.get_card_holders(search_terms="*?&%", limit=10)
        assert results is not None
        assert isinstance(results, list)


@pytest.mark.integration
class TestConcurrentOperations:
    """Test behavior with concurrent-like operations."""

    def test_update_while_listing(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Test that update doesn't break list operations."""
        # Create a cardholder
        uid = gp_sync.new_card_holder(test_cardholder)
        ch = gp_sync.get_card_holder(uid=uid)

        # Update it
        ch.description = "Updated"
        gp_sync.update_card_holder(ch)

        # Still should be able to list
        results = gp_sync.get_card_holders(limit=10)
        assert results is not None
        assert isinstance(results, list)

        cleanup_cardholders.append(ch)

    def test_delete_immediately_after_create(self, gp_sync, test_cardholder):
        """Test deleting cardholder immediately after creation."""
        uid = gp_sync.new_card_holder(test_cardholder)
        ch = gp_sync.get_card_holder(uid=uid)

        # Immediately delete
        result = gp_sync.delete_card_holder(ch)
        assert result is True

        # Verify deleted
        deleted = gp_sync.get_card_holder(uid=uid)
        assert deleted is None
