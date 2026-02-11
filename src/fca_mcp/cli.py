"""
FCA MCP Server with AI Analysis - Complete Production System.

This is the unified server combining MCP protocol, AI analysis, and LLM integration.
Run this single file to access all FCA regulatory data analysis features.
"""

import argparse
import asyncio
import json
import logging
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Any

import typer
import uvicorn

import fca_mcp

logger = logging.getLogger(__name__)

# ============================================================================
# AI ASSISTANT - Risk Analysis and Insights
# ============================================================================


class FcaAiAssistant:
    """AI Assistant that analyzes FCA financial data."""

    def __init__(self, server):
        """Initialize AI Assistant with MCP server."""
        self.server = server
        self.context = {}

    async def analyze_firm_risk(self, firm_name: str) -> dict[str, Any]:
        """Analyze firm's regulatory risk profile with comprehensive insights."""
        logger.info("\n[AI] Analyzing risk profile for '%s'...", firm_name)

        search_result = await self.server.handle_request(
            tool="search_firms", params={"query": firm_name, "limit": 1}, authorization=None
        )

        if "error" in search_result or not search_result.get("data"):
            return {
                "status": "error",
                "message": f"Firm '{firm_name}' not found",
                "recommendation": "Please check the firm name and try again",
            }

        firm = search_result["data"][0]
        firm_id = firm.get("firm_id")
        firm_status = firm.get("status")

        logger.info("   [+] Found: %s (FRN: %s)", firm.get("firm_name"), firm_id)

        details_result = await self.server.handle_request(
            tool="firm_get", params={"firm_id": firm_id}, authorization=None
        )

        firm_details = details_result.get("data", {})

        history_result = await self.server.handle_request(
            tool="firm_related", params={"firm_id": firm_id, "kind": "history", "mode": "full"}, authorization=None
        )

        history = history_result.get("data", [])

        requirements_result = await self.server.handle_request(
            tool="firm_related", params={"firm_id": firm_id, "kind": "requirements", "mode": "full"}, authorization=None
        )

        requirements = requirements_result.get("data", [])

        risk_score = self._calculate_risk_score(firm_status, history, requirements)
        insights = self._generate_insights(firm_details, history, requirements)

        analysis = {
            "status": "success",
            "firm_name": firm.get("firm_name"),
            "frn": firm_id,
            "analysis_date": datetime.now().isoformat(),
            "risk_assessment": {
                "overall_risk": risk_score["level"],
                "risk_score": risk_score["score"],
                "factors": risk_score["factors"],
            },
            "regulatory_status": {
                "status": firm_status,
                "type": firm_details.get("firm_type"),
                "active_requirements": len(requirements),
                "disciplinary_actions": len(history),
            },
            "insights": insights,
            "recommendation": self._generate_recommendation(risk_score, history),
        }

        return analysis

    def _calculate_risk_score(self, status: str, history: list, requirements: list) -> dict:
        """Calculate risk score based on regulatory data."""
        score = 0
        factors = []

        if "unauthorised" in status.lower():
            score += 50
            factors.append("Unauthorized status - HIGH RISK")
        elif "no longer" in status.lower():
            score += 30
            factors.append("No longer authorized - MEDIUM RISK")
        elif "authorised" in status.lower():
            score += 0
            factors.append("Currently authorized - LOW RISK")

        if len(history) > 10:
            score += 40
            factors.append(f"Extensive disciplinary history ({len(history)} actions) - HIGH RISK")
        elif len(history) > 5:
            score += 25
            factors.append(f"Significant disciplinary history ({len(history)} actions) - MEDIUM RISK")
        elif len(history) > 0:
            score += 10
            factors.append(f"Some disciplinary history ({len(history)} actions) - LOW RISK")
        else:
            factors.append("No disciplinary history - POSITIVE")

        if len(requirements) > 8:
            score += 20
            factors.append(f"Many regulatory requirements ({len(requirements)}) - MEDIUM RISK")
        elif len(requirements) > 0:
            score += 5
            factors.append(f"Some regulatory requirements ({len(requirements)}) - LOW RISK")

        if score >= 60:
            level = "HIGH RISK"
        elif score >= 30:
            level = "MEDIUM RISK"
        else:
            level = "LOW RISK"

        return {"score": score, "level": level, "factors": factors}

    def _generate_insights(self, details: dict, history: list, requirements: list) -> list[str]:
        """Generate insights from regulatory data."""
        insights = []

        firm_type = details.get("firm_type", "")
        if firm_type:
            insights.append(f"Firm is classified as '{firm_type}'")

        if details.get("companies_house_number"):
            insights.append(f"Registered with Companies House: {details['companies_house_number']}")

        if history:
            action_types = {}
            for item in history:
                action_type = item.get("action_type", "Unknown")
                action_types[action_type] = action_types.get(action_type, 0) + 1

            for action, count in action_types.items():
                insights.append(f"Has {count} {action} action(s) on record")
        else:
            insights.append("No disciplinary actions recorded - positive compliance history")

        if requirements:
            insights.append(f"Subject to {len(requirements)} regulatory requirements")

        return insights

    def _generate_recommendation(self, risk_score: dict, history: list) -> str:
        """Generate actionable recommendation."""
        level = risk_score["level"]

        if level == "HIGH RISK":
            return (
                "HIGH RISK: This firm presents significant regulatory concerns. "
                "Recommend thorough due diligence before any business engagement."
            )
        elif level == "MEDIUM RISK":
            return (
                "MEDIUM RISK: This firm has some regulatory concerns. "
                "Review disciplinary history and requirements carefully."
            )
        else:
            return (
                "LOW RISK: This firm has a good regulatory standing. "
                "Standard due diligence procedures should be sufficient."
            )

    async def compare_firms(self, firm1_name: str, firm2_name: str) -> dict[str, Any]:
        """Compare two firms side by side."""
        logger.info("\n[AI] Comparing '%s' vs '%s'...", firm1_name, firm2_name)

        analysis1 = await self.analyze_firm_risk(firm1_name)
        await asyncio.sleep(0.5)
        analysis2 = await self.analyze_firm_risk(firm2_name)

        if analysis1["status"] == "error" or analysis2["status"] == "error":
            return {"status": "error", "message": "Could not analyze one or both firms"}

        score1 = analysis1["risk_assessment"]["risk_score"]
        score2 = analysis2["risk_assessment"]["risk_score"]
        diff = abs(score1 - score2)

        if diff < 10:
            similarity = "Very similar risk profiles"
        elif diff < 30:
            similarity = "Somewhat different risk profiles"
        else:
            similarity = "Significantly different risk profiles"

        lower_risk = analysis1["firm_name"] if score1 < score2 else analysis2["firm_name"]

        comparison = {
            "status": "success",
            "comparison_date": datetime.now().isoformat(),
            "firm_1": {
                "name": analysis1["firm_name"],
                "frn": analysis1["frn"],
                "risk_level": analysis1["risk_assessment"]["overall_risk"],
                "risk_score": score1,
                "disciplinary_actions": analysis1["regulatory_status"]["disciplinary_actions"],
            },
            "firm_2": {
                "name": analysis2["firm_name"],
                "frn": analysis2["frn"],
                "risk_level": analysis2["risk_assessment"]["overall_risk"],
                "risk_score": score2,
                "disciplinary_actions": analysis2["regulatory_status"]["disciplinary_actions"],
            },
            "analysis": {
                "similarity": similarity,
                "lower_risk_firm": lower_risk,
                "risk_difference": diff,
                "score_difference": score2 - score1,
            },
            "recommendation": (
                f"Based on regulatory data, {lower_risk} presents a lower risk profile. "
                f"Consider this for lower-risk engagement, but conduct thorough due diligence on both."
            ),
        }

        return comparison

    async def get_firm_permissions_summary(self, firm_name: str) -> dict[str, Any]:
        """Get comprehensive permissions summary with analysis."""
        logger.info("\n[AI] Analyzing permissions for '%s'...", firm_name)

        search_result = await self.server.handle_request(
            tool="search_firms", params={"query": firm_name, "limit": 1}, authorization=None
        )

        if "error" in search_result or not search_result.get("data"):
            return {"status": "error", "message": f"Firm '{firm_name}' not found"}

        firm = search_result["data"][0]
        firm_id = firm.get("firm_id")

        perms_result = await self.server.handle_request(
            tool="firm_related", params={"firm_id": firm_id, "kind": "permissions", "mode": "full"}, authorization=None
        )

        permissions = perms_result.get("data", [])

        categories = self._categorize_permissions(permissions)

        has_limitations = sum(1 for p in permissions if p.get("limitations"))

        insights = []
        if len(permissions) > 30:
            insights.append(f"Extensive authorization with {len(permissions)} permissions")
        elif len(permissions) > 15:
            insights.append(f"Moderate authorization with {len(permissions)} permissions")
        else:
            insights.append(f"Limited authorization with {len(permissions)} permissions")

        top_category = max(categories.items(), key=lambda x: x[1])
        if top_category[1] > 0:
            insights.append(f"Primary focus on {top_category[0]} activities ({top_category[1]} permissions)")

        return {
            "status": "success",
            "firm_name": firm.get("firm_name"),
            "frn": firm_id,
            "total_permissions": len(permissions),
            "categories": categories,
            "scope_analysis": {
                "unrestricted_permissions": len(permissions) - has_limitations,
                "restricted_permissions": has_limitations,
                "scope": "Broad" if has_limitations < len(permissions) * 0.3 else "Restricted",
            },
            "insights": insights,
            "top_permissions": [p["permission_name"] for p in permissions[:5]],
        }

    def _categorize_permissions(self, permissions: list) -> dict:
        """Categorize permissions by type."""
        categories = {"investment": 0, "lending": 0, "insurance": 0, "payment": 0, "advisory": 0, "other": 0}

        for perm in permissions:
            name = perm.get("permission_name", "").lower()

            if any(word in name for word in ["investment", "portfolio", "fund", "securities"]):
                categories["investment"] += 1
            elif any(word in name for word in ["lending", "credit", "loan", "mortgage"]):
                categories["lending"] += 1
            elif any(word in name for word in ["insurance", "underwriting"]):
                categories["insurance"] += 1
            elif any(word in name for word in ["payment", "money", "transfer"]):
                categories["payment"] += 1
            elif any(word in name for word in ["advising", "advisory", "consultation"]):
                categories["advisory"] += 1
            else:
                categories["other"] += 1

        return categories


