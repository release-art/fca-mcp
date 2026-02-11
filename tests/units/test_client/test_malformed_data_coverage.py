"""Tests for malformed data handling to achieve 100% coverage.

These tests target warning paths and edge cases in data parsing.
"""

import pytest
import fca_api


class TestMalformedDataHandling:
    """Test handling of malformed API responses."""

    @pytest.mark.asyncio
    async def test_firm_names_with_non_dict_element(self, test_client: fca_api.async_api.Client):
        """Test _parse_firm_names_pg with non-dict element."""
        malformed_data = [
            "invalid_string_element",  # This should trigger warning on line 452
        ]

        # Parse and check that invalid element is skipped
        result = test_client._parse_firm_names_pg(malformed_data)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_firm_names_with_unexpected_field(self, test_client: fca_api.async_api.Client):
        """Test _parse_firm_names_pg with unexpected field."""
        malformed_data = [
            {
                "unknown_field": "value",  # This should trigger warning on line 465
            }
        ]

        result = test_client._parse_firm_names_pg(malformed_data)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_firm_controlled_functions_non_dict_row(self, test_client: fca_api.async_api.Client):
        """Test _parse_firm_controlled_functions_pg with non-dict row."""
        malformed_data = [
            "invalid_row",  # Should trigger warning on line 544
        ]

        result = test_client._parse_firm_controlled_functions_pg(malformed_data)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_firm_controlled_functions_non_dict_value(self, test_client: fca_api.async_api.Client):
        """Test _parse_firm_controlled_functions_pg with non-dict value."""
        malformed_data = [
            {
                "current": "invalid_string_value",  # Should trigger warning on line 549
            }
        ]

        result = test_client._parse_firm_controlled_functions_pg(malformed_data)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_firm_permissions_non_list(self, test_client: fca_api.async_api.Client):
        """Test _parse_firm_permissions_pg with non-list permission data."""
        malformed_data = {
            "Permission 1": "invalid_string_instead_of_list",  # Should trigger warning on line 612
        }

        result = test_client._parse_firm_permissions_pg(malformed_data)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_firm_passports_non_dict(self, test_client: fca_api.async_api.Client):
        """Test _parse_firm_passports_pg with non-dict element."""
        malformed_data = [
            "invalid_element",  # Should trigger warning on line 731
        ]

        result = test_client._parse_firm_passports_pg(malformed_data)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_firm_passports_unexpected_field(self, test_client: fca_api.async_api.Client):
        """Test _parse_firm_passports_pg with unexpected field."""
        malformed_data = [
            {
                "unknown_field": "value",  # Should trigger warning on line 740
            }
        ]

        result = test_client._parse_firm_passports_pg(malformed_data)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_individual_cf_non_dict_row(self, test_client: fca_api.async_api.Client):
        """Test parsing individual controlled functions with non-dict row."""
        malformed_data = [
            "invalid_row",  # Should trigger warning on line 919
        ]

        result = test_client._parse_individual_controlled_functions_pg(malformed_data)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_individual_cf_non_dict_value(self, test_client: fca_api.async_api.Client):
        """Test parsing individual controlled functions with non-dict value."""
        malformed_data = [
            {
                "current": "invalid_value",  # Should trigger warning on line 924
            }
        ]

        result = test_client._parse_individual_controlled_functions_pg(malformed_data)
        assert len(result) == 0

