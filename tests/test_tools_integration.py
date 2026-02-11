"""Comprehensive integration tests for MCP tools with real API."""

import pytest
import pytest_asyncio

from fca_mcp.adapters.fca_async_adapter import FcaApiAdapter
from fca_mcp.server.cache.memory import InMemoryCache
from fca_mcp.server.pagination.orchestrator import PaginationOrchestrator
from fca_mcp.server.tools.handlers import FirmGetParams, FirmRelatedParams, McpTools, SearchFirmsParams


@pytest_asyncio.fixture
async def fca_adapter():
    """Create FCA API adapter with real credentials."""
    adapter = FcaApiAdapter(credentials=("developer@release.art", "2177e659a8afc899c39e30bda383e1b2"))
    async with adapter:
        yield adapter


@pytest_asyncio.fixture
async def mcp_tools(fca_adapter):
    """Create MCP tools instance."""
    cache = InMemoryCache(default_ttl=300)
    paginator = PaginationOrchestrator(max_items=200, preview_items=10)
    return McpTools(adapter=fca_adapter, cache=cache, paginator=paginator)


class TestSearchFirmsTool:
    """Tests for search_firms tool."""

    @pytest.mark.asyncio
    async def test_search_firms_basic(self, mcp_tools):
        """Test basic firm search."""
        params = SearchFirmsParams(query="Barclays", limit=5)
        result = await mcp_tools.search_firms(params)

        assert result["type"] == "fca.firm.search"
        assert result["meta"]["items_returned"] > 0
        assert len(result["data"]) <= 5
        assert all("firm_id" in firm for firm in result["data"])
        assert all("firm_name" in firm for firm in result["data"])

    @pytest.mark.asyncio
    async def test_search_firms_caching(self, mcp_tools):
        """Test that search results are cached."""
        params = SearchFirmsParams(query="Revolution", limit=3)
        
        # First call - should hit API
        result1 = await mcp_tools.search_firms(params)
        
        # Second call - should hit cache  (same data returned faster)
        result2 = await mcp_tools.search_firms(params)
        
        # Results should be identical
        assert result1["data"] == result2["data"]
        assert result1["meta"]["items_returned"] == result2["meta"]["items_returned"]

    @pytest.mark.asyncio
    async def test_search_firms_limit_enforcement(self, mcp_tools):
        """Test that limit is properly enforced."""
        params = SearchFirmsParams(query="Bank", limit=3)
        result = await mcp_tools.search_firms(params)
        
        assert len(result["data"]) <= 3
        assert result["meta"]["items_returned"] <= 3

    @pytest.mark.asyncio
    async def test_search_firms_empty_results(self, mcp_tools):
        """Test search with no results."""
        params = SearchFirmsParams(query="XYZ_NONEXISTENT_FIRM_12345", limit=5)
        result = await mcp_tools.search_firms(params)
        
        assert result["meta"]["items_returned"] == 0
        assert result["data"] == []


class TestFirmGetTool:
    """Tests for firm_get tool."""

    @pytest.mark.asyncio
    async def test_firm_get_basic(self, mcp_tools):
        """Test basic firm retrieval."""
        params = FirmGetParams(firm_id="122702")  # Barclays
        result = await mcp_tools.firm_get(params)
        
        assert result["type"] == "fca.firm.details"
        assert result["data"]["firm_id"] == "122702"
        assert "firm_name" in result["data"]
        assert "status" in result["data"]

    @pytest.mark.asyncio
    async def test_firm_get_with_names(self, mcp_tools):
        """Test firm retrieval with names included."""
        params = FirmGetParams(firm_id="122702", include=["names"])
        result = await mcp_tools.firm_get(params)
        
        assert "names" in result["data"]
        assert isinstance(result["data"]["names"], list)
        if result["data"]["names"]:
            assert "name" in result["data"]["names"][0]

    @pytest.mark.asyncio
    async def test_firm_get_with_addresses(self, mcp_tools):
        """Test firm retrieval with addresses included."""
        params = FirmGetParams(firm_id="122702", include=["addresses"])
        result = await mcp_tools.firm_get(params)
        
        assert "addresses" in result["data"]
        assert isinstance(result["data"]["addresses"], list)

    @pytest.mark.asyncio
    async def test_firm_get_with_multiple_includes(self, mcp_tools):
        """Test firm retrieval with multiple includes."""
        params = FirmGetParams(firm_id="122702", include=["names", "addresses"])
        result = await mcp_tools.firm_get(params)
        
        assert "names" in result["data"]
        assert "addresses" in result["data"]

    @pytest.mark.asyncio
    async def test_firm_get_caching(self, mcp_tools):
        """Test that firm details are cached."""
        params = FirmGetParams(firm_id="122702")
        
        result1 = await mcp_tools.firm_get(params)
        result2 = await mcp_tools.firm_get(params)
        
        # Cached results should be identical
        assert result1["data"]["firm_name"] == result2["data"]["firm_name"]
        assert result1["data"]["firm_id"] == result2["data"]["firm_id"]