# ============================================================================
# NATURAL LANGUAGE INTERFACE - LLM Integration
# ============================================================================


class NaturalLanguageInterface:
    """Natural language interface for FCA data queries."""

    def __init__(self, assistant: FcaAiAssistant):
        """Initialize with AI assistant."""
        self.assistant = assistant

    async def process_query(self, query: str) -> dict:
        """Process natural language query and return structured response."""
        query_lower = query.lower()

        if "risk" in query_lower or "safe" in query_lower or "analyze" in query_lower:
            firm_name = self._extract_firm_name(query)
            if firm_name:
                return await self.assistant.analyze_firm_risk(firm_name)
            else:
                return {"status": "error", "message": "Please specify a firm name"}

        elif "compare" in query_lower or "versus" in query_lower or "vs" in query_lower:
            firms = self._extract_multiple_firms(query)
            if len(firms) >= 2:
                return await self.assistant.compare_firms(firms[0], firms[1])
            else:
                return {"status": "error", "message": "Please specify two firms to compare"}

        elif "permission" in query_lower or "authorized" in query_lower or "license" in query_lower:
            firm_name = self._extract_firm_name(query)
            if firm_name:
                return await self.assistant.get_firm_permissions_summary(firm_name)
            else:
                return {"status": "error", "message": "Please specify a firm name"}

        else:
            return {
                "status": "help",
                "message": "I can help you with:",
                "capabilities": [
                    "Analyze firm risk: 'What is the risk profile of Barclays?'",
                    "Compare firms: 'Compare Barclays vs HSBC'",
                    "Check permissions: 'What permissions does Lloyds have?'",
                ],
            }

    def _extract_firm_name(self, query: str) -> str:
        """Extract firm name from query."""
        firms = ["barclays", "hsbc", "lloyds", "natwest", "santander", "rbs", "nationwide"]

        query_lower = query.lower()
        for firm in firms:
            if firm in query_lower:
                return firm.capitalize()

        if '"' in query:
            parts = query.split('"')
            if len(parts) >= 2:
                return parts[1]

        return ""

    def _extract_multiple_firms(self, query: str) -> list[str]:
        """Extract multiple firm names from comparison query."""
        firms = []

        if " vs " in query.lower():
            parts = query.lower().split(" vs ")
        elif " versus " in query.lower():
            parts = query.lower().split(" versus ")
        elif " and " in query.lower():
            parts = query.lower().split(" and ")
        else:
            return []

        for part in parts[:2]:
            firm = self._extract_firm_name(part)
            if firm:
                firms.append(firm)

        return firms

    def format_response(self, response: dict) -> str:
        """Format response for human-readable output."""
        if response.get("status") == "error":
            return f"[ERROR] {response['message']}"

        if response.get("status") == "help":
            output = f"\n{response['message']}\n"
            for cap in response["capabilities"]:
                output += f"   - {cap}\n"
            return output

        if "risk_assessment" in response:
            output = f"\n[RISK ANALYSIS] {response['firm_name']}\n"
            output += f"{'=' * 70}\n"
            output += f"Risk Level: {response['risk_assessment']['overall_risk']}\n"
            output += f"Risk Score: {response['risk_assessment']['risk_score']}/100\n"
            output += "\nKey Insights:\n"
            for insight in response["insights"]:
                output += f"   - {insight}\n"
            output += "\nRecommendation:\n"
            output += f"   {response['recommendation']}\n"
            return output

        if "firm_1" in response and "firm_2" in response:
            output = "\n[COMPARISON REPORT]\n"
            output += f"{'=' * 70}\n"
            output += f"\nFirm 1: {response['firm_1']['name']}\n"
            output += f"   Risk: {response['firm_1']['risk_level']} ({response['firm_1']['risk_score']}/100)\n"
            output += f"\nFirm 2: {response['firm_2']['name']}\n"
            output += f"   Risk: {response['firm_2']['risk_level']} ({response['firm_2']['risk_score']}/100)\n"
            output += f"\n{response['analysis']['similarity']}\n"
            output += f"Lower risk: {response['analysis']['lower_risk_firm']}\n"
            output += f"\n{response['recommendation']}\n"
            return output

        if "total_permissions" in response:
            output = f"\n[PERMISSIONS] {response['firm_name']}\n"
            output += f"{'=' * 70}\n"
            output += f"Total: {response['total_permissions']}\n"
            output += f"Scope: {response['scope_analysis']['scope']}\n"
            output += "\nInsights:\n"
            for insight in response["insights"]:
                output += f"   - {insight}\n"
            return output

        return json.dumps(response, indent=2)


