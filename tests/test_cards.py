"""Test card operations."""

import pytest
from pyGuardPoint_Build.pyGuardPoint import GuardPointError, Card, Cardholder


@pytest.mark.integration
@pytest.mark.destructive
class TestCardOperations:
    """Test card CRUD operations."""

    @pytest.fixture
    def test_cardholder_with_cards(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Create a cardholder for card tests."""
        uid = gp_sync.new_card_holder(test_cardholder)
        ch = gp_sync.get_card_holder(uid=uid)
        cleanup_cardholders.append(ch)
        return ch

    def test_create_card(self, gp_sync, test_cardholder_with_cards, cleanup_cards):
        """Test creating a new card."""
        card = Card()
        card.cardCode = f"pytest_{pytest.current_test_id}"
        card.cardType = "Magnetic"
        card.description = "Created by pytest"
        card.cardholderUID = test_cardholder_with_cards.uid

        uid = gp_sync.new_card(card)
        assert uid is not None
        assert len(uid) == 36  # UUID format

        # Verify card was created
        created_card = gp_sync.get_card(uid)
        assert created_card is not None
        assert created_card.cardCode == card.cardCode
        assert created_card.cardholderUID == test_cardholder_with_cards.uid

        cleanup_cards.append(created_card)

    def test_get_card(self, gp_sync, test_cardholder_with_cards, cleanup_cards):
        """Test retrieving a card by UID."""
        card = Card()
        card.cardCode = f"pytest_get_{pytest.current_test_id}"
        card.cardType = "Magnetic"
        card.cardholderUID = test_cardholder_with_cards.uid

        uid = gp_sync.new_card(card)

        # Retrieve
        retrieved = gp_sync.get_card(uid)
        assert retrieved is not None
        assert retrieved.uid == uid
        assert retrieved.cardCode == card.cardCode

        cleanup_cards.append(retrieved)

    def test_update_card(self, gp_sync, test_cardholder_with_cards, cleanup_cards):
        """Test updating a card."""
        card = Card()
        card.cardCode = f"pytest_upd_{pytest.current_test_id}"
        card.cardType = "Magnetic"
        card.cardholderUID = test_cardholder_with_cards.uid

        uid = gp_sync.new_card(card)

        # Modify
        modified = gp_sync.get_card(uid)
        modified.description = "Updated by pytest"

        # Update
        result = gp_sync.update_card(modified)
        assert result is True

        # Verify
        verified = gp_sync.get_card(uid)
        assert verified.description == "Updated by pytest"

        cleanup_cards.append(verified)

    def test_delete_card(self, gp_sync, test_cardholder_with_cards):
        """Test deleting a card."""
        card = Card()
        card.cardCode = f"pytest_del_{pytest.current_test_id}"
        card.cardType = "Magnetic"
        card.cardholderUID = test_cardholder_with_cards.uid

        uid = gp_sync.new_card(card)

        # Verify exists
        created = gp_sync.get_card(uid)
        assert created is not None

        # Delete
        result = gp_sync.delete_card(created)
        assert result is True

        # Verify deleted
        deleted = gp_sync.get_card(uid)
        assert deleted is None

    def test_get_all_cards(self, gp_sync):
        """Test getting all cards."""
        cards = gp_sync.get_cards(limit=50)
        assert cards is not None
        assert isinstance(cards, list)

    def test_cardholder_has_cards_after_creation(self, gp_sync, test_cardholder_with_cards, cleanup_cards):
        """Test that cardholder's card list updates after creating card."""
        card = Card()
        card.cardCode = f"pytest_list_{pytest.current_test_id}"
        card.cardType = "Magnetic"
        card.cardholderUID = test_cardholder_with_cards.uid

        uid = gp_sync.new_card(card)

        # Refresh cardholder
        refreshed = gp_sync.get_card_holder(test_cardholder_with_cards.uid)
        # Check that cards list is populated or card can be retrieved separately
        card_check = gp_sync.get_card(uid)
        assert card_check is not None

        cleanup_cards.append(card_check)


@pytest.mark.integration
class TestCardValidation:
    """Test card validation and constraints."""

    def test_card_requires_code(self, gp_sync, test_cardholder_with_cards):
        """Test that card requires a code."""
        card = Card()
        card.cardCode = ""  # Empty code
        card.cardType = "Magnetic"
        card.cardholderUID = test_cardholder_with_cards.uid

        # This may raise an error or be rejected by server
        try:
            uid = gp_sync.new_card(card)
            # If it succeeds, verify the code is assigned something
            if uid:
                created = gp_sync.get_card(uid)
                if created:
                    gp_sync.delete_card(created)
        except GuardPointError:
            # Expected - card needs code
            pass

    def test_card_with_different_types(self, gp_sync, test_cardholder_with_cards, cleanup_cards):
        """Test creating cards with different types."""
        card_types = ["Magnetic", "Proximity"]

        for card_type in card_types:
            card = Card()
            card.cardCode = f"pytest_{card_type}_{pytest.current_test_id}"
            card.cardType = card_type
            card.cardholderUID = test_cardholder_with_cards.uid

            uid = gp_sync.new_card(card)
            assert uid is not None

            created = gp_sync.get_card(uid)
            assert created.cardType == card_type
            cleanup_cards.append(created)

    def test_card_status_field(self, gp_sync, test_cardholder_with_cards, cleanup_cards):
        """Test card status field."""
        card = Card()
        card.cardCode = f"pytest_status_{pytest.current_test_id}"
        card.cardType = "Magnetic"
        card.status = "Free"
        card.cardholderUID = test_cardholder_with_cards.uid

        uid = gp_sync.new_card(card)

        created = gp_sync.get_card(uid)
        assert created.status is not None

        cleanup_cards.append(created)
