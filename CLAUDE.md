# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

An MCP (Model Context Protocol) server exposing the UK FCA Financial Services Register via 25 read-only tools. Built on FastMCP v3, served over HTTP (Starlette/uvicorn) or stdio. Uses Auth0 for OAuth2; in `proxy` mode, client registrations are persisted in Azure Blob Storage (Fernet-encrypted).

## Commands

```bash
# Install dependencies
pdm install

# Run server (HTTP mode, development)
pdm run python -m fca_mcp serve --reload

# Run server (stdio mode, for MCP clients)
pdm run python -m fca_mcp stdio

# Run all tests with coverage
pdm run pytest

# Run a single test file
pdm run pytest tests/server/test_firm_simple.py

# Run a single test
pdm run pytest tests/server/test_firm_simple.py::test_get_firm -v

# Lint
pdm run ruff check

# Auto-fix lint issues
pdm run ruff check --fix

# Format
pdm run ruff format

# Docker (includes Azurite for Azure emulation)
docker-compose up --build
```

## Architecture

### Server Composition

`get_server()` in `src/fca_mcp/server/__init__.py` builds the main FastMCP instance and mounts five sub-servers, each owning a group of tools:

- `search.py` — 3 tools: `search_frn`, `search_irn`, `search_prn`
- `firms.py` — 15 tools: `get_firm`, `get_firm_names`, `get_firm_addresses`, etc.
- `funds.py` — 3 tools: `get_fund`, `get_fund_names`, `get_fund_subfunds`
- `individuals.py` — 3 tools: `get_individual`, `get_individual_controlled_functions`, `get_individual_disciplinary_history`
- `markets.py` — 1 tool: `get_regulated_markets`

### Dependency Injection

Tools receive the FCA API client via FastMCP's `Depends` system:

```python
async def tool_name(
    frn: FrnParam,
    fca_client: fca_api.async_api.Client = deps.FcaApiDep,
) -> ReturnType:
```

`FcaApiDep` chains: `CurrentContext()` → `get_fca_app()` (extracts from lifespan context) → `get_fca_api()`.

### Type Reflection System

`reflect_fca_api_t()` in `server/types/base.py` dynamically generates Pydantic models from `fca-api` library types, stripping fields marked as internal (e.g., `InternalUrl`). Tools call `ReturnType.from_api_t(api_result)` to convert API responses.

### Authentication

Two distinct concepts — note the underscore vs hyphen difference:
- **Scope** (`auth/scopes.py`): `FCA_API_RO = "fca-api:read"` — the OAuth2 scope in tokens
- **Tag** (`auth/tags.py`): `FCA_API_RO = "fca_api:read"` — the tag on tool decorators

`AuthMiddleware` uses `restrict_tag()`: tools tagged with `FCA_API_RO` require the matching scope in the access token. Untagged tools (e.g., `initialize`, `tools/list`) are allowed through without scope checks. The middleware skips auth entirely for stdio transport.

Auth provider (`auth/provider.py`) has two modes selected by `AUTH0_MODE`:
- `remote` (default): `RemoteAuthProvider` + `JWTVerifier` — validates tokens issued by an upstream Auth0 tenant. No client storage.
- `proxy`: `Auth0Provider` — full OAuth proxy with dynamic client registration. Clients are persisted in `AzureBlobStore` wrapped in `FernetEncryptionWrapper` (key: `AUTH0_STORAGE_ENCRYPTION_KEY`).

Note: `JWTVerifier` is intentionally constructed without `required_scopes`. Global scope enforcement would reject `initialize`/`tools/list`; scope checks live in `AuthMiddleware` + `restrict_tag` instead.

### Middleware Stack (execution order)

1. `ErrorHandlingMiddleware`
2. `RateLimitingMiddleware`
3. `LoggingMiddleware`
4. `AuthMiddleware` (innermost — runs last before tool execution)

### Testing

Tests use FastMCP's in-memory transport (`FastMCPTransport`) — no HTTP server needed. Key fixtures in `tests/server/conftest.py`:

- `mock_fca_api` (autouse): Patches `fca_api.async_api.Client` with a caching mock that records/replays real API responses
- `mock_auth_components` (autouse): Replaces the configured auth provider (`RemoteAuthProvider` or `Auth0Provider`) with `DebugTokenVerifier` and injects a synthetic `AccessToken` so auth middleware works without live Azure/Auth0
- `oauth_scopes`: Override per-test to control granted scopes (default: `["fca-api:read"]`)
- `mcp_app` → `mcp_client`: Creates server and async client

To test scope denial, override `oauth_scopes` in a test:

```python
@pytest.fixture
def oauth_scopes():
    return []  # No scopes — tagged tools should be denied
```

## Code Style

- **Line length**: 120 characters
- **Ruff rules**: A, B, C, E, F, I, W, N, C4, T20, PTH
- **Python**: >=3.13 required
- All tools use `ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True)`
- Parameter descriptions use `Annotated[str, pydantic.Field(description=...)]` with type aliases (`FrnParam`, `PrnParam`, `IrnParam`) to avoid repetition