# ============================================================================
# SERVER RUNNER - Complete Management System
# ============================================================================


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


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
app = typer.Typer(pretty_exceptions_enable=False)


@app.callback(invoke_without_command=True)
def startup(ctx: typer.Context):
    """Startup callback that runs before any command."""
    fca_mcp.logging.configure()
    logger.info("Fca Mcp CLI started.")


@app.command()
def main_http_mode(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run HTTP server mode (synchronous entry point)."""
    logger.info("[HTTP] Starting server on %s:%s", host, port)
    logger.info(
        "[HTTP] Web UI: http://%s:%s",
        host,
        port,
    )
    logger.info(
        "[HTTP] API Docs: http://%s:%s/docs",
        host,
        port,
    )

    # uvicorn.run manages its own event loop
    uvicorn.run("fca_mcp.uvcorn_app:get_fastapi_app", host=host, port=port, log_level="info", factory=True)


@app.command()
async def main(interactive: bool = True, enable_auth: bool = True) -> None:
    """Main entry point for the FCA MCP Server (CLI mode only)."""
    # parser = argparse.ArgumentParser(
    #     description="FCA MCP Server with AI Analysis",
    #     formatter_class=argparse.RawDescriptionHelpFormatter,
    #     epilog=textwrap.dedent("""
    #         Examples:
    #         python fca_mcp_server.py                    # Interactive mode
    #         python fca_mcp_server.py --no-interactive   # Non-interactive mode
    #         python fca_mcp_server.py --http-mode        # HTTP server mode
    #         python fca_mcp_server.py --enable-auth      # With OAuth authentication

    #         Interactive commands:
    #         search Barclays                             # Search for firms
    #         firm 122702                                 # Get firm details
    #         analyze Barclays Bank                       # AI risk analysis
    #         compare Barclays vs HSBC                    # Compare firms
    #         ask What is the risk of Barclays?          # Natural language query

    #         HTTP endpoints:
    #         GET  /                                       # Web UI
    #         GET  /health                                 # Health check
    #         POST /api/search                             # Search firms
    #         POST /api/analyze                            # Analyze firm
    #         POST /api/compare                            # Compare firms
    #         POST /api/ask                                # Natural language query
    #     """),
    # )
    # args = parser.parse_args()

    # CLI mode only
    runner = FcaMcpServerRunner()

    def signal_handler(sig, frame):
        runner.shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await runner.run(interactive=interactive, enable_auth=enable_auth)


def run_main() -> None:
    """Entry point that handles asyncio context."""
    # Pre-parse to check for HTTP mode
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--http-mode", action="store_true")
    args, _ = parser.parse_known_args()

    if args.http_mode:
        # HTTP mode: call synchronous HTTP function
        main_http_mode()
    else:
        # CLI mode: wrap async main in asyncio.run
        asyncio.run(main())


if __name__ == "__main__":
    run_main()
