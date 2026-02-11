from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


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
