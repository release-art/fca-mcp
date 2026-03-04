"""Global settings for the fca-mcp project."""

from __future__ import annotations

import base64
import enum
import functools
from typing import Annotated, Literal

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


@enum.unique
class AzureCredentialType(enum.StrEnum):
    """Types of Azure credentials supported for authentication."""

    NONE = "none"
    DEFAULT = "default"


class AzureSettings(BaseSettings):
    """Azure storage configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="AZURE_",
        extra="forbid",
    )

    credential: Annotated[
        AzureCredentialType,
        Field(
            description="Azure credential type to use for authentication",
        ),
    ]

    storage_connection_string: Annotated[
        str,
        Field(
            description="Azure Storage connection string",
        ),
    ]


class Auth0Settings(BaseSettings):
    """Auth0 OAuth configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="AUTH0_",
        extra="forbid",
    )

    domain: Annotated[
        str,
        Field(
            ...,
            description="Auth0 domain (e.g., 'your-tenant.auth0.com')",
        ),
    ]
    audience: Annotated[
        str,
        Field(
            ...,
            description="Auth0 API audience identifier",
        ),
    ]
    client_id: Annotated[
        str,
        Field(
            description="Auth0 client ID (optional, for client credentials flow)",
        ),
    ]
    client_secret: Annotated[
        str,
        Field(
            description="Auth0 client secret (optional, for client credentials flow)",
        ),
    ]
    jwt_signing_key: Annotated[
        str,
        Field(
            description="JWT signing key for validating tokens (optional)",
        ),
    ]
    storage_encryption_key: Annotated[
        str,
        Field(
            description="Encryption key for securely storing sensitive data (optional)",
        ),
    ]

    @field_validator("storage_encryption_key")
    @classmethod
    def validate_storage_encryption_key(cls, v: str) -> str:
        """Validate that storage_encryption_key is 32 url-safe base64-encoded bytes."""
        try:
            decoded = base64.urlsafe_b64decode(v)
            if len(decoded) != 32:
                raise ValueError(f"must be 32 bytes when decoded, got {len(decoded)} bytes")
        except Exception as e:
            raise ValueError(f"must be 32 url-safe base64-encoded bytes: {e}") from e
        return v


class FcaApiSettings(BaseSettings):
    """FCA API credentials and configuration."""

    model_config = SettingsConfigDict(
        env_prefix="FCA_API_",
        extra="forbid",
    )

    username: Annotated[
        str,
        Field(
            ...,
            description="FCA API username/email",
        ),
    ]
    key: Annotated[
        str,
        Field(
            ...,
            description="FCA API key",
        ),
    ]
    base_url: Annotated[
        HttpUrl | None,
        Field(
            default=None,
            description="FCA API base URL (optional override)",
        ),
    ]
    timeout: Annotated[
        float,
        Field(
            default=30.0,
            gt=0,
            description="API request timeout in seconds",
        ),
    ]
    max_retries: Annotated[
        int,
        Field(
            default=3,
            ge=0,
            description="Maximum number of retries for failed requests",
        ),
    ]


class ServerSettings(BaseSettings):
    """Server configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="SERVER_",
        extra="forbid",
    )

    host: Annotated[
        str,
        Field(
            default="0.0.0.0",
            description="Server host address",
        ),
    ]
    port: Annotated[
        int,
        Field(
            default=8000,
            ge=1,
            le=65535,
            description="Server port number",
        ),
    ]
    base_url: Annotated[
        HttpUrl,
        Field(
            ...,
            description="Full base URL",
        ),
    ]
    workers: Annotated[
        int,
        Field(
            default=1,
            ge=1,
            description="Number of worker processes",
        ),
    ]


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        extra="forbid",
    )

    level: Annotated[
        Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        Field(
            default="INFO",
            description="Logging level",
        ),
    ]
    format: Annotated[
        Literal["json", "text"],
        Field(
            default="text",
            description="Log output format",
        ),
    ]
    file: Annotated[
        str | None,
        Field(
            default=None,
            description="Log file path (None = stdout only)",
        ),
    ]


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(
        extra="forbid",
        case_sensitive=False,
    )

    # Environment and deployment
    environment: Annotated[
        Literal["development", "staging", "production"],
        Field(
            default="development",
            description="Application environment",
        ),
    ]
    debug: Annotated[
        bool,
        Field(
            default=False,
            description="Enable debug mode",
        ),
    ]

    # Nested settings
    azure: Annotated[AzureSettings, Field(default_factory=AzureSettings)]
    auth0: Annotated[Auth0Settings, Field(default_factory=Auth0Settings)]
    fca_api: Annotated[FcaApiSettings, Field(default_factory=FcaApiSettings)]
    server: Annotated[ServerSettings, Field(default_factory=ServerSettings)]
    logging: Annotated[LoggingSettings, Field(default_factory=LoggingSettings)]

    # Additional top-level settings
    cors_origins: Annotated[
        list[str],
        Field(
            default_factory=lambda: ["*"],
            description="Allowed CORS origins",
        ),
    ]
    api_version: Annotated[
        str,
        Field(
            default="v1",
            description="API version prefix",
        ),
    ]

    def get_base_url(self) -> str:
        """Get the full base URL for the application."""
        return str(self.server.base_url)


@functools.lru_cache
def get_settings() -> Settings:
    """
    Get cached global settings instance.

    This function is cached to ensure a single Settings instance
    is used throughout the application lifecycle.

    Returns:
        Settings: The global settings instance
    """
    return Settings()
