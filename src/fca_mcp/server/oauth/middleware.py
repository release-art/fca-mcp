"""OAuth2 client authentication."""

from datetime import datetime, timedelta

from pydantic import BaseModel, Field


class OAuthClient(BaseModel):
    """OAuth client registration."""

    client_id: str = Field(..., description="Client identifier")
    client_secret: str = Field(..., description="Client secret")
    scopes: list[str] = Field(default_factory=list, description="Allowed scopes")
    active: bool = Field(default=True, description="Whether client is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OAuthToken(BaseModel):
    """OAuth bearer token."""

    token: str = Field(..., description="Token string")
    client_id: str = Field(..., description="Associated client ID")
    scopes: list[str] = Field(default_factory=list)
    expires_at: datetime = Field(..., description="Token expiration time")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() >= self.expires_at

    def has_scope(self, scope: str) -> bool:
        """Check if token has specific scope."""
        return scope in self.scopes


class OAuthRegistry:
    """Registry for OAuth clients and tokens."""

    def __init__(self):
        """Initialize registry."""
        self.clients: dict[str, OAuthClient] = {}
        self.tokens: dict[str, OAuthToken] = {}

    def register_client(
        self,
        client_id: str,
        client_secret: str,
        scopes: list[str] | None = None,
    ) -> OAuthClient:
        """Register new client.

        Args:
            client_id: Client identifier
            client_secret: Client secret
            scopes: Allowed scopes

        Returns:
            Registered client
        """
        client = OAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes or ["read:firms", "search:firms"],
        )
        self.clients[client_id] = client
        return client

    def create_token(
        self,
        client_id: str,
        client_secret: str,
        ttl_hours: int = 24,
    ) -> OAuthToken | None:
        """Create token for client.

        Args:
            client_id: Client identifier
            client_secret: Client secret
            ttl_hours: Token time-to-live in hours

        Returns:
            Token if credentials valid, None otherwise
        """
        client = self.clients.get(client_id)
        if not client or not client.active:
            return None

        if client.client_secret != client_secret:
            return None

        token_str = f"mcp_token_{client_id}_{datetime.utcnow().timestamp()}"
        token = OAuthToken(
            token=token_str,
            client_id=client_id,
            scopes=client.scopes,
            expires_at=datetime.utcnow() + timedelta(hours=ttl_hours),
        )

        self.tokens[token_str] = token
        return token

    def validate_token(self, token_str: str) -> OAuthToken | None:
        """Validate bearer token.

        Args:
            token_str: Token string

        Returns:
            Valid token or None
        """
        token = self.tokens.get(token_str)
        if not token or token.is_expired():
            return None

        client = self.clients.get(token.client_id)
        if not client or not client.active:
            return None

        return token

    def revoke_token(self, token_str: str) -> bool:
        """Revoke token.

        Args:
            token_str: Token to revoke

        Returns:
            True if revoked
        """
        if token_str in self.tokens:
            del self.tokens[token_str]
            return True
        return False


class OAuthMiddleware:
    """OAuth authentication middleware."""

    def __init__(self, registry: OAuthRegistry):
        """Initialize middleware.

        Args:
            registry: OAuth registry
        """
        self.registry = registry

    async def authenticate(self, authorization: str | None) -> tuple[bool, str, OAuthToken | None]:
        """Authenticate request.

        Args:
            authorization: Authorization header value

        Returns:
            Tuple of (success, message, token)
        """
        if not authorization:
            return False, "Missing authorization header", None

        if not authorization.startswith("Bearer "):
            return False, "Invalid authorization format", None

        token_str = authorization[7:]
        token = self.registry.validate_token(token_str)

        if not token:
            return False, "Invalid or expired token", None

        return True, "Authenticated", token
