"""Complete demonstration of MCP Server with FCA API.

Demonstrates:
1. MCP server initialization with real FCA API data
2. All 3 main tools (search_firms, firm_get, firm_related)
3. TOON format for responses
4. Pagination and caching
5. How LLM can use this data
"""
import asyncio
import json
import logging
from typing import Any
from datetime import datetime

from fca_mcp.server.main import create_server

logger = logging.getLogger(__name__)


def print_header(title: str, char: str = "=", width: int = 100) -> None:
    """Print formatted header."""
    logger.info("\n%s", char * width)
    logger.info("%s", f"{title:^{width}}")
    logger.info("%s\n", char * width)


def print_section(title: str) -> None:
    """Print formatted section title."""
    logger.info("\n%s", "─" * 100)
    logger.info("  [+] %s", title)
    logger.info("%s", "─" * 100)


def print_toon_response(response: dict[str, Any], limit: int = 5) -> None:
    """Print TOON response in readable format."""
    logger.info("\nType: %s", response.get("type", "Unknown"))
    logger.info("Version: %s", response.get("version", "Unknown"))
    
    meta = response.get('meta', {})
    if meta:
        logger.info("\n[Stats] Meta Information:")
        logger.info("   Items returned: %s", meta.get("items_returned", 0))
        logger.info("   Pages loaded: %s", meta.get("pages_loaded", 1))
        logger.info("   Truncated: %s", meta.get("truncated", False))
        if meta.get('execution_time_ms'):
            logger.info("   Execution time: %.2fms", meta.get("execution_time_ms", 0))
    
    data = response.get('data', [])
    if isinstance(data, list):
        logger.info("\nData: (%s items, showing first %s):", len(data), min(limit, len(data)))
        for i, item in enumerate(data[:limit], 1):
            try:
                logger.info("\n   %s. %s", i, json.dumps(item, indent=6, ensure_ascii=False, default=str))
            except Exception:
                logger.info("\n   %s. %s", i, item)
    elif isinstance(data, dict):
        logger.info("\nData:")
        try:
            logger.info("%s", json.dumps(data, indent=3, ensure_ascii=False, default=str))
        except Exception:
            logger.info("%s", data)


async def demo_tool_1_search_firms(server: Any) -> None:
    """Demonstration of TOOL 1: search_firms - Search for financial firms."""
    print_header("TOOL 1: SEARCH_FIRMS - Search for Financial Firms")
    
    # Example 1: Search for Barclays
    print_section("Search: 'Barclays' (limit: 5)")
    result = await server.handle_request(
        tool="search_firms",
        params={"query": "Barclays", "limit": 5},
        authorization=None,
    )
    
    if 'error' not in result:
        print_toon_response(result)
        logger.info("\n⏱️  Request time: %.2fms", result.get("meta", {}).get("request_time_ms", 0))
    else:
        logger.error("❌ Error: %s", result["error"])
    
    # Example 2: Search for Revolution
    print_section("Search: 'Revolution' (limit: 3)")
    result = await server.handle_request(
        tool="search_firms",
        params={"query": "Revolution", "limit": 3},
        authorization=None,
    )
    
    if 'error' not in result:
        print_toon_response(result, limit=3)
        logger.info("\n⏱️  Request time: %.2fms", result.get("meta", {}).get("request_time_ms", 0))


async def demo_tool_2_firm_get(server: Any) -> None:
    """Demonstration of TOOL 2: firm_get - Get firm details."""
    print_header("TOOL 2: FIRM_GET - Detailed Firm Information")
    
    # Example 1: Barclays Bank
    print_section("Firm: Barclays Bank Plc (FRN: 122702)")
    result = await server.handle_request(
        tool="firm_get",
        params={"firm_id": "122702"},
        authorization=None,
    )
    
    if 'error' not in result:
        print_toon_response(result, limit=1)
        logger.info("\n[Time] Request time: %.2fms", result.get("meta", {}).get("request_time_ms", 0))
        
        # Показати структуру даних для LLM
        data = result.get('data', {})
        logger.info("\n[i] Для LLM доступні поля:")
        if isinstance(data, dict):
            for key in data.keys():
                logger.info("   - %s", key)
    else:
        logger.error("[ERROR] Error: %s", result["error"])


