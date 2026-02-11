from __future__ import annotations

import json
import logging

import fca_mcp

logger = logging.getLogger(__name__)


class NaturalLanguageInterface:
    """Natural language interface for FCA data queries."""

    def __init__(self, assistant: fca_mcp.fca_ai_assistant.FcaAiAssistant):
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
