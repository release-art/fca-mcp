# MCP Server for FCA Register API

Production-grade Model Context Protocol (MCP) server that exposes UK FCA Financial Services Register data to LLM clients through a structured, efficient API.

## Features

- **3 Focused Tools**: Minimal tool count for maximum efficiency
  - `search_firms`: Search for financial firms
  - `firm_get`: Get firm details with optional quick includes
  - `firm_related`: Universal access to all firm-related data
  
- **OAuth2 Authentication**: Bearer token authentication for LLM clients
- **TOON Format**: Structured Type-Object-Object-Namespace responses
- **Smart Pagination**: Preview and full modes with automatic truncation
- **Usage Tracking**: Comprehensive metrics and event logging
- **Caching**: In-memory cache with TTL support
- **Rate Limiting**: Configurable request limits per client
- **Timeout Guards**: Protection against slow endpoints
- **Production Ready**: Comprehensive tests, Docker support

## Architecture

```
LLM Client
    ↓ MCP Protocol + OAuth Bearer Token
┌─────────────────────────────────────┐
│         MCP Server                  │
│  ─────────────────────────────────  │
│  OAuth Middleware                   │
│  Rate Limiter                       │
│  Tool Router                        │
│  ├─ search_firms                    │
│  ├─ firm_get                        │
│  └─ firm_related (unified)          │
│  Pagination Orchestrator            │
│  TOON Formatter                     │
│  Cache Layer                        │
│  Usage Tracker                      │
└──────────────┬──────────────────────┘
               ↓
        fca-api (async)
               ↓
        FCA Register API
```

## Quick Start

### Prerequisites

- Python 3.11+
- FCA Register API credentials
- Docker (optional)

### Installation

```bash
pip install -e .
```

### Configuration

Create `.env` file:

```bash
FCA_API_EMAIL=your_email@example.com
FCA_API_KEY=your_api_key
```

### Basic Usage

```python
import asyncio
from mcp_fca.server.main import create_server

async def main():
    async with await create_server() as server:
        client = server.register_client(
            client_id="my_llm_client",
            client_secret="secret123",
            scopes=["read:firms", "search:firms"]
        )
        
        token = server.create_token("my_llm_client", "secret123")
        auth_header = f"Bearer {token['access_token']}"
        
        result = await server.handle_request(
            tool="search_firms",
            params={"query": "barclays", "limit": 5},
            authorization=auth_header
        )
        
        print(result)

asyncio.run(main())
```

## MCP Tools

### 1. search_firms

Search for firms by name.

**Parameters:**
- `query` (string): Search query
- `limit` (int): Maximum results (1-50, default: 5)

**Response:**
```json
{
  "type": "fca.firm.search",
  "version": "1.0",
  "data": [
    {
      "firm_id": "123456",
      "firm_name": "Example Firm Ltd",
      "status": "Authorised",
      "firm_type": "Limited Company"
    }
  ],
  "meta": {
    "pages_loaded": 1,
    "items_returned": 5,
    "truncated": false,
    "execution_time_ms": 123.45
  }
}
```

### 2. firm_get

Get firm core details with optional quick includes.

**Parameters:**
- `firm_id` (string): FRN (Firm Reference Number)
- `include` (list[string]): Optional data to include: `["names", "addresses"]`
- `summary` (bool): Return summary format (default: true)

**Response:**
```json
{
  "type": "fca.firm.details",
  "version": "1.0",
  "data": {
    "firm_id": "123456",
    "firm_name": "Example Firm Ltd",
    "status": "Authorised",
    "firm_type": "Limited Company",
    "effective_date": "2020-01-01T00:00:00",
    "names": [...],
    "addresses": [...]
  },
  "meta": {
    "pages_loaded": 1,
    "items_returned": 1,
    "truncated": false,
    "execution_time_ms": 89.12
  }
}
```

### 3. firm_related

Universal tool for all firm-related data with pagination.

**Parameters:**
- `firm_id` (string): FRN
- `kind` (string): Data type - one of:
  - `names`: Firm names
  - `addresses`: Addresses
  - `permissions`: Regulatory permissions
  - `individuals`: Associated individuals
  - `history`: Disciplinary history
  - `passports`: Passport information
  - `regulators`: Regulators
  - `requirements`: Requirements
  - `waivers`: Waivers
  - `appointed_representatives`: ARs
  - `controlled_functions`: Controlled functions