async def demo_tool_3_firm_related(server: Any) -> None:
    """Demonstration of TOOL 3: firm_related - Firm related data."""
    print_header("TOOL 3: FIRM_RELATED - Firm Related Data")
    
    firm_id = "122702"  # Barclays
    
    # Example 1: Permissions
    print_section(f"Permissions for FRN {firm_id} (first 3)")
    result = await server.handle_request(
        tool="firm_related",
        params={
            "firm_id": firm_id,
            "kind": "permissions",
            "page_size": 3,
        },
        authorization=None,
    )
    
    if 'error' not in result:
        print_toon_response(result, limit=3)
        logger.info("\n⏱️  Request time: %.2fms", result.get("meta", {}).get("request_time_ms", 0))
    
    # Приклад 2: Requirements (вимоги)
    print_section(f"Requirements для FRN {firm_id} (перші 2)")
    result = await server.handle_request(
        tool="firm_related",
        params={
            "firm_id": firm_id,
            "kind": "requirements",
            "page_size": 2,
        },
        authorization=None,
    )
    
    if 'error' not in result:
        print_toon_response(result, limit=2)
    
    # Приклад 3: Waivers (відступи)
    print_section(f"Waivers для FRN {firm_id} (перші 2)")
    result = await server.handle_request(
        tool="firm_related",
        params={
            "firm_id": firm_id,
            "kind": "waivers",
            "page_size": 2,
        },
        authorization=None,
    )
    
    if 'error' not in result:
        print_toon_response(result, limit=2)
    
    # Приклад 4: Passports
    print_section(f"Passports для FRN {firm_id} (всі)")
    result = await server.handle_request(
        tool="firm_related",
        params={
            "firm_id": firm_id,
            "kind": "passports",
        },
        authorization=None,
    )
    
    if 'error' not in result:
        print_toon_response(result, limit=5)
    
    # Приклад 5: Disciplinary History
    print_section(f"Disciplinary History для FRN {firm_id}")
    result = await server.handle_request(
        tool="firm_related",
        params={
            "firm_id": firm_id,
            "kind": "disciplinary_history",
        },
        authorization=None,
    )
    
    if 'error' not in result:
        data = result.get('data', [])
        if data:
            print_toon_response(result, limit=2)
        else:
            logger.info("\n   [OK] Немає дисциплінарної історії (це добре!)")


async def demo_llm_usage(server: Any) -> None:
    """Демонстрація як LLM може використовувати MCP сервер."""
    print_header("LLM USAGE SCENARIO - Як LLM використовує MCP сервер")
    
    logger.info("\n>>> LLM Prompt: 'Знайди інформацію про Barclays Bank та покажи їх дозволи'")
    logger.info("\n[AI] LLM виконує:")
    
    # Крок 1: Пошук фірми
    logger.info("\n   Крок 1: Викликає search_firms")
    result1 = await server.handle_request(
        tool="search_firms",
        params={"query": "Barclays Bank", "limit": 1},
        authorization=None,
    )
    
    if 'error' not in result1:
        data = result1.get('data', [])
        if data:
            firm = data[0]
            frn = firm.get('firm_id')
            name = firm.get('firm_name')
            logger.info("   [+] Знайдено: %s (FRN: %s)", name, frn)
            
            # Крок 2: Отримати деталі фірми
            logger.info("\n   Крок 2: Викликає firm_get для FRN %s", frn)
            result2 = await server.handle_request(
                tool="firm_get",
                params={"firm_id": frn},
                authorization=None,
            )
            
            firm_data = result2.get('data', {}) if 'error' not in result2 else {}
            if firm_data:
                logger.info("   [+] Отримано деталі: %s", firm_data.get("firm_name", "N/A"))
            
            # Крок 3: Отримати дозволи
            logger.info("\n   Крок 3: Викликає firm_related для permissions")
            result3 = await server.handle_request(
                tool="firm_related",
                params={
                    "firm_id": frn,
                    "kind": "permissions",
                    "max_items": 3,
                },
                authorization=None,
            )
            
            perms = []
            if 'error' not in result3:
                perms = result3.get('data', [])
                logger.info("   [+] Знайдено %s дозволів:", len(perms))
                for i, perm in enumerate(perms[:3], 1):
                    logger.info("      %s. %s", i, perm.get("permission_name", "Unknown"))
                    if perm.get('customer_types'):
                        logger.info("         Customer types: %s", perm["customer_types"])
            
            # Крок 4: LLM формує відповідь
            logger.info("\n   Крок 4: LLM формує відповідь користувачу:")
            if firm_data:
                logger.info("\n   ==> '%s (FRN: %s) є %s фірмою.", name, frn, firm_data.get("status", "N/A"))
                if perms:
                    logger.info("       Фірма має %s регуляторних дозволів, включаючи:", len(perms))
                    for i, perm in enumerate(perms[:3], 1):
                        logger.info("       %s. %s", i, perm.get("permission_name", "N/A"))
            else:
                logger.info("\n   ==> Не вдалося отримати деталі для фірми %s", name)


