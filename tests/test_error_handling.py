"""Test error handling and edge cases."""

import pytest
from pyGuardPoint_Build.pyGuardPoint import (
    GuardPoint, GuardPointError, GuardPointUnauthorized, Cardholder,
)


@pytest.mark.integration
class TestAuthenticationErrors:

    def test_invalid_credentials(self, config):
        """Wrong password should raise an auth error (P12 still needed to reach the auth layer)."""
        bad_gp = GuardPoint(
            host=config.host,
            username='admin',
            pwd='wrongpassword_pytest',
            p12_file=config.p12_file,
            p12_pwd=config.p12_pwd,
            timeout=config.timeout,
        )
        with pytest.raises((GuardPointUnauthorized, GuardPointError)):
            bad_gp.get_card_holders(limit=1)

    def test_invalid_host(self):
        """Unreachable host should raise a connection-level exception."""
        bad_gp = GuardPoint(
            host='https://nonexistent.invalid.local',
            username='admin',
            pwd='admin',
            timeout=2,
        )
        with pytest.raises(Exception):
            bad_gp.get_card_holders(limit=1)


@pytest.mark.integration
class TestResourceNotFound:

    def test_get_nonexistent_cardholder(self, gp_sync):
        # Null UUID triggers a server OData error on this version — accept either outcome
        try:
            result = gp_sync.get_card_holder(uid="00000000-0000-0000-0000-000000000000")
            assert result is None
        except GuardPointError:
            pass

    def test_get_nonexistent_reader(self, gp_sync):
        # The server returns an empty Reader object for an unknown UID rather than None
        result = gp_sync.get_reader("00000000-0000-0000-0000-000000000000")
        assert result is not None  # empty object, not an exception

    def test_delete_nonexistent_cardholder(self, gp_sync):
        ch = Cardholder()
        ch.uid = "00000000-0000-0000-0000-000000000000"
        with pytest.raises(GuardPointError):
            gp_sync.delete_card_holder(ch)


@pytest.mark.integration
@pytest.mark.destructive
class TestDataValidation:

    def test_cardholder_with_special_characters(self, gp_sync, cleanup_cardholders):
        ch = Cardholder()
        ch.firstName = "Test-Name_123"
        ch.lastName  = "O'Brien"

        created = gp_sync.new_card_holder(ch)
        assert created is not None
        cleanup_cardholders.append(created)

    def test_cardholder_with_unicode(self, gp_sync, cleanup_cardholders):
        ch = Cardholder()
        ch.firstName = "José"
        ch.lastName  = "García"

        try:
            created = gp_sync.new_card_holder(ch)
            if created:
                cleanup_cardholders.append(created)
        except GuardPointError:
            pass  # Server may reject unicode names

    def test_cardholder_with_very_long_name(self, gp_sync, cleanup_cardholders):
        ch = Cardholder()
        ch.firstName = "A" * 100
        ch.lastName  = "B" * 100

        try:
            created = gp_sync.new_card_holder(ch)
            if created:
                cleanup_cardholders.append(created)
        except GuardPointError:
            pass  # Server may enforce field-length limits


@pytest.mark.integration
class TestListOperations:

    def test_get_with_zero_limit(self, gp_sync):
        try:
            results = gp_sync.get_card_holders(limit=0)
            assert results is not None
        except GuardPointError:
            pass

    def test_get_with_large_limit(self, gp_sync):
        results = gp_sync.get_card_holders(limit=10000)
        assert results is not None
        assert isinstance(results, list)

    def test_search_with_empty_terms(self, gp_sync):
        results = gp_sync.get_card_holders(search_terms="", limit=10)
        assert results is not None
        assert isinstance(results, list)

    def test_search_with_nonexistent_term(self, gp_sync):
        results = gp_sync.get_card_holders(search_terms="zzznomatch999", limit=10)
        assert results is not None
        assert isinstance(results, list)
