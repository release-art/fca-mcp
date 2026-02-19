from __future__ import annotations

"""Tests for OAuth middleware."""


def test_register_client(oauth_registry, test_client_id, test_client_secret):
    """Test client registration."""
    client = oauth_registry.register_client(
        client_id=test_client_id,
        client_secret=test_client_secret,
        scopes=["read:firms"],
    )

    assert client.client_id == test_client_id
    assert client.client_secret == test_client_secret
    assert "read:firms" in client.scopes
    assert client.active


def test_create_token(oauth_registry, registered_client, test_client_id, test_client_secret):
    """Test token creation."""
    token = oauth_registry.create_token(test_client_id, test_client_secret)

    assert token is not None
    assert token.client_id == test_client_id
    assert not token.is_expired()


def test_create_token_invalid_credentials(oauth_registry, registered_client, test_client_id):
    """Test token creation with invalid credentials."""
    token = oauth_registry.create_token(test_client_id, "wrong_secret")
    assert token is None


def test_validate_token(oauth_registry, test_token):
    """Test token validation."""
    validated = oauth_registry.validate_token(test_token.token)

    assert validated is not None
    assert validated.client_id == test_token.client_id


def test_validate_invalid_token(oauth_registry):
    """Test validation of invalid token."""
    validated = oauth_registry.validate_token("invalid_token")
    assert validated is None


def test_revoke_token(oauth_registry, test_token):
    """Test token revocation."""
    result = oauth_registry.revoke_token(test_token.token)
    assert result is True

    validated = oauth_registry.validate_token(test_token.token)
    assert validated is None


def test_token_has_scope(test_token):
    """Test token scope checking."""
    assert test_token.has_scope("read:firms")
    assert not test_token.has_scope("write:firms")
