"""Test cardholder CRUD operations."""

import pytest
from pyGuardPoint_Build.pyGuardPoint import GuardPointError, Cardholder


@pytest.mark.integration
@pytest.mark.destructive
class TestCardholderCRUD:
    """Test cardholder create, read, update, delete operations."""

    def test_create_cardholder(self, gp_sync, test_cardholder, cleanup_cardholders):
        ch = test_cardholder
        created = gp_sync.new_card_holder(ch)

        assert created is not None
        assert created.uid is not None
        assert len(created.uid) == 36
        assert created.firstName == ch.firstName
        assert created.lastName == ch.lastName

        cleanup_cardholders.append(created)

    def test_create_cardholder_with_personal_details(self, gp_sync, test_cardholder_pd, cleanup_cardholders):
        ch = test_cardholder_pd
        created = gp_sync.new_card_holder(ch)

        assert created is not None

        fetched = gp_sync.get_card_holder(uid=created.uid)
        assert fetched is not None
        assert fetched.cardholderPersonalDetail is not None
        assert fetched.cardholderPersonalDetail.company == "PyTest Corp"

        cleanup_cardholders.append(created)

    def test_get_cardholder_by_uid(self, gp_sync, test_cardholder, cleanup_cardholders):
        created = gp_sync.new_card_holder(test_cardholder)

        retrieved = gp_sync.get_card_holder(uid=created.uid)
        assert retrieved is not None
        assert retrieved.uid == created.uid
        assert retrieved.firstName == test_cardholder.firstName

        cleanup_cardholders.append(created)

    def test_update_cardholder(self, gp_sync, test_cardholder, cleanup_cardholders):
        created = gp_sync.new_card_holder(test_cardholder)

        fetched = gp_sync.get_card_holder(uid=created.uid)
        fetched.description = "Updated by pytest"
        fetched.pinCode = "9999"

        result = gp_sync.update_card_holder(fetched)
        assert result is True

        verified = gp_sync.get_card_holder(uid=created.uid)
        assert verified.description == "Updated by pytest"

        cleanup_cardholders.append(created)

    def test_delete_cardholder(self, gp_sync, test_cardholder):
        created = gp_sync.new_card_holder(test_cardholder)
        assert created is not None

        result = gp_sync.delete_card_holder(created)
        assert result is True
        # Note: server soft-deletes, so a subsequent fetch may still return
        # the record briefly — we trust the HTTP 204 response

    def test_get_nonexistent_cardholder(self, gp_sync):
        # Server may return None or raise an OData error for non-existent UIDs
        try:
            result = gp_sync.get_card_holder(uid="00000000-0000-0000-0000-000000000000")
            assert result is None
        except GuardPointError:
            pass  # Also acceptable — server rejects the nil UUID with an OData error

    def test_search_cardholders_by_name(self, gp_sync, test_cardholder, cleanup_cardholders):
        test_cardholder.firstName = "UniqueSearchName"
        created = gp_sync.new_card_holder(test_cardholder)

        results = gp_sync.get_card_holders(search_terms="UniqueSearchName", limit=10)
        assert results is not None
        assert any(c.uid == created.uid for c in results)

        cleanup_cardholders.append(created)

    def test_cardholder_has_empty_cards_on_creation(self, gp_sync, test_cardholder, cleanup_cardholders):
        created = gp_sync.new_card_holder(test_cardholder)

        fetched = gp_sync.get_card_holder(uid=created.uid)
        assert fetched is not None
        assert isinstance(fetched.cards, list)
        assert len(fetched.cards) == 0

        cleanup_cardholders.append(created)

    def test_create_duplicate_pincode_allowed(self, gp_sync, test_cardholder, unique_id, cleanup_cardholders):
        test_cardholder.pinCode = "5555"
        ch2 = Cardholder()
        ch2.firstName = f"PyTestPin2_{unique_id}"
        ch2.lastName  = "auto"
        ch2.pinCode   = "5555"

        created1 = gp_sync.new_card_holder(test_cardholder)
        created2 = gp_sync.new_card_holder(ch2)

        assert created1 is not None
        assert created2 is not None
        assert created1.uid != created2.uid

        cleanup_cardholders.extend([created1, created2])

    def test_get_cardholder_by_last_name(self, gp_sync, test_cardholder, cleanup_cardholders):
        test_cardholder.lastName = "UniqueLastName"
        created = gp_sync.new_card_holder(test_cardholder)

        results = gp_sync.get_card_holders(lastName="UniqueLastName", limit=10)
        assert results is not None
        assert any(c.uid == created.uid for c in results)

        cleanup_cardholders.append(created)


