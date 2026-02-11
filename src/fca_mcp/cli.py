"""
FCA MCP Server with AI Analysis - Complete Production System.

This is the unified server combining MCP protocol, AI analysis, and LLM integration.
Run this single file to access all FCA regulatory data analysis features.
"""

import argparse
import asyncio
import json
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Any

from fca_mcp.server.main import create_server

# Try to import FastAPI for HTTP mode
try:
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, JSONResponse
    from pydantic import BaseModel

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    HTTPException = None
    JSONResponse = None
    HTMLResponse = None
    BaseModel = None


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
        print(f"\n[AI] Analyzing risk profile for '{firm_name}'...")

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

        print(f"   [+] Found: {firm.get('firm_name')} (FRN: {firm_id})")

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
        print(f"\n[AI] Comparing '{firm1_name}' vs '{firm2_name}'...")

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
        print(f"\n[AI] Analyzing permissions for '{firm_name}'...")

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
        print("=" * 100)
        print("FCA MCP SERVER WITH AI ANALYSIS")
        print("=" * 100)
        print()

        fca_email = os.getenv("FCA_API_EMAIL")
        fca_key = os.getenv("FCA_API_KEY")

        if not fca_email or not fca_key:
            print("[ERROR] Missing FCA API credentials!")
            print("Set FCA_API_EMAIL and FCA_API_KEY in .env file")
            return

        print("[INIT] Connecting to FCA API...")
        print(f"  Email: {fca_email}")
        print(f"  API Key: {'*' * 32}")
        print(f"  Auth: {enable_auth}")
        print()

        try:
            self.server = await create_server(fca_email=fca_email, fca_key=fca_key, enable_auth=enable_auth)

            self.assistant = FcaAiAssistant(self.server)
            self.nl_interface = NaturalLanguageInterface(self.assistant)

            print("[OK] Server started successfully!")
            print()
            print("Available Features:")
            print("  [1] MCP Tools: search_firms, firm_get, firm_related")
            print("  [2] AI Analysis: Risk scoring, firm comparison, insights")
            print("  [3] NL Interface: Natural language queries for LLMs")
            print()

        except Exception as e:
            print(f"[ERROR] Failed to start server: {e}")
            raise

    async def interactive_mode(self) -> None:
        """Run server in interactive mode with advanced commands."""
        print("=" * 100)
        print("INTERACTIVE MODE - Advanced Interface")
        print("=" * 100)
        print()
        print("Commands:")
        print("  search <query> [limit]        - Search for firms")
        print("  firm <firm_id>                - Get firm details")
        print("  related <frn> <kind>          - Get related data")
        print("  analyze <firm_name>           - AI risk analysis")
        print("  compare <firm1> vs <firm2>    - Compare two firms")
        print("  permissions <firm_name>       - Analyze permissions")
        print("  ask <natural_language>        - Natural language query")
        print("  stats                         - Show statistics")
        print("  help                          - Show this help")
        print("  exit / quit                   - Exit server")
        print()

        while not self.shutdown_event.is_set():
            try:
                command = await asyncio.get_event_loop().run_in_executor(None, input, "\n> ")

                command = command.strip()
                if not command:
                    continue

                parts = command.split()
                cmd = parts[0].lower()

                if cmd in ["exit", "quit", "q"]:
                    print("\n[INFO] Shutting down server...")
                    break

                elif cmd == "help":
                    self.print_help()

                elif cmd == "stats":
                    await self.print_stats()

                elif cmd == "search":
                    if len(parts) < 2:
                        print("[ERROR] Usage: search <query> [limit]")
                        continue
                    query = " ".join(parts[1 : parts.index(parts[-1]) if parts[-1].isdigit() else len(parts)])
                    limit = int(parts[-1]) if parts[-1].isdigit() else 10
                    await self.handle_search(query, limit)

                elif cmd == "firm":
                    if len(parts) < 2:
                        print("[ERROR] Usage: firm <firm_id>")
                        continue
                    await self.handle_firm(parts[1])

                elif cmd == "related":
                    if len(parts) < 3:
                        print("[ERROR] Usage: related <frn> <kind>")
                        continue
                    await self.handle_related(parts[1], parts[2])

                elif cmd == "analyze":
                    if len(parts) < 2:
                        print("[ERROR] Usage: analyze <firm_name>")
                        continue
                    firm_name = " ".join(parts[1:])
                    await self.handle_analyze(firm_name)

                elif cmd == "compare":
                    if "vs" not in command.lower():
                        print("[ERROR] Usage: compare <firm1> vs <firm2>")
                        continue
                    firms = command.lower().split("vs")
                    firm1 = firms[0].replace("compare", "").strip()
                    firm2 = firms[1].strip()
                    await self.handle_compare(firm1, firm2)

                elif cmd == "permissions":
                    if len(parts) < 2:
                        print("[ERROR] Usage: permissions <firm_name>")
                        continue
                    firm_name = " ".join(parts[1:])
                    await self.handle_permissions(firm_name)

                elif cmd == "ask":
                    if len(parts) < 2:
                        print("[ERROR] Usage: ask <your question>")
                        continue
                    question = " ".join(parts[1:])
                    await self.handle_nl_query(question)

                else:
                    print(f"[ERROR] Unknown command: {cmd}")
                    print("Type 'help' for available commands")

            except KeyboardInterrupt:
                print("\n[INFO] Interrupt received")
                break
            except Exception as e:
                print(f"[ERROR] Command failed: {e}")

        self.shutdown_event.set()

    async def handle_search(self, query: str, limit: int) -> None:
        """Handle search command."""
        print(f"\n[SEARCH] Searching for '{query}' (limit: {limit})...")

        result = await self.server.handle_request(
            tool="search_firms", params={"query": query, "limit": limit}, authorization=None
        )

        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return

        data = result.get("data", [])
        meta = result.get("meta", {})

        print(f"\n[OK] Found {meta.get('items_returned', 0)} results")
        print(f"Execution time: {meta.get('execution_time_ms', 0):.1f}ms")

        for i, firm in enumerate(data, 1):
            print(f"  {i}. {firm.get('firm_name')} (FRN: {firm.get('firm_id')}) - {firm.get('status')}")

    async def handle_firm(self, firm_id: str) -> None:
        """Handle firm details command."""
        print(f"\n[FIRM] Getting details for FRN {firm_id}...")

        result = await self.server.handle_request(tool="firm_get", params={"firm_id": firm_id}, authorization=None)

        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return

        data = result.get("data", {})
        print("\n[OK] Firm Details:")
        print(f"  Name: {data.get('firm_name')}")
        print(f"  Status: {data.get('status')}")
        print(f"  Type: {data.get('firm_type')}")
        print(f"  Companies House: {data.get('companies_house_number', 'N/A')}")

    async def handle_related(self, frn: str, kind: str) -> None:
        """Handle related data command."""
        print(f"\n[RELATED] Getting {kind} for FRN {frn}...")

        result = await self.server.handle_request(
            tool="firm_related", params={"firm_id": frn, "kind": kind, "mode": "full"}, authorization=None
        )

        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return

        data = result.get("data", [])
        meta = result.get("meta", {})

        print(f"\n[OK] Retrieved {meta.get('items_returned', 0)} items")
        print(f"Truncated: {meta.get('truncated', False)}")

        for i, item in enumerate(data[:5], 1):
            print(f"  {i}. {list(item.values())[:3]}")

        if len(data) > 5:
            print(f"  ... and {len(data) - 5} more items")

    async def handle_analyze(self, firm_name: str) -> None:
        """Handle AI risk analysis command."""
        analysis = await self.assistant.analyze_firm_risk(firm_name)

        if analysis["status"] == "error":
            print(f"\n[ERROR] {analysis['message']}")
            return

        print(f"\n[AI ANALYSIS] {analysis['firm_name']}")
        print(f"{'=' * 70}")
        print(f"Risk Level: {analysis['risk_assessment']['overall_risk']}")
        print(f"Risk Score: {analysis['risk_assessment']['risk_score']}/100")
        print("\nRegulatory Status:")
        print(f"  Status: {analysis['regulatory_status']['status']}")
        print(f"  Type: {analysis['regulatory_status']['type']}")
        print(f"  Requirements: {analysis['regulatory_status']['active_requirements']}")
        print(f"  Disciplinary Actions: {analysis['regulatory_status']['disciplinary_actions']}")
        print("\nKey Insights:")
        for insight in analysis["insights"]:
            print(f"  - {insight}")
        print("\nRecommendation:")
        print(f"  {analysis['recommendation']}")

    async def handle_compare(self, firm1: str, firm2: str) -> None:
        """Handle firm comparison command."""
        comparison = await self.assistant.compare_firms(firm1, firm2)

        if comparison["status"] == "error":
            print(f"\n[ERROR] {comparison['message']}")
            return

        print("\n[COMPARISON REPORT]")
        print(f"{'=' * 70}")
        print(f"\nFirm 1: {comparison['firm_1']['name']}")
        print(f"  Risk: {comparison['firm_1']['risk_level']} ({comparison['firm_1']['risk_score']}/100)")
        print(f"  Disciplinary Actions: {comparison['firm_1']['disciplinary_actions']}")
        print(f"\nFirm 2: {comparison['firm_2']['name']}")
        print(f"  Risk: {comparison['firm_2']['risk_level']} ({comparison['firm_2']['risk_score']}/100)")
        print(f"  Disciplinary Actions: {comparison['firm_2']['disciplinary_actions']}")
        print("\nAnalysis:")
        print(f"  {comparison['analysis']['similarity']}")
        print(f"  Lower risk firm: {comparison['analysis']['lower_risk_firm']}")
        print("\nRecommendation:")
        print(f"  {comparison['recommendation']}")

    async def handle_permissions(self, firm_name: str) -> None:
        """Handle permissions analysis command."""
        result = await self.assistant.get_firm_permissions_summary(firm_name)

        if result["status"] == "error":
            print(f"\n[ERROR] {result['message']}")
            return

        print(f"\n[PERMISSIONS ANALYSIS] {result['firm_name']}")
        print(f"{'=' * 70}")
        print(f"Total Permissions: {result['total_permissions']}")
        print(f"Scope: {result['scope_analysis']['scope']}")
        print("\nCategories:")
        for category, count in result["categories"].items():
            if count > 0:
                print(f"  {category.capitalize()}: {count}")
        print("\nInsights:")
        for insight in result["insights"]:
            print(f"  - {insight}")
        print("\nTop 5 Permissions:")
        for i, perm in enumerate(result["top_permissions"], 1):
            print(f"  {i}. {perm}")

    async def handle_nl_query(self, question: str) -> None:
        """Handle natural language query."""
        print(f"\n[NL QUERY] Processing: '{question}'")

        response = await self.nl_interface.process_query(question)
        formatted = self.nl_interface.format_response(response)

        print(formatted)

    async def print_stats(self) -> None:
        """Print server statistics."""
        stats = self.server.get_usage_stats()

        print("\n[STATISTICS]")
        print(f"{'=' * 70}")
        print(f"Total Events: {stats.get('total_events', 0)}")
        print(f"Total Items: {stats.get('total_items_returned', 0)}")
        print(f"Cache Hits: {stats.get('cache_hits', 0)}")
        print(f"Cache Misses: {stats.get('cache_misses', 0)}")

        by_tool = stats.get("by_tool", {})
        if by_tool:
            print("\nBy Tool:")
            for tool, count in by_tool.items():
                print(f"  {tool}: {count} calls")

    def print_help(self) -> None:
        """Print help message."""
        print("\n" + "=" * 100)
        print("AVAILABLE COMMANDS")
        print("=" * 100)
        print()
        print("MCP Tools:")
        print("  search <query> [limit]        - Search for firms")
        print("  firm <firm_id>                - Get firm details")
        print("  related <frn> <kind>          - Get related data (permissions, history, etc.)")
        print()
        print("AI Analysis:")
        print("  analyze <firm_name>           - Comprehensive risk analysis")
        print("  compare <firm1> vs <firm2>    - Compare two firms")
        print("  permissions <firm_name>       - Analyze firm permissions")
        print()
        print("LLM Integration:")
        print("  ask <question>                - Natural language query")
        print("    Examples:")
        print("      ask What is the risk profile of Barclays?")
        print("      ask Compare Barclays vs HSBC")
        print("      ask What permissions does Lloyds have?")
        print()
        print("System:")
        print("  stats                         - Show usage statistics")
        print("  help                          - Show this help")
        print("  exit / quit                   - Exit server")
        print()
        print("Available data kinds: names, addresses, permissions, individuals, history,")
        print("                      requirements, waivers, exclusions, passports, regulators,")
        print("                      appointed_representatives, controlled_functions")
        print()

    async def shutdown(self) -> None:
        """Shutdown server gracefully."""
        if self.server:
            print("\n[INFO] Closing server connections...")
            await self.server.close()
            print("[OK] Server closed successfully")

    async def run(self, interactive: bool = True, enable_auth: bool = False) -> None:
        """Run the complete server."""
        await self.start(enable_auth)

        if interactive:
            await self.interactive_mode()
        else:
            print("[INFO] Running in non-interactive mode")
            print("[INFO] Press Ctrl+C to stop")
            await self.shutdown_event.wait()

        await self.shutdown()