- `mode` (string): `preview` (10 items) or `full` (default: preview)
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (1-200, default: 50)
- `max_items` (int): Hard limit (1-1000, default: 200)
- `summary` (bool): Summary format (default: true)

**Response:**
```json
{
  "type": "fca.firm.permissions",
  "version": "1.0",
  "data": [
    {
      "permission_name": "Accepting deposits",
      "status": "Active",
      "granted_date": "2020-01-01T00:00:00"
    }
  ],
  "meta": {
    "pages_loaded": 2,
    "items_returned": 42,
    "truncated": false,
    "total_available": 42,
    "execution_time_ms": 234.56
  }
}
```

## Authentication

### Register Client

```python
client = server.register_client(
    client_id="llm_client_1",
    client_secret="secure_secret",
    scopes=["read:firms", "search:firms"]
)
```

### Create Token

```python
token = server.create_token(
    client_id="llm_client_1",
    client_secret="secure_secret"
)
```

### Make Request

```python
result = await server.handle_request(
    tool="search_firms",
    params={"query": "test"},
    authorization=f"Bearer {token['access_token']}"
)
```

## Docker Usage

### Build and Run

```bash
cp .env.example .env
docker-compose up --build
```

### Run Tests in Docker

```bash
docker-compose --profile test up test-runner
```

## Testing

### Run All Tests

```bash
pdm run pytest mcp_fca/tests/ -v
```

### Run Specific Test File

```bash
pdm run pytest mcp_fca/tests/test_oauth.py -v
```

### With Coverage

```bash
pdm run pytest mcp_fca/tests/ --cov=mcp_fca --cov-report=html
```

## Configuration

### Rate Limiting

```python
server = McpServer(
    fca_credentials=(email, key),
    enable_rate_limiting=True
)
server.rate_limiter = RateLimitGuard(
    max_requests=100,
    window_seconds=60
)
```

### Cache TTL

```python
server.cache = InMemoryCache(default_ttl=600)
```

### Pagination Limits

```python
server.paginator = PaginationOrchestrator(
    max_items=500,
    preview_items=20,
    timeout_seconds=30.0
)
```

## Usage Tracking

### Get Statistics

```python
stats = server.get_usage_stats(client_id="llm_client_1")
print(stats)
```

**Output:**
```python
{
    "total_requests": 150,
    "total_items": 3420,
    "avg_latency_ms": 145.6,
    "error_rate": 0.02,
    "tool_usage": {
        "search_firms": 50,
        "firm_get": 60,
        "firm_related": 40
    }
}
```

## Error Handling

All errors return structured responses:

```json
{
  "error": "Rate limit exceeded: 100 requests per 60s",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

**Error Codes:**
- `AUTH_FAILED`: Authentication failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INVALID_PARAMS`: Invalid parameters
- `TIMEOUT`: Request timed out
- `UNKNOWN_TOOL`: Tool not found
- `INTERNAL_ERROR`: Server error

## Project Structure

```
mcp_fca/
├── __init__.py
├── models/              # Pydantic data models
│   ├── firm.py
│   ├── meta.py
│   └── toon.py
├── adapters/            # External API adapters
│   └── fca_async_adapter.py
├── server/
│   ├── main.py         # Main MCP server
│   ├── tools/          # Tool handlers
│   │   └── handlers.py
│   ├── oauth/          # OAuth authentication
│   │   └── middleware.py
│   ├── tracking/       # Usage tracking
│   │   └── tracker.py
│   ├── pagination/     # Pagination orchestration
│   │   └── orchestrator.py
│   ├── cache/          # Cache layer
│   │   └── memory.py
│   ├── guards/         # Rate limits, timeouts
│   │   └── limits.py
│   └── toon/           # TOON formatter
│       └── formatter.py
└── tests/              # Comprehensive test suite
    ├── test_oauth.py
    ├── test_cache.py
    ├── test_pagination.py
    ├── test_guards.py
    ├── test_toon.py
    └── test_tracking.py
```

## Development

### Linting

```bash
pdm run ruff check mcp_fca/
```

### Auto-format

```bash
pdm run ruff format mcp_fca/
```

## License

Mozilla Public License 2.0 (MPL-2.0)

## Support

For issues related to:
- **MCP Server**: Open issue in this repository
- **FCA API Client**: See [fca-api documentation](https://docs.release.art/fca-api/)
- **FCA Register API**: Contact FCA directly

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Run test suite
5. Submit pull request

## Acknowledgments

Built on top of the excellent [fca-api](https://github.com/release-art/fca-api) library.
