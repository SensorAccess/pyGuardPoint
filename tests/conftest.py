"""Pytest configuration and fixtures for pyGuardPoint tests."""

import os
import pytest
import sys
from dataclasses import dataclass

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import (
    GuardPoint, GuardPointAsyncIO, GuardPointError, GuardPointUnauthorized,
    Cardholder, Card, Area, CardholderPersonalDetail
)


@dataclass
class TestConfig:
    """Test server configuration."""
    host: str = os.getenv('GP_HOST', 'https://sensoraccess.duckdns.org')
    username: str = os.getenv('GP_USER', 'admin')
    password: str = os.getenv('GP_PASS', 'admin')
    tls_p12_file: str = os.getenv('GP_TLS_P12')
    tls_p12_pwd: str = os.getenv('GP_TLS_P12_PWD', '')
    timeout: int = 10


@pytest.fixture(scope='session')
def config():
    """Test server configuration."""
    return TestConfig()


@pytest.fixture
def gp_sync(config):
    """Sync GuardPoint client."""
    gp = GuardPoint(
        host=config.host,
        username=config.username,
        pwd=config.password,
        timeout=config.timeout
    )
    yield gp


@pytest.fixture
async def gp_async(config):
    """Async GuardPoint client."""
    gp = GuardPointAsyncIO(
        host=config.host,
        username=config.username,
        pwd=config.password,
        timeout=config.timeout
    )
    yield gp
    await gp.close()


@pytest.fixture
def test_cardholder():
    """Create a test cardholder object."""
    ch = Cardholder()
    ch.firstName = f"Test_Cardholder"
    ch.lastName = f"pytest_{pytest.current_test_id}"
    ch.pinCode = "1234"
    ch.description = "Created by pytest - will be deleted"
    return ch


@pytest.fixture
def test_cardholder_pd():
    """Create test cardholder with personal details."""
    ch = Cardholder()
    ch.firstName = "TestPD"
    ch.lastName = f"pytest_{pytest.current_test_id}"

    pd = CardholderPersonalDetail()
    pd.company = "PyTest Corp"
    pd.email = f"test-{pytest.current_test_id}@example.com"
    pd.department = "QA"

    ch.cardholderPersonalDetail = pd
    return ch


@pytest.fixture
def cleanup_cardholders(gp_sync):
    """Cleanup fixture - removes cardholders created during tests."""
    created_cardholders = []

    yield created_cardholders

    # Cleanup: delete all created cardholders
    for ch in created_cardholders:
        try:
            if gp_sync.delete_card_holder(ch):
                print(f"Deleted cardholder: {ch.firstName} {ch.lastName}")
        except GuardPointError as e:
            print(f"Failed to cleanup cardholder {ch.uid}: {e}")


@pytest.fixture
def cleanup_cards(gp_sync):
    """Cleanup fixture - removes cards created during tests."""
    created_cards = []

    yield created_cards

    # Cleanup: delete all created cards
    for card in created_cards:
        try:
            if gp_sync.delete_card(card):
                print(f"Deleted card: {card.cardCode}")
        except GuardPointError as e:
            print(f"Failed to cleanup card {card.uid}: {e}")


def pytest_configure(config):
    """Pytest configuration hook."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "integration: integration tests that require live server"
    )
    config.addinivalue_line(
        "markers", "async: async operation tests"
    )
    config.addinivalue_line(
        "markers", "slow: slow tests"
    )
    config.addinivalue_line(
        "markers", "destructive: tests that create/modify/delete data"
    )


@pytest.fixture(autouse=True)
def setup_test_id():
    """Setup unique test ID for each test."""
    pytest.current_test_id = os.urandom(4).hex()[:8]