# ============================================================================
# HTTP API SERVER - Web Interface
# ============================================================================

if FASTAPI_AVAILABLE:
    from contextlib import asynccontextmanager

    # Global server instances
    _global_server = None
    _global_assistant = None
    _global_nl_interface = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Manage application lifespan - startup and shutdown."""
        global _global_server, _global_assistant, _global_nl_interface

        fca_email = os.getenv("FCA_API_EMAIL")
        fca_key = os.getenv("FCA_API_KEY")

        if not fca_email or not fca_key:
            print("[ERROR] Missing FCA API credentials in environment")
            yield
            return

        _global_server = await create_server(fca_email=fca_email, fca_key=fca_key, enable_auth=False)

        _global_assistant = FcaAiAssistant(_global_server)
        _global_nl_interface = NaturalLanguageInterface(_global_assistant)

        print("[HTTP] Server initialized successfully")

        yield

        if _global_server:
            await _global_server.close()
            print("[HTTP] Server closed")

    app = FastAPI(
        title="FCA MCP Server API",
        description="HTTP API for FCA regulatory data with AI analysis",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class SearchRequest(BaseModel):
        query: str
        limit: int = 10

    class AnalyzeRequest(BaseModel):
        firm_name: str

    class CompareRequest(BaseModel):
        firm1: str
        firm2: str

    class NLQueryRequest(BaseModel):
        question: str

    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Root endpoint with HTML interface."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>FCA MCP Server</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }
                .card {
                    background: white;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .endpoint {
                    background: #f8f9fa;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #667eea;
                    border-radius: 4px;
                }
                .method {
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    margin-right: 10px;
                }
                .get { background: #61affe; color: white; }
                .post { background: #49cc90; color: white; }
                code {
                    background: #e9ecef;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: monospace;
                }
                .feature {
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 6px 12px;
                    margin: 5px;
                    border-radius: 20px;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏛️ FCA MCP Server</h1>
                <p>AI-Powered UK Financial Conduct Authority Data Analysis</p>
                <div>
                    <span class="feature">MCP Protocol</span>
                    <span class="feature">AI Analysis</span>
                    <span class="feature">Risk Scoring</span>
                    <span class="feature">LLM Integration</span>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 System Status</h2>
                <p>✅ Server is running and ready</p>
                <p>✅ FCA API connected</p>
                <p>✅ AI Assistant active</p>
            </div>
            
            <div class="card">
                <h2>🔌 API Endpoints</h2>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/health</code>
                    <p>Health check endpoint</p>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/docs</code>
                    <p>Interactive API documentation (Swagger UI)</p>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/api/search</code>
                    <p>Search for firms by name</p>
                    <pre>{"query": "Barclays", "limit": 10}</pre>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/api/analyze</code>
                    <p>AI risk analysis of a firm</p>
                    <pre>{"firm_name": "Barclays Bank"}</pre>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/api/compare</code>
                    <p>Compare two firms</p>
                    <pre>{"firm1": "Barclays", "firm2": "HSBC"}</pre>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/api/ask</code>
                    <p>Natural language query</p>
                    <pre>{"question": "Is Barclays Bank safe?"}</pre>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/api/stats</code>
                    <p>Server usage statistics</p>
                </div>
            </div>
            
            <div class="card">
                <h2>📚 Quick Start</h2>
                <p><strong>1. View API Documentation:</strong></p>
                <p><a href="/docs" target="_blank">Open Swagger UI</a></p>
                
                <p><strong>2. Try an example:</strong></p>
                <pre>curl -X POST http://localhost:8000/api/search \\
  -H "Content-Type: application/json" \\
  -d '{"query": "Barclays", "limit": 5}'</pre>
            </div>
            
            <div class="card">
                <h2>ℹ️ About</h2>
                <p>This server provides:</p>
                <ul>
                    <li>✅ Complete access to FCA Financial Services Register</li>
                    <li>✅ AI-powered risk analysis (0-100 scoring)</li>
                    <li>✅ Firm comparison and insights</li>
                    <li>✅ Permission categorization and analysis</li>
                    <li>✅ Natural language query processing</li>
                    <li>✅ RESTful HTTP API</li>
                </ul>
            </div>
        </body>
        </html>
        """

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "FCA MCP Server",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "features": {"mcp_tools": True, "ai_analysis": True, "nl_interface": True},
        }

    @app.post("/api/search")
    async def search_firms(request: SearchRequest):
        """Search for firms."""
        if not _global_server:
            raise HTTPException(status_code=503, detail="Server not initialized")

        result = await _global_server.handle_request(
            tool="search_firms", params={"query": request.query, "limit": request.limit}, authorization=None
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    @app.post("/api/analyze")
    async def analyze_firm(request: AnalyzeRequest):
        """AI risk analysis of a firm."""
        if not _global_assistant:
            raise HTTPException(status_code=503, detail="AI Assistant not initialized")

        analysis = await _global_assistant.analyze_firm_risk(request.firm_name)

        if analysis["status"] == "error":
            raise HTTPException(status_code=404, detail=analysis["message"])

        return analysis

    @app.post("/api/compare")
    async def compare_firms(request: CompareRequest):
        """Compare two firms."""
        if not _global_assistant:
            raise HTTPException(status_code=503, detail="AI Assistant not initialized")

        comparison = await _global_assistant.compare_firms(request.firm1, request.firm2)

        if comparison["status"] == "error":
            raise HTTPException(status_code=400, detail=comparison["message"])

        return comparison

    @app.post("/api/ask")
    async def natural_language_query(request: NLQueryRequest):
        """Process natural language query."""
        if not _global_nl_interface:
            raise HTTPException(status_code=503, detail="NL Interface not initialized")

        response = await _global_nl_interface.process_query(request.question)
        return response

    @app.get("/api/stats")
    async def get_stats():
        """Get server statistics."""
        if not _global_server:
            raise HTTPException(status_code=503, detail="Server not initialized")

        return _global_server.get_usage_stats()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main_http_mode() -> None:
    """Run HTTP server mode (synchronous entry point)."""
    parser = argparse.ArgumentParser(
        description="FCA MCP Server - HTTP Mode", formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--http-mode", action="store_true", required=False)
    parser.add_argument("--host", default="0.0.0.0", help="HTTP server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="HTTP server port (default: 8000)")
    args, _ = parser.parse_known_args()

    if not FASTAPI_AVAILABLE:
        print("[ERROR] FastAPI not installed. Install with: pip install fastapi uvicorn")
        sys.exit(1)

    print(f"[HTTP] Starting server on {args.host}:{args.port}")
    print(f"[HTTP] Web UI: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}")
    print(f"[HTTP] API Docs: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}/docs")

    # uvicorn.run manages its own event loop
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


async def main() -> None:
    """Main entry point for the FCA MCP Server (CLI mode only)."""
    parser = argparse.ArgumentParser(
        description="FCA MCP Server with AI Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fca_mcp_server.py                    # Interactive mode
  python fca_mcp_server.py --no-interactive   # Non-interactive mode
  python fca_mcp_server.py --http-mode        # HTTP server mode
  python fca_mcp_server.py --enable-auth      # With OAuth authentication

Interactive commands:
  search Barclays                             # Search for firms
  firm 122702                                 # Get firm details
  analyze Barclays Bank                       # AI risk analysis
  compare Barclays vs HSBC                    # Compare firms
  ask What is the risk of Barclays?          # Natural language query

HTTP endpoints:
  GET  /                                       # Web UI
  GET  /health                                 # Health check
  POST /api/search                             # Search firms
  POST /api/analyze                            # Analyze firm
  POST /api/compare                            # Compare firms
  POST /api/ask                                # Natural language query
        """,
    )
    parser.add_argument("--no-interactive", action="store_true", help="Run in non-interactive mode (server only)")
    parser.add_argument("--enable-auth", action="store_true", help="Enable OAuth2 authentication")

    args = parser.parse_args()

    # CLI mode only
    runner = FcaMcpServerRunner()

    def signal_handler(sig, frame):
        runner.shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await runner.run(interactive=not args.no_interactive, enable_auth=args.enable_auth)


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
