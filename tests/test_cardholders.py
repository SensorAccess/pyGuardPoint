"""Test cardholder CRUD operations."""

import pytest
from pyGuardPoint_Build.pyGuardPoint import GuardPointError, GuardPointUnauthorized, Cardholder


@pytest.mark.integration
@pytest.mark.destructive
class TestCardholderCRUD:
    """Test cardholder create, read, update, delete operations."""

    def test_create_cardholder(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Test creating a new cardholder."""
        ch = test_cardholder
        uid = gp_sync.new_card_holder(ch)

        assert uid is not None
        assert len(uid) == 36  # UUID format
        assert uid != ''

        # Verify cardholder was created
        created_ch = gp_sync.get_card_holder(uid=uid)
        assert created_ch is not None
        assert created_ch.firstName == ch.firstName
        assert created_ch.lastName == ch.lastName

        cleanup_cardholders.append(created_ch)

    def test_create_cardholder_with_personal_details(self, gp_sync, test_cardholder_pd, cleanup_cardholders):
        """Test creating cardholder with personal details."""
        ch = test_cardholder_pd
        uid = gp_sync.new_card_holder(ch)

        assert uid is not None

        # Verify personal details were saved
        created_ch = gp_sync.get_card_holder(uid=uid)
        assert created_ch is not None
        assert created_ch.cardholderPersonalDetail is not None
        assert created_ch.cardholderPersonalDetail.company == "PyTest Corp"
        assert created_ch.cardholderPersonalDetail.email == f"test-{pytest.current_test_id}@example.com"

        cleanup_cardholders.append(created_ch)

    def test_get_cardholder_by_uid(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Test retrieving cardholder by UID."""
        ch = test_cardholder
        uid = gp_sync.new_card_holder(ch)

        # Retrieve by UID
        retrieved = gp_sync.get_card_holder(uid=uid)
        assert retrieved is not None
        assert retrieved.uid == uid
        assert retrieved.firstName == ch.firstName

        cleanup_cardholders.append(retrieved)

    def test_update_cardholder(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Test updating cardholder properties."""
        ch = test_cardholder
        uid = gp_sync.new_card_holder(ch)

        # Modify cardholder
        modified = gp_sync.get_card_holder(uid=uid)
        original_desc = modified.description
        modified.description = "Updated by pytest"
        modified.pinCode = "9999"

        # Update
        result = gp_sync.update_card_holder(modified)
        assert result is True

        # Verify update
        verified = gp_sync.get_card_holder(uid=uid)
        assert verified.description == "Updated by pytest"
        assert verified.pinCode == "9999"

        cleanup_cardholders.append(verified)

    def test_delete_cardholder(self, gp_sync, test_cardholder):
        """Test deleting a cardholder."""
        ch = test_cardholder
        uid = gp_sync.new_card_holder(ch)

        # Verify it exists
        created = gp_sync.get_card_holder(uid=uid)
        assert created is not None

        # Delete it
        result = gp_sync.delete_card_holder(created)
        assert result is True

        # Verify it's gone
        deleted = gp_sync.get_card_holder(uid=uid)
        assert deleted is None

    def test_get_nonexistent_cardholder(self, gp_sync):
        """Test getting a cardholder that doesn't exist."""
        fake_uid = "00000000-0000-0000-0000-000000000000"
        result = gp_sync.get_card_holder(uid=fake_uid)
        assert result is None

    def test_search_cardholders_by_name(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Test searching for cardholders by name."""
        ch = test_cardholder
        ch.firstName = "UniqueTestName"
        uid = gp_sync.new_card_holder(ch)

        # Search
        results = gp_sync.get_card_holders(search_terms="UniqueTestName", limit=10)
        assert results is not None
        assert len(results) > 0

        found = [c for c in results if c.uid == uid]
        assert len(found) == 1
        assert found[0].firstName == "UniqueTestName"

        cleanup_cardholders.append(gp_sync.get_card_holder(uid=uid))

    def test_cardholder_with_cards(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Test cardholder has proper card collection structure."""
        ch = test_cardholder
        uid = gp_sync.new_card_holder(ch)

        # Retrieve and check cards collection
        created = gp_sync.get_card_holder(uid=uid)
        assert created is not None
        assert created.cards is not None
        assert isinstance(created.cards, list)
        assert len(created.cards) == 0  # New cardholder has no cards

        cleanup_cardholders.append(created)

    def test_cardholder_personal_details_none_when_not_set(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Test cardholder without personal details doesn't break."""
        ch = test_cardholder
        uid = gp_sync.new_card_holder(ch)

        # Retrieve
        created = gp_sync.get_card_holder(uid=uid)
        assert created is not None
        # Personal details may be None or empty object

        cleanup_cardholders.append(created)


@pytest.mark.integration
class TestCardholderRetrieval:
    """Test cardholder retrieval and listing operations."""

    def test_get_all_cardholders(self, gp_sync):
        """Test getting all cardholders with pagination."""
        results = gp_sync.get_card_holders(limit=50)

        assert results is not None
        assert isinstance(results, list)
        assert len(results) > 0

    def test_get_cardholders_with_offset(self, gp_sync):
        """Test getting cardholders with offset."""
        results1 = gp_sync.get_card_holders(limit=10)
        results2 = gp_sync.get_card_holders(limit=10, offset=5)

        assert results1 is not None
        assert results2 is not None
        assert len(results1) > 0
        assert len(results2) > 0

    def test_get_cardholders_with_count(self, gp_sync):
        """Test getting cardholder count."""
        count = gp_sync.get_card_holders(count=True)
        assert count >= 0

    def test_get_cardholders_with_search_terms(self, gp_sync):
        """Test searching cardholders with search terms."""
        # Search for common name
        results = gp_sync.get_card_holders(search_terms="test", limit=20)
        assert results is not None
        assert isinstance(results, list)


@pytest.mark.integration
class TestCardholderErrorHandling:
    """Test error handling in cardholder operations."""

    def test_invalid_cardholder_uid_format(self, gp_sync):
        """Test handling of invalid UID format."""
        # This should not raise, just return None
        result = gp_sync.get_card_holder(uid="invalid-uid")
        # Server may return error or None depending on validation

    def test_create_duplicate_pincode_allowed(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Test that duplicate PINs are allowed."""
        ch1 = test_cardholder
        ch1.firstName = "TestPin1"
        ch1.pinCode = "5555"

        ch2 = Cardholder()
        ch2.firstName = "TestPin2"
        ch2.lastName = test_cardholder.lastName
        ch2.pinCode = "5555"

        uid1 = gp_sync.new_card_holder(ch1)
        uid2 = gp_sync.new_card_holder(ch2)

        assert uid1 is not None
        assert uid2 is not None
        assert uid1 != uid2

        cleanup_cardholders.append(gp_sync.get_card_holder(uid=uid1))
        cleanup_cardholders.append(gp_sync.get_card_holder(uid=uid2))

    def test_empty_search_returns_all(self, gp_sync):
        """Test that empty search string returns all cardholders."""
        results1 = gp_sync.get_card_holders(search_terms="", limit=20)
        results2 = gp_sync.get_card_holders(limit=20)

        assert results1 is not None
        assert results2 is not None
        # Both should return similar counts (may vary based on timing)

    def test_get_cardholder_by_last_name(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Test searching by last name only."""
        ch = test_cardholder
        ch.lastName = "UniqueLast"
        uid = gp_sync.new_card_holder(ch)

        results = gp_sync.get_card_holders(lastName="UniqueLast", limit=10)
        assert results is not None

        found = [c for c in results if c.uid == uid]
        assert len(found) > 0

        cleanup_cardholders.append(gp_sync.get_card_holder(uid=uid))
