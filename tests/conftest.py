"""Test configuration."""

import pytest
import pytest_asyncio

from fca_mcp.server.oauth.middleware import OAuthRegistry


@pytest.fixture
def oauth_registry():
    """Create OAuth registry."""
    return OAuthRegistry()


@pytest.fixture
def test_client_id():
    """Test client ID."""
    return "test_client"


@pytest.fixture
def test_client_secret():
    """Test client secret."""
    return "test_secret"


@pytest.fixture
def registered_client(oauth_registry, test_client_id, test_client_secret):
    """Register test client."""
    return oauth_registry.register_client(
        client_id=test_client_id,
        client_secret=test_client_secret,
        scopes=["read:firms", "search:firms"],
    )


@pytest.fixture
def test_token(oauth_registry, test_client_id, test_client_secret, registered_client):
    """Create test token."""
    return oauth_registry.create_token(test_client_id, test_client_secret)