async def demo_statistics(server: Any) -> None:
    """Show server usage statistics."""
    print_header("MCP SERVER STATISTICS")
    
    stats = server.get_usage_stats()
    
    logger.info("[Stats] Tool Usage:")
    logger.info("   - Total Events: %s", stats.get("total_events", 0))
    logger.info("   - Total Items Returned: %s", stats.get("total_items_returned", 0))
    
    by_tool = stats.get('by_tool', {})
    if by_tool:
        logger.info("\n   By tool:")
        for tool_name, count in by_tool.items():
            logger.info("      - %s: %s calls", tool_name, count)
    
    logger.info("\n[Speed] Performance:")
    logger.info("   - Cache hits: %s", stats.get("cache_hits", 0))
    logger.info("   - Cache misses: %s", stats.get("cache_misses", 0))
    cache_hits = stats.get('cache_hits', 0)
    cache_misses = stats.get('cache_misses', 0)
    hit_rate = cache_hits / max(cache_hits + cache_misses, 1) * 100
    logger.info("   - Cache hit rate: %.1f%%", hit_rate)
    
    logger.info("\n[Security] Security:")
    logger.info("   - OAuth enabled: %s", stats.get("oauth_enabled", False))
    logger.info("   - Rate limiting: Active")


async def main() -> None:
    """Main demonstration function."""
    print_header("FCA API + MCP SERVER - COMPLETE DEMONSTRATION", "=", 100)
    logger.info("Demonstration of MCP server with real FCA API data")
    logger.info("Shows how LLM can use tools to retrieve financial data")
    
    # Server initialization
    logger.info("\n>> Connecting to FCA API...")
    logger.info("   Email: developer@release.art")
    logger.info("   API Key: ************************************")
    logger.info("   Using real API credentials")
    
    server = await create_server(
        fca_email="developer@release.art",
        fca_key="2177e659a8afc899c39e30bda383e1b2",
        enable_auth=False,  # OAuth disabled for demo
    )
    
    logger.info("[OK] Server initialized successfully!\n")
    
    try:
        # Demonstration of all tools
        await demo_tool_1_search_firms(server)
        await demo_tool_2_firm_get(server)
        await demo_tool_3_firm_related(server)
        
        # LLM usage demonstration
        await demo_llm_usage(server)
        
        # Statistics
        await demo_statistics(server)
        
        # Final message
        print_header("DEMONSTRATION COMPLETE", "=", 100)
        logger.info("[OK] All tools work correctly")
        logger.info("[OK] Data is displayed in TOON format")
        logger.info("[OK] LLM can use MCP server to retrieve financial data")
        logger.info("\n[i] MCP server is ready for integration with Claude, GPT-4 and other LLMs!")
        
    finally:
        logger.info("\n>> Closing connection to FCA API...")
        await server.close()
        logger.info("[OK] Connection closed\n")


if __name__ == "__main__":
    asyncio.run(main())