class TestFirmRelatedTool:
    """Tests for firm_related tool."""

    @pytest.mark.asyncio
    async def test_firm_related_names(self, mcp_tools):
        """Test getting firm names."""
        params = FirmRelatedParams(firm_id="122702", kind="names", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.names"
        assert isinstance(result["data"], list)
        assert result["meta"]["pages_loaded"] >= 1

    @pytest.mark.asyncio
    async def test_firm_related_addresses(self, mcp_tools):
        """Test getting firm addresses."""
        params = FirmRelatedParams(firm_id="122702", kind="addresses", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.addresses"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_firm_related_permissions(self, mcp_tools):
        """Test getting firm permissions."""
        params = FirmRelatedParams(firm_id="122702", kind="permissions", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.permissions"
        assert isinstance(result["data"], list)
        assert result["meta"]["items_returned"] <= 10  # Preview mode limit

    @pytest.mark.asyncio
    async def test_firm_related_individuals(self, mcp_tools):
        """Test getting firm individuals."""
        params = FirmRelatedParams(firm_id="122702", kind="individuals", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.individuals"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_firm_related_passports(self, mcp_tools):
        """Test getting firm passports."""
        params = FirmRelatedParams(firm_id="122702", kind="passports", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.passports"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_firm_related_regulators(self, mcp_tools):
        """Test getting firm regulators."""
        params = FirmRelatedParams(firm_id="122702", kind="regulators", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.regulators"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_firm_related_requirements(self, mcp_tools):
        """Test getting firm requirements."""
        params = FirmRelatedParams(firm_id="122702", kind="requirements", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.requirements"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_firm_related_waivers(self, mcp_tools):
        """Test getting firm waivers."""
        params = FirmRelatedParams(firm_id="122702", kind="waivers", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.waivers"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_firm_related_appointed_representatives(self, mcp_tools):
        """Test getting appointed representatives."""
        params = FirmRelatedParams(firm_id="122702", kind="appointed_representatives", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.appointed_representatives"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_firm_related_controlled_functions(self, mcp_tools):
        """Test getting controlled functions."""
        params = FirmRelatedParams(firm_id="122702", kind="controlled_functions", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.controlled_functions"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_firm_related_history(self, mcp_tools):
        """Test getting disciplinary history."""
        params = FirmRelatedParams(firm_id="122702", kind="history", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert result["type"] == "fca.firm.history"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_firm_related_preview_vs_full_mode(self, mcp_tools):
        """Test difference between preview and full modes."""
        # Preview mode
        params_preview = FirmRelatedParams(firm_id="122702", kind="permissions", mode="preview")
        result_preview = await mcp_tools.firm_related(params_preview)
        
        # Full mode
        params_full = FirmRelatedParams(firm_id="122702", kind="permissions", mode="full", max_items=50)
        result_full = await mcp_tools.firm_related(params_full)
        
        # Preview should have <= 10 items
        assert result_preview["meta"]["items_returned"] <= 10
        # Full can have more
        assert result_full["meta"]["items_returned"] >= result_preview["meta"]["items_returned"]

    @pytest.mark.asyncio
    async def test_firm_related_invalid_kind(self, mcp_tools):
        """Test that invalid kind raises error."""
        params = FirmRelatedParams(firm_id="122702", kind="invalid_type", mode="preview")
        
        with pytest.raises(ValueError, match="Unknown kind"):
            await mcp_tools.firm_related(params)

    @pytest.mark.asyncio
    async def test_firm_related_caching(self, mcp_tools):
        """Test that related data is cached."""
        params = FirmRelatedParams(firm_id="122702", kind="names", mode="preview")
        
        result1 = await mcp_tools.firm_related(params)
        result2 = await mcp_tools.firm_related(params)
        
        # Cached results should be identical
        assert result1["data"] == result2["data"]
        assert result1["meta"]["items_returned"] == result2["meta"]["items_returned"]


class TestToonFormatCompliance:
    """Test TOON format compliance across all tools."""

    @pytest.mark.asyncio
    async def test_search_firms_toon_format(self, mcp_tools):
        """Verify search_firms returns proper TOON format."""
        params = SearchFirmsParams(query="Test", limit=1)
        result = await mcp_tools.search_firms(params)
        
        assert "type" in result
        assert "version" in result
        assert "data" in result
        assert "meta" in result
        assert "pages_loaded" in result["meta"]
        assert "items_returned" in result["meta"]
        assert "truncated" in result["meta"]
        assert "execution_time_ms" in result["meta"]

    @pytest.mark.asyncio
    async def test_firm_get_toon_format(self, mcp_tools):
        """Verify firm_get returns proper TOON format."""
        params = FirmGetParams(firm_id="122702")
        result = await mcp_tools.firm_get(params)
        
        assert "type" in result
        assert "version" in result
        assert "data" in result
        assert "meta" in result

    @pytest.mark.asyncio
    async def test_firm_related_toon_format(self, mcp_tools):
        """Verify firm_related returns proper TOON format."""
        params = FirmRelatedParams(firm_id="122702", kind="names", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        assert "type" in result
        assert "version" in result
        assert "data" in result
        assert "meta" in result
        assert result["type"].startswith("fca.firm.")


class TestDataMinimization:
    """Test that responses don't include unnecessary API metadata."""

    @pytest.mark.asyncio
    async def test_no_pagination_urls_in_response(self, mcp_tools):
        """Ensure pagination URLs are not exposed to LLM."""
        params = FirmRelatedParams(firm_id="122702", kind="names", mode="preview")
        result = await mcp_tools.firm_related(params)
        
        # Check that internal pagination URLs are not exposed
        result_str = str(result)
        assert "next_url" not in result_str.lower()
        assert "previous_url" not in result_str.lower()
        assert "register.fca.org.uk" not in result_str  # No raw API URLs

    @pytest.mark.asyncio
    async def test_clean_data_structure(self, mcp_tools):
        """Verify response contains only essential fields."""
        params = SearchFirmsParams(query="Bank", limit=1)
        result = await mcp_tools.search_firms(params)
        
        # Should only have: type, version, data, meta
        top_level_keys = set(result.keys())
        assert top_level_keys == {"type", "version", "data", "meta"}

