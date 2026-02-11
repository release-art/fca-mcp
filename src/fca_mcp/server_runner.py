from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

import fca_mcp

logger = logging.getLogger(__name__)


class FcaMcpServerRunner:
    """Complete FCA MCP Server with AI analysis and interactive interface."""

    def __init__(self):
        """Initialize server runner."""
        self.server = None
        self.assistant = None
        self.nl_interface = None
        self.shutdown_event = asyncio.Event()
        self.load_env()

    def load_env(self) -> None:
        """Load environment variables from .env file."""
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

    async def start(self, enable_auth: bool = False) -> None:
        """Start the MCP server with AI capabilities."""
        logger.info("%s", "=" * 100)
        logger.info("FCA MCP SERVER WITH AI ANALYSIS")
        logger.info("%s", "=" * 100)
        logger.info("")

        fca_email = os.getenv("FCA_API_USERNAME")
        fca_key = os.getenv("FCA_API_KEY")

        if not fca_email or not fca_key:
            logger.error("[ERROR] Missing FCA API credentials!")
            logger.error("Set FCA_API_USERNAME and FCA_API_KEY in .env file")
            return

        logger.info("[INIT] Connecting to FCA API...")
        logger.info("  Email: %s", fca_email)
        logger.info("  API Key: %s", "*" * 32)
        logger.info("  Auth: %s", enable_auth)
        logger.info("")

        try:
            self.server = await fca_mcp.server.main.create_server(
                fca_email=fca_email, fca_key=fca_key, enable_auth=enable_auth
            )

            self.assistant = FcaAiAssistant(self.server)
            self.nl_interface = NaturalLanguageInterface(self.assistant)

            logger.info("[OK] Server started successfully!")
            logger.info("")
            logger.info("Available Features:")
            logger.info("  [1] MCP Tools: search_firms, firm_get, firm_related")
            logger.info("  [2] AI Analysis: Risk scoring, firm comparison, insights")
            logger.info("  [3] NL Interface: Natural language queries for LLMs")
            logger.info("")

        except Exception as e:
            logger.error("[ERROR] Failed to start server: %s", e)
            raise

    async def interactive_mode(self) -> None:
        """Run server in interactive mode with advanced commands."""
        logger.info("%s", "=" * 100)
        logger.info("INTERACTIVE MODE - Advanced Interface")
        logger.info("%s", "=" * 100)
        logger.info("")
        logger.info("Commands:")
        logger.info("  search <query> [limit]        - Search for firms")
        logger.info("  firm <firm_id>                - Get firm details")
        logger.info("  related <frn> <kind>          - Get related data")
        logger.info("  analyze <firm_name>           - AI risk analysis")
        logger.info("  compare <firm1> vs <firm2>    - Compare two firms")
        logger.info("  permissions <firm_name>       - Analyze permissions")
        logger.info("  ask <natural_language>        - Natural language query")
        logger.info("  stats                         - Show statistics")
        logger.info("  help                          - Show this help")
        logger.info("  exit / quit                   - Exit server")
        logger.info("")

        while not self.shutdown_event.is_set():
            try:
                command = await asyncio.get_event_loop().run_in_executor(None, input, "\n> ")

                command = command.strip()
                if not command:
                    continue

                parts = command.split()
                cmd = parts[0].lower()

                if cmd in ["exit", "quit", "q"]:
                    logger.info("\n[INFO] Shutting down server...")
                    break

                elif cmd == "help":
                    self.print_help()

                elif cmd == "stats":
                    await self.print_stats()

                elif cmd == "search":
                    if len(parts) < 2:
                        logger.error("[ERROR] Usage: search <query> [limit]")
                        continue
                    query = " ".join(parts[1 : parts.index(parts[-1]) if parts[-1].isdigit() else len(parts)])
                    limit = int(parts[-1]) if parts[-1].isdigit() else 10
                    await self.handle_search(query, limit)

                elif cmd == "firm":
                    if len(parts) < 2:
                        logger.error("[ERROR] Usage: firm <firm_id>")
                        continue
                    await self.handle_firm(parts[1])

                elif cmd == "related":
                    if len(parts) < 3:
                        logger.error("[ERROR] Usage: related <frn> <kind>")
                        continue
                    await self.handle_related(parts[1], parts[2])

                elif cmd == "analyze":
                    if len(parts) < 2:
                        logger.error("[ERROR] Usage: analyze <firm_name>")
                        continue
                    firm_name = " ".join(parts[1:])
                    await self.handle_analyze(firm_name)

                elif cmd == "compare":
                    if "vs" not in command.lower():
                        logger.error("[ERROR] Usage: compare <firm1> vs <firm2>")
                        continue
                    firms = command.lower().split("vs")
                    firm1 = firms[0].replace("compare", "").strip()
                    firm2 = firms[1].strip()
                    await self.handle_compare(firm1, firm2)

                elif cmd == "permissions":
                    if len(parts) < 2:
                        logger.error("[ERROR] Usage: permissions <firm_name>")
                        continue
                    firm_name = " ".join(parts[1:])
                    await self.handle_permissions(firm_name)

                elif cmd == "ask":
                    if len(parts) < 2:
                        logger.error("[ERROR] Usage: ask <your question>")
                        continue
                    question = " ".join(parts[1:])
                    await self.handle_nl_query(question)

                else:
                    logger.error("[ERROR] Unknown command: %s", cmd)
                    logger.error("Type 'help' for available commands")

            except KeyboardInterrupt:
                logger.info("\n[INFO] Interrupt received")
                break
            except Exception as e:
                logger.error("[ERROR] Command failed: %s", e)

        self.shutdown_event.set()

    async def handle_search(self, query: str, limit: int) -> None:
        """Handle search command."""
        logger.info("\n[SEARCH] Searching for '%s' (limit: %s)...", query, limit)

        result = await self.server.handle_request(
            tool="search_firms", params={"query": query, "limit": limit}, authorization=None
        )

        if "error" in result:
            logger.error("[ERROR] %s", result["error"])
            return

        data = result.get("data", [])
        meta = result.get("meta", {})

        logger.info("\n[OK] Found %s results", meta.get("items_returned", 0))
        logger.info("Execution time: %.1fms", meta.get("execution_time_ms", 0))

        for i, firm in enumerate(data, 1):
            logger.info(
                "  %s. %s (FRN: %s) - %s",
                i,
                firm.get("firm_name"),
                firm.get("firm_id"),
                firm.get("status"),
            )

    async def handle_firm(self, firm_id: str) -> None:
        """Handle firm details command."""
        logger.info("\n[FIRM] Getting details for FRN %s...", firm_id)

        result = await self.server.handle_request(tool="firm_get", params={"firm_id": firm_id}, authorization=None)

        if "error" in result:
            logger.error("[ERROR] %s", result["error"])
            return

        data = result.get("data", {})
        logger.info("\n[OK] Firm Details:")
        logger.info("  Name: %s", data.get("firm_name"))
        logger.info("  Status: %s", data.get("status"))
        logger.info("  Type: %s", data.get("firm_type"))
        logger.info("  Companies House: %s", data.get("companies_house_number", "N/A"))

    async def handle_related(self, frn: str, kind: str) -> None:
        """Handle related data command."""
        logger.info("\n[RELATED] Getting %s for FRN %s...", kind, frn)

        result = await self.server.handle_request(
            tool="firm_related", params={"firm_id": frn, "kind": kind, "mode": "full"}, authorization=None
        )

        if "error" in result:
            logger.error("[ERROR] %s", result["error"])
            return

        data = result.get("data", [])
        meta = result.get("meta", {})

        logger.info("\n[OK] Retrieved %s items", meta.get("items_returned", 0))
        logger.info("Truncated: %s", meta.get("truncated", False))

        for i, item in enumerate(data[:5], 1):
            logger.info("  %s. %s", i, list(item.values())[:3])

        if len(data) > 5:
            logger.info("  ... and %s more items", len(data) - 5)

    async def handle_analyze(self, firm_name: str) -> None:
        """Handle AI risk analysis command."""
        analysis = await self.assistant.analyze_firm_risk(firm_name)

        if analysis["status"] == "error":
            logger.error("\n[ERROR] %s", analysis["message"])
            return

        logger.info("\n[AI ANALYSIS] %s", analysis["firm_name"])
        logger.info("%s", "=" * 70)
        logger.info("Risk Level: %s", analysis["risk_assessment"]["overall_risk"])
        logger.info("Risk Score: %s/100", analysis["risk_assessment"]["risk_score"])
        logger.info("\nRegulatory Status:")
        logger.info("  Status: %s", analysis["regulatory_status"]["status"])
        logger.info("  Type: %s", analysis["regulatory_status"]["type"])
        logger.info("  Requirements: %s", analysis["regulatory_status"]["active_requirements"])
        logger.info("  Disciplinary Actions: %s", analysis["regulatory_status"]["disciplinary_actions"])
        logger.info("\nKey Insights:")
        for insight in analysis["insights"]:
            logger.info("  - %s", insight)
        logger.info("\nRecommendation:")
        logger.info("  %s", analysis["recommendation"])

    async def handle_compare(self, firm1: str, firm2: str) -> None:
        """Handle firm comparison command."""
        comparison = await self.assistant.compare_firms(firm1, firm2)

        if comparison["status"] == "error":
            logger.error("\n[ERROR] %s", comparison["message"])
            return

        logger.info("\n[COMPARISON REPORT]")
        logger.info("%s", "=" * 70)
        logger.info("\nFirm 1: %s", comparison["firm_1"]["name"])
        logger.info(
            "  Risk: %s (%s/100)",
            comparison["firm_1"]["risk_level"],
            comparison["firm_1"]["risk_score"],
        )
        logger.info("  Disciplinary Actions: %s", comparison["firm_1"]["disciplinary_actions"])
        logger.info("\nFirm 2: %s", comparison["firm_2"]["name"])
        logger.info(
            "  Risk: %s (%s/100)",
            comparison["firm_2"]["risk_level"],
            comparison["firm_2"]["risk_score"],
        )
        logger.info("  Disciplinary Actions: %s", comparison["firm_2"]["disciplinary_actions"])
        logger.info("\nAnalysis:")
        logger.info("  %s", comparison["analysis"]["similarity"])
        logger.info("  Lower risk firm: %s", comparison["analysis"]["lower_risk_firm"])
        logger.info("\nRecommendation:")
        logger.info("  %s", comparison["recommendation"])

    async def handle_permissions(self, firm_name: str) -> None:
        """Handle permissions analysis command."""
        result = await self.assistant.get_firm_permissions_summary(firm_name)

        if result["status"] == "error":
            logger.error("\n[ERROR] %s", result["message"])
            return

        logger.info("\n[PERMISSIONS ANALYSIS] %s", result["firm_name"])
        logger.info("%s", "=" * 70)
        logger.info("Total Permissions: %s", result["total_permissions"])
        logger.info("Scope: %s", result["scope_analysis"]["scope"])
        logger.info("\nCategories:")
        for category, count in result["categories"].items():
            if count > 0:
                logger.info("  %s: %s", category.capitalize(), count)
        logger.info("\nInsights:")
        for insight in result["insights"]:
            logger.info("  - %s", insight)
        logger.info("\nTop 5 Permissions:")
        for i, perm in enumerate(result["top_permissions"], 1):
            logger.info("  %s. %s", i, perm)

    async def handle_nl_query(self, question: str) -> None:
        """Handle natural language query."""
        logger.info("\n[NL QUERY] Processing: '%s'", question)

        response = await self.nl_interface.process_query(question)
        formatted = self.nl_interface.format_response(response)

        logger.info("%s", formatted)

    async def print_stats(self) -> None:
        """Print server statistics."""
        stats = self.server.get_usage_stats()

        logger.info("\n[STATISTICS]")
        logger.info("%s", "=" * 70)
        logger.info("Total Events: %s", stats.get("total_events", 0))
        logger.info("Total Items: %s", stats.get("total_items_returned", 0))
        logger.info("Cache Hits: %s", stats.get("cache_hits", 0))
        logger.info("Cache Misses: %s", stats.get("cache_misses", 0))

        by_tool = stats.get("by_tool", {})
        if by_tool:
            logger.info("\nBy Tool:")
            for tool, count in by_tool.items():
                logger.info("  %s: %s calls", tool, count)

    def print_help(self) -> None:
        """Print help message."""
        logger.info("\n%s", "=" * 100)
        logger.info("AVAILABLE COMMANDS")
        logger.info("%s", "=" * 100)
        logger.info("")
        logger.info("MCP Tools:")
        logger.info("  search <query> [limit]        - Search for firms")
        logger.info("  firm <firm_id>                - Get firm details")
        logger.info("  related <frn> <kind>          - Get related data (permissions, history, etc.)")
        logger.info("")
        logger.info("AI Analysis:")
        logger.info("  analyze <firm_name>           - Comprehensive risk analysis")
        logger.info("  compare <firm1> vs <firm2>    - Compare two firms")
        logger.info("  permissions <firm_name>       - Analyze firm permissions")
        logger.info("")
        logger.info("LLM Integration:")
        logger.info("  ask <question>                - Natural language query")
        logger.info("    Examples:")
        logger.info("      ask What is the risk profile of Barclays?")
        logger.info("      ask Compare Barclays vs HSBC")
        logger.info("      ask What permissions does Lloyds have?")
        logger.info("")
        logger.info("System:")
        logger.info("  stats                         - Show usage statistics")
        logger.info("  help                          - Show this help")
        logger.info("  exit / quit                   - Exit server")
        logger.info("")
        logger.info("Available data kinds: names, addresses, permissions, individuals, history,")
        logger.info("                      requirements, waivers, exclusions, passports, regulators,")
        logger.info("                      appointed_representatives, controlled_functions")
        logger.info("")

    async def shutdown(self) -> None:
        """Shutdown server gracefully."""
        if self.server:
            logger.info("\n[INFO] Closing server connections...")
            await self.server.close()
            logger.info("[OK] Server closed successfully")

    async def run(self, interactive: bool = True, enable_auth: bool = False) -> None:
        """Run the complete server."""
        await self.start(enable_auth)

        if interactive:
            await self.interactive_mode()
        else:
            logger.info("[INFO] Running in non-interactive mode")
            logger.info("[INFO] Press Ctrl+C to stop")
            await self.shutdown_event.wait()

        await self.shutdown()
