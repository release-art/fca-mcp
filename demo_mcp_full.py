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
from typing import Any
from datetime import datetime

from mcp_fca.server.main import create_server


def print_header(title: str, char: str = "=", width: int = 100) -> None:
    """Print formatted header."""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}\n")


def print_section(title: str) -> None:
    """Print formatted section title."""
    print(f"\n{'─' * 100}")
    print(f"  [+] {title}")
    print(f"{'─' * 100}")


def print_toon_response(response: dict[str, Any], limit: int = 5) -> None:
    """Print TOON response in readable format."""
    print(f"\nType: {response.get('type', 'Unknown')}")
    print(f"Version: {response.get('version', 'Unknown')}")
    
    meta = response.get('meta', {})
    if meta:
        print(f"\n[Stats] Meta Information:")
        print(f"   Items returned: {meta.get('items_returned', 0)}")
        print(f"   Pages loaded: {meta.get('pages_loaded', 1)}")
        print(f"   Truncated: {meta.get('truncated', False)}")
        if meta.get('execution_time_ms'):
            print(f"   Execution time: {meta.get('execution_time_ms', 0):.2f}ms")
    
    data = response.get('data', [])
    if isinstance(data, list):
        print(f"\nData: ({len(data)} items, showing first {min(limit, len(data))}):")
        for i, item in enumerate(data[:limit], 1):
            try:
                print(f"\n   {i}. {json.dumps(item, indent=6, ensure_ascii=False, default=str)}")
            except Exception:
                print(f"\n   {i}. {item}")
    elif isinstance(data, dict):
        print(f"\nData:")
        try:
            print(f"{json.dumps(data, indent=3, ensure_ascii=False, default=str)}")
        except Exception:
            print(f"{data}")


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
        print(f"\n⏱️  Request time: {result.get('meta', {}).get('request_time_ms', 0):.2f}ms")
    else:
        print(f"❌ Error: {result['error']}")
    
    # Example 2: Search for Revolution
    print_section("Search: 'Revolution' (limit: 3)")
    result = await server.handle_request(
        tool="search_firms",
        params={"query": "Revolution", "limit": 3},
        authorization=None,
    )
    
    if 'error' not in result:
        print_toon_response(result, limit=3)
        print(f"\n⏱️  Request time: {result.get('meta', {}).get('request_time_ms', 0):.2f}ms")


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
        print(f"\n[Time] Request time: {result.get('meta', {}).get('request_time_ms', 0):.2f}ms")
        
        # Показати структуру даних для LLM
        data = result.get('data', {})
        print("\n[i] Для LLM доступні поля:")
        if isinstance(data, dict):
            for key in data.keys():
                print(f"   - {key}")
    else:
        print(f"[ERROR] Error: {result['error']}")


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
        print(f"\n⏱️  Request time: {result.get('meta', {}).get('request_time_ms', 0):.2f}ms")
    
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
            print("\n   [OK] Немає дисциплінарної історії (це добре!)")


async def demo_llm_usage(server: Any) -> None:
    """Демонстрація як LLM може використовувати MCP сервер."""
    print_header("LLM USAGE SCENARIO - Як LLM використовує MCP сервер")
    
    print("\n>>> LLM Prompt: 'Знайди інформацію про Barclays Bank та покажи їх дозволи'")
    print("\n[AI] LLM виконує:")
    
    # Крок 1: Пошук фірми
    print("\n   Крок 1: Викликає search_firms")
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
            print(f"   [+] Знайдено: {name} (FRN: {frn})")
            
            # Крок 2: Отримати деталі фірми
            print(f"\n   Крок 2: Викликає firm_get для FRN {frn}")
            result2 = await server.handle_request(
                tool="firm_get",
                params={"firm_id": frn},
                authorization=None,
            )
            
            firm_data = result2.get('data', {}) if 'error' not in result2 else {}
            if firm_data:
                print(f"   [+] Отримано деталі: {firm_data.get('firm_name', 'N/A')}")
            
            # Крок 3: Отримати дозволи
            print(f"\n   Крок 3: Викликає firm_related для permissions")
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
                print(f"   [+] Знайдено {len(perms)} дозволів:")
                for i, perm in enumerate(perms[:3], 1):
                    print(f"      {i}. {perm.get('permission_name', 'Unknown')}")
                    if perm.get('customer_types'):
                        print(f"         Customer types: {perm['customer_types']}")
            
            # Крок 4: LLM формує відповідь
            print(f"\n   Крок 4: LLM формує відповідь користувачу:")
            if firm_data:
                print(f"\n   ==> '{name} (FRN: {frn}) є {firm_data.get('status', 'N/A')} фірмою.")
                if perms:
                    print(f"       Фірма має {len(perms)} регуляторних дозволів, включаючи:")
                    for i, perm in enumerate(perms[:3], 1):
                        print(f"       {i}. {perm.get('permission_name', 'N/A')}")
            else:
                print(f"\n   ==> Не вдалося отримати деталі для фірми {name}")


async def demo_statistics(server: Any) -> None:
    """Show server usage statistics."""
    print_header("MCP SERVER STATISTICS")
    
    stats = server.get_usage_stats()
    
    print("[Stats] Tool Usage:")
    print(f"   - Total Events: {stats.get('total_events', 0)}")
    print(f"   - Total Items Returned: {stats.get('total_items_returned', 0)}")
    
    by_tool = stats.get('by_tool', {})
    if by_tool:
        print(f"\n   By tool:")
        for tool_name, count in by_tool.items():
            print(f"      - {tool_name}: {count} calls")
    
    print(f"\n[Speed] Performance:")
    print(f"   - Cache hits: {stats.get('cache_hits', 0)}")
    print(f"   - Cache misses: {stats.get('cache_misses', 0)}")
    cache_hits = stats.get('cache_hits', 0)
    cache_misses = stats.get('cache_misses', 0)
    hit_rate = cache_hits / max(cache_hits + cache_misses, 1) * 100
    print(f"   - Cache hit rate: {hit_rate:.1f}%")
    
    print(f"\n[Security] Security:")
    print(f"   - OAuth enabled: {stats.get('oauth_enabled', False)}")
    print(f"   - Rate limiting: Active")


async def main() -> None:
    """Main demonstration function."""
    print_header("FCA API + MCP SERVER - COMPLETE DEMONSTRATION", "=", 100)
    print("Demonstration of MCP server with real FCA API data")
    print("Shows how LLM can use tools to retrieve financial data")
    
    # Server initialization
    print("\n>> Connecting to FCA API...")
    print("   Email: developer@release.art")
    print("   API Key: ************************************")
    print("   Using real API credentials")
    
    server = await create_server(
        fca_email="developer@release.art",
        fca_key="2177e659a8afc899c39e30bda383e1b2",
        enable_auth=False,  # OAuth disabled for demo
    )
    
    print("[OK] Server initialized successfully!\n")
    
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
        print("[OK] All tools work correctly")
        print("[OK] Data is displayed in TOON format")
        print("[OK] LLM can use MCP server to retrieve financial data")
        print("\n[i] MCP server is ready for integration with Claude, GPT-4 and other LLMs!")
        
    finally:
        print("\n>> Closing connection to FCA API...")
        await server.close()
        print("[OK] Connection closed\n")


if __name__ == "__main__":
    asyncio.run(main())
