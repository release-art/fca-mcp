"""Global settings for the fca-mcp project."""

from __future__ import annotations

import functools
from typing import Literal

from pydantic import Field, HttpUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Auth0Settings(BaseSettings):
    """Auth0 OAuth configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="AUTH0_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    domain: str = Field(
        ...,
        description="Auth0 domain (e.g., 'your-tenant.auth0.com')",
    )
    audience: str = Field(
        ...,
        description="Auth0 API audience identifier",
    )
    client_id: str = Field(
        description="Auth0 client ID (optional, for client credentials flow)",
    )
    client_secret: str = Field(
        description="Auth0 client secret (optional, for client credentials flow)",
    )


class RedisSettings(BaseSettings):
    """Redis connection and caching configuration."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    password: str | None = Field(
        default=None,
        description="Redis password (if required)",
    )
    db: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis database number (0-15)",
    )
    max_connections: int = Field(
        default=10,
        ge=1,
        description="Maximum number of connections in the pool",
    )
    socket_timeout: float = Field(
        default=5.0,
        gt=0,
        description="Socket timeout in seconds",
    )
    socket_connect_timeout: float = Field(
        default=5.0,
        gt=0,
        description="Socket connection timeout in seconds",
    )
    cache_ttl: int = Field(
        default=3600,
        ge=0,
        description="Default cache TTL in seconds (0 = no expiration)",
    )
    enabled: bool = Field(
        default=True,
        description="Enable Redis caching",
    )


class FcaApiSettings(BaseSettings):
    """FCA API credentials and configuration."""

    model_config = SettingsConfigDict(
        env_prefix="FCA_API_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    username: str = Field(
        ...,
        description="FCA API username/email",
    )
    key: str = Field(
        ...,
        description="FCA API key",
    )
    base_url: HttpUrl | None = Field(
        default=None,
        description="FCA API base URL (optional override)",
    )
    timeout: float = Field(
        default=30.0,
        gt=0,
        description="API request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum number of retries for failed requests",
    )


class ServerSettings(BaseSettings):
    """Server configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="SERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(
        default="0.0.0.0",
        description="Server host address",
    )
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port number",
    )
    base_url: HttpUrl = Field(
        description="Full base URL",
    )
    workers: int = Field(
        default=1,
        ge=1,
        description="Number of worker processes",
    )


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    format: Literal["json", "text"] = Field(
        default="text",
        description="Log output format",
    )
    file: str | None = Field(
        default=None,
        description="Log file path (None = stdout only)",
    )


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Environment and deployment
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    # Nested settings
    auth0: Auth0Settings = Field(default_factory=Auth0Settings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    fca_api: FcaApiSettings = Field(default_factory=FcaApiSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    # Additional top-level settings
    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS origins",
    )
    api_version: str = Field(
        default="v1",
        description="API version prefix",
    )

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
