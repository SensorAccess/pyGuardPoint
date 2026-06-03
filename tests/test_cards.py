"""Test card operations."""

import os
import pytest
from pyGuardPoint_Build.pyGuardPoint import GuardPointError, Card


def _hex_code():
    """Return a fresh 8-char uppercase hex card code (hex chars only — server requirement)."""
    return os.urandom(4).hex().upper()


@pytest.mark.integration
@pytest.mark.destructive
class TestCardOperations:
    """Test card CRUD operations."""

    @pytest.fixture
    def cardholder(self, gp_sync, test_cardholder, cleanup_cardholders):
        """Create a cardholder to attach cards to."""
        created = gp_sync.new_card_holder(test_cardholder)
        cleanup_cardholders.append(created)
        return created

    def test_create_card(self, gp_sync, cardholder, cleanup_cards):
        card = Card()
        card.cardCode      = _hex_code()
        card.cardType      = "Magnetic"
        card.description   = "Created by pytest"
        card.cardholderUID = cardholder.uid

        created = gp_sync.new_card(card)
        assert created is not None
        assert created.uid is not None
        assert len(created.uid) == 36
        assert created.cardCode == card.cardCode

        cleanup_cards.append(created)

    def test_get_card(self, gp_sync, cardholder, cleanup_cards):
        card = Card()
        card.cardCode      = _hex_code()
        card.cardType      = "Magnetic"
        card.cardholderUID = cardholder.uid

        created = gp_sync.new_card(card)

        retrieved = gp_sync.get_card(created.uid)
        assert retrieved is not None
        assert retrieved.uid == created.uid
        assert retrieved.cardCode == card.cardCode

        cleanup_cards.append(created)

    def test_update_card(self, gp_sync, cardholder, cleanup_cards):
        card = Card()
        card.cardCode      = _hex_code()
        card.cardType      = "Magnetic"
        card.cardholderUID = cardholder.uid

        created = gp_sync.new_card(card)
        created.description = "Updated by pytest"

        result = gp_sync.update_card(created)
        assert result is True

        verified = gp_sync.get_card(created.uid)
        assert verified.description == "Updated by pytest"

        cleanup_cards.append(created)

    def test_delete_card(self, gp_sync, cardholder):
        card = Card()
        card.cardCode      = _hex_code()
        card.cardType      = "Magnetic"
        card.cardholderUID = cardholder.uid

        created = gp_sync.new_card(card)
        assert created is not None

        result = gp_sync.delete_card(created)
        assert result is True

    def test_get_all_cards(self, gp_sync):
        cards = gp_sync.get_cards(limit=50)
        assert cards is not None
        assert isinstance(cards, list)

    def test_get_card_count(self, gp_sync):
        count = gp_sync.get_cards(count=True)
        assert isinstance(count, int)
        assert count >= 0

    def test_cardholder_card_linked(self, gp_sync, cardholder, cleanup_cards):
        card = Card()
        card.cardCode      = _hex_code()
        card.cardType      = "Magnetic"
        card.cardholderUID = cardholder.uid

        created = gp_sync.new_card(card)
        fetched = gp_sync.get_card(created.uid)
        assert fetched.cardholderUID == cardholder.uid

        cleanup_cards.append(created)


@pytest.mark.integration
class TestCardValidation:
    """Card field validation."""

    @pytest.fixture
    def cardholder(self, gp_sync, test_cardholder, cleanup_cardholders):
        created = gp_sync.new_card_holder(test_cardholder)
        cleanup_cardholders.append(created)
        return created

    def test_card_type_magnetic(self, gp_sync, cardholder, cleanup_cards):
        card = Card()
        card.cardCode      = _hex_code()
        card.cardType      = "Magnetic"
        card.cardholderUID = cardholder.uid

        created = gp_sync.new_card(card)
        assert created is not None
        assert created.cardType == "Magnetic"
        cleanup_cards.append(created)

    def test_card_status_field(self, gp_sync, cardholder, cleanup_cards):
        card = Card()
        card.cardCode      = _hex_code()
        card.cardType      = "Magnetic"
        card.status        = "Free"
        card.cardholderUID = cardholder.uid

        created = gp_sync.new_card(card)
        assert created.status is not None
        cleanup_cards.append(created)
