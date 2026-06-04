"""Pytest configuration and fixtures for pyGuardPoint tests."""

import os
import sys
import pytest

# Resolve path relative to this file so tests run correctly from any directory
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'pyGuardPoint_Build'))

from pyGuardPoint_Build.pyGuardPoint import (
    GuardPoint, GuardPointAsyncIO, GuardPointError, GuardPointUnauthorized,
    Cardholder, Card, CardholderPersonalDetail,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_default_p12 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MobileGuardDefault.p12')


class TestConfig:
    """Test server configuration — driven by environment variables."""
    host     = os.getenv('GP_HOST',    'https://sensoraccess.duckdns.org')
    username = os.getenv('GP_USER',    'admin')
    password = os.getenv('GP_PASS',    'admin')
    p12_file = os.getenv('GP_P12',     _default_p12)
    p12_pwd  = os.getenv('GP_P12_PWD', 'test')
    timeout  = 30


@pytest.fixture(scope='session')
def config():
    return TestConfig()


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

@pytest.fixture
def gp_sync(config):
    """Synchronous GuardPoint client."""
    gp = GuardPoint(
        host=config.host,
        username=config.username,
        pwd=config.password,
        p12_file=config.p12_file,
        p12_pwd=config.p12_pwd,
        timeout=config.timeout,
    )
    yield gp


@pytest.fixture
async def gp_async(config):
    """Asynchronous GuardPoint client."""
    gp = GuardPointAsyncIO(
        host=config.host,
        username=config.username,
        pwd=config.password,
        p12_file=config.p12_file,
        p12_pwd=config.p12_pwd,
        timeout=config.timeout,
    )
    yield gp
    await gp.close()


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

@pytest.fixture
def unique_id():
    """Eight-character hex ID unique to this test run."""
    return os.urandom(4).hex()


@pytest.fixture
def test_cardholder(unique_id):
    """Minimal cardholder object ready for creation."""
    ch = Cardholder()
    ch.firstName = f"PyTest_{unique_id}"
    ch.lastName  = "auto"
    ch.pinCode   = "1234"
    ch.description = "Created by pytest — will be deleted"
    return ch


@pytest.fixture
def test_cardholder_pd(unique_id):
    """Cardholder with personal details."""
    ch = Cardholder()
    ch.firstName = f"PyTestPD_{unique_id}"
    ch.lastName  = "auto"

    pd = CardholderPersonalDetail()
    pd.company    = "PyTest Corp"
    pd.email      = f"pytest-{unique_id}@example.com"
    pd.department = "QA"
    ch.cardholderPersonalDetail = pd
    return ch


# ---------------------------------------------------------------------------
# Cleanup helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def cleanup_cardholders(gp_sync):
    """Append created Cardholder objects; they are deleted after the test."""
    created = []
    yield created
    for ch in created:
        try:
            gp_sync.delete_card_holder(ch)
        except GuardPointError:
            pass


@pytest.fixture
def cleanup_cards(gp_sync):
    """Append created Card objects; they are deleted after the test."""
    created = []
    yield created
    for card in created:
        try:
            gp_sync.delete_card(card)
        except GuardPointError:
            pass


# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

def pytest_configure(config):
    config.addinivalue_line("markers", "integration: requires a live GuardPoint server")
    config.addinivalue_line("markers", "destructive: creates, modifies, or deletes data")
    config.addinivalue_line("markers", "slow: takes longer than a few seconds")
