"""Async adapter for fca-api library."""

from typing import Any

import fca_api
from fca_api import async_api


class FcaApiAdapter:
    """Adapter wrapping fca-api async client."""

    def __init__(self, credentials: tuple[str, str]):
        """Initialize adapter.

        Args:
            credentials: Tuple of (email, api_key) for FCA API
        """
        self.credentials = credentials
        self._client: async_api.Client | None = None

    async def __aenter__(self):
        """Enter async context manager."""
        self._client = async_api.Client(credentials=self.credentials)
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def search_firms(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search for firms by name.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of firm search results
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        results = await self._client.search_frn(query)
        firms = []

        count = 0
        async for firm in results:
            if count >= limit:
                break
            firms.append(
                {
                    "firm_id": firm.frn,
                    "firm_name": firm.name,
                    "status": firm.status,
                    "firm_type": getattr(firm, "type", None),
                }
            )
            count += 1

        return firms

    async def get_firm(self, firm_id: str) -> dict[str, Any]:
        """Get firm details.

        Args:
            firm_id: Firm Reference Number (FRN)

        Returns:
            Firm details
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        firm = await self._client.get_firm(firm_id)

        return {
            "firm_id": firm.frn,
            "firm_name": firm.name,
            "status": firm.status,
            "firm_type": firm.type,
            "companies_house_number": firm.companies_house_number,
            "client_money_permission": firm.client_money_permission,
            "status_effective_date": getattr(firm, "status_effective_date", None),
        }

    async def get_firm_names(self, firm_id: str) -> list[dict[str, Any]]:
        """Get firm names.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of firm names
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        names = await self._client.get_firm_names(firm_id)
        results = []

        async for name in names:
            results.append(
                {
                    "name": name.name,
                    "name_type": getattr(name, "name_type", "primary"),
                    "effective_from": getattr(name, "effective_from", None),
                    "effective_to": getattr(name, "effective_to", None),
                }
            )

        return results

    async def get_firm_addresses(self, firm_id: str) -> list[dict[str, Any]]:
        """Get firm addresses.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of addresses
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        addresses = await self._client.get_firm_addresses(firm_id)
        results = []

        async for addr in addresses:
            results.append(
                {
                    "address_lines": getattr(addr, "address_lines", []),
                    "postcode": getattr(addr, "postcode", None),
                    "country": getattr(addr, "country", None),
                    "address_type": getattr(addr, "address_type", None),
                }
            )

        return results

    async def get_firm_permissions(self, firm_id: str) -> list[dict[str, Any]]:
        """Get firm permissions.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of permissions
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        permissions = await self._client.get_firm_permissions(firm_id)
        results = []

        async for perm in permissions:
            results.append(
                {
                    "permission_name": getattr(perm, "name", "Unknown"),
                    "customer_types": getattr(perm, "customer_type", None),
                    "investment_types": getattr(perm, "investment_type", None),
                    "limitations": getattr(perm, "limitation", None),
                }
            )

        return results

    async def get_firm_individuals(self, firm_id: str) -> list[dict[str, Any]]:
        """Get individuals associated with firm.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of individuals
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        individuals = await self._client.get_firm_individuals(firm_id)
        results = []

        async for ind in individuals:
            results.append(
                {
                    "individual_id": getattr(ind, "irn", ""),
                    "full_name": getattr(ind, "name", "Unknown"),
                    "status": getattr(ind, "status", None),
                }
            )

        return results

    async def get_firm_disciplinary_history(self, firm_id: str) -> list[dict[str, Any]]:
        """Get firm disciplinary history.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of disciplinary actions
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        history = await self._client.get_firm_disciplinary_history(firm_id)
        results = []

        async for action in history:
            results.append(
                {
                    "action_type": getattr(action, "type_of_action", "Unknown"),
                    "action_description": getattr(action, "type_of_description", "Unknown"),
                    "enforcement_type": getattr(action, "enforcement_type", None),
                    "effective_from": getattr(action, "effective_from", None),
                }
            )

        return results

    async def get_firm_passports(self, firm_id: str) -> list[dict[str, Any]]:
        """Get firm passports.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of passports
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        passports = await self._client.get_firm_passports(firm_id)
        results = []

        async for passport in passports:
            results.append(
                {
                    "country": getattr(passport, "country", "Unknown"),
                    "direction": getattr(passport, "direction", "Unknown"),
                    "permissions_url": str(getattr(passport, "permissions", "")),
                }
            )

        return results

    async def get_firm_regulators(self, firm_id: str) -> list[dict[str, Any]]:
        """Get firm regulators.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of regulators
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        regulators = await self._client.get_firm_regulators(firm_id)
        results = []

        async for reg in regulators:
            results.append(
                {
                    "regulator_name": getattr(reg, "name", "Unknown"),
                    "regulator_type": getattr(reg, "regulator_type", None),
                }
            )

        return results

    async def get_firm_requirements(self, firm_id: str) -> list[dict[str, Any]]:
        """Get firm requirements.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of requirements
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        requirements = await self._client.get_firm_requirements(firm_id)
        results = []

        async for req in requirements:
            # Get the full model dump to extract dynamic requirement content
            req_dict = req.model_dump()
            # Extract content from dynamic fields (exclude standard fields)
            standard_fields = {'reference', 'effective_date', 'financial_promotions_requirement', 'financial_promotions_investment_types'}
            content_fields = {k: v for k, v in req_dict.items() if k not in standard_fields and v}
            
            # Get first content field or use abbreviated version
            content_text = "No content"
            if content_fields:
                first_content = next(iter(content_fields.values()))
                content_text = str(first_content)[:200] + "..." if len(str(first_content)) > 200 else str(first_content)
            
            results.append(
                {
                    "requirement_reference": getattr(req, "reference", "Unknown"),
                    "requirement_content": content_text,
                    "effective_date": getattr(req, "effective_date", None),
                    "financial_promotions": getattr(req, "financial_promotions_requirement", False),
                }
            )

        return results

    async def get_firm_waivers(self, firm_id: str) -> list[dict[str, Any]]:
        """Get firm waivers.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of waivers
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        waivers = await self._client.get_firm_waivers(firm_id)
        results = []

        async for waiver in waivers:
            rule_articles = getattr(waiver, "rule_article_numbers", [])
            results.append(
                {
                    "rule_article_numbers": rule_articles,
                    "discretions": getattr(waiver, "discretions", None),
                    "discretions_url": str(getattr(waiver, "discretions_url", "")),
                }
            )

        return results

    async def get_firm_appointed_representatives(self, firm_id: str) -> list[dict[str, Any]]:
        """Get appointed representatives.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of appointed representatives
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        ars = await self._client.get_firm_appointed_representatives(firm_id)
        results = []

        async for ar in ars:
            results.append(
                {
                    "firm_id": ar.frn,
                    "firm_name": ar.name,
                    "status": getattr(ar, "status", None),
                    "type": ar.type,
                    "subtype": ar.subtype,
                }
            )

        return results

    async def get_firm_controlled_functions(self, firm_id: str) -> list[dict[str, Any]]:
        """Get controlled functions.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of controlled functions
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        cfs = await self._client.get_firm_controlled_functions(firm_id)
        results = []

        async for cf in cfs:
            results.append(
                {
                    "function_name": getattr(cf, "function", "Unknown"),
                    "individual_id": getattr(cf, "individual_reference_number", None),
                    "individual_name": getattr(cf, "individual_name", None),
                }
            )

        return results

    async def get_firm_exclusions(self, firm_id: str) -> list[dict[str, Any]]:
        """Get firm exclusions.

        Args:
            firm_id: Firm Reference Number

        Returns:
            List of exclusions
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        exclusions = await self._client.get_firm_exclusions(firm_id)
        results = []

        async for exclusion in exclusions:
            results.append(
                {
                    "exclusion_type": getattr(exclusion, "exclusion_type", None),
                    "particular_exclusion_relied_upon": getattr(
                        exclusion, "particular_exclusion_relied_upon", None
                    ),
                    "effective_from": (
                        exclusion.effective_from.isoformat()
                        if getattr(exclusion, "effective_from", None)
                        else None
                    ),
                    "effective_to": (
                        exclusion.effective_to.isoformat()
                        if getattr(exclusion, "effective_to", None)
                        else None
                    ),
                }
            )

        return results