@pytest.mark.integration
@pytest.mark.destructive
class TestSearchMatchAll:
    """search_match_all narrows a multi-word search_terms to an AND across words
    (each word can still match any field), instead of the default OR-across-everything."""

    @pytest.fixture
    def match_all_cardholders(self, gp_sync, unique_id, cleanup_cardholders):
        """Two cardholders sharing one search token but differing on the other -
        `full` contains both search words, `partial` contains only one."""
        full = Cardholder()
        full.firstName = f"MatchAll_{unique_id}_John"
        full.lastName = f"MatchAll_{unique_id}_Smith"
        full.description = "Created by pytest — will be deleted"

        partial = Cardholder()
        partial.firstName = f"MatchAll_{unique_id}_John"
        partial.lastName = "Different"
        partial.description = "Created by pytest — will be deleted"

        created_full = gp_sync.new_card_holder(full)
        created_partial = gp_sync.new_card_holder(partial)
        cleanup_cardholders.append(created_full)
        cleanup_cardholders.append(created_partial)

        return created_full, created_partial

    def test_or_mode_matches_either_word(self, gp_sync, unique_id, match_all_cardholders):
        created_full, created_partial = match_all_cardholders
        search_terms = f"MatchAll_{unique_id}_John MatchAll_{unique_id}_Smith"

        results = gp_sync.get_card_holders(search_terms=search_terms, limit=50)
        result_uids = {c.uid for c in results}

        assert created_full.uid in result_uids
        assert created_partial.uid in result_uids

    def test_match_all_excludes_partial_matches(self, gp_sync, unique_id, match_all_cardholders):
        created_full, created_partial = match_all_cardholders
        search_terms = f"MatchAll_{unique_id}_John MatchAll_{unique_id}_Smith"

        results = gp_sync.get_card_holders(search_terms=search_terms, search_match_all=True, limit=50)
        result_uids = {c.uid for c in results}

        assert created_full.uid in result_uids
        assert created_partial.uid not in result_uids

    def test_match_all_single_word_matches_either_record(self, gp_sync, unique_id, match_all_cardholders):
        # With only one search word there's nothing to AND against - both cardholders
        # share it, so match_all behaves the same as the default here.
        created_full, created_partial = match_all_cardholders

        results = gp_sync.get_card_holders(search_terms=f"MatchAll_{unique_id}_John",
                                           search_match_all=True, limit=50)
        result_uids = {c.uid for c in results}

        assert created_full.uid in result_uids
        assert created_partial.uid in result_uids


@pytest.mark.integration
class TestCardholderRetrieval:
    """Test cardholder listing and search."""

    def test_get_cardholders(self, gp_sync):
        results = gp_sync.get_card_holders(limit=10)
        assert results is not None
        assert isinstance(results, list)

    def test_get_cardholders_with_offset(self, gp_sync):
        page1 = gp_sync.get_card_holders(limit=10)
        page2 = gp_sync.get_card_holders(limit=10, offset=5)
        assert page1 is not None
        assert page2 is not None

    def test_get_cardholder_count(self, gp_sync):
        count = gp_sync.get_cardholder_count()
        assert isinstance(count, int)
        assert count >= 0

    def test_search_with_terms(self, gp_sync):
        results = gp_sync.get_card_holders(search_terms="test", limit=10)
        assert results is not None
        assert isinstance(results, list)

    def test_search_with_empty_terms(self, gp_sync):
        results = gp_sync.get_card_holders(search_terms="", limit=10)
        assert results is not None
        assert isinstance(results, list)


@pytest.mark.integration
class TestCardholderErrorHandling:
    """Error handling edge cases."""

    def test_invalid_uid_format(self, gp_sync):
        with pytest.raises(Exception):
            gp_sync.get_card_holder(uid="not-a-valid-uuid")

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
            pass  # Server may not support unicode names
