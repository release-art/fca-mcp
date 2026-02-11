"""Tests for raw_status_codes edge cases to achieve 100% coverage."""

import pytest
import warnings
from fca_api import raw_status_codes


class TestFindCodeEdgeCases:
    """Test find_code function edge cases."""

    def test_find_code_with_none(self):
        """Test that None input returns None."""
        result = raw_status_codes.find_code(None)
        assert result is None

    def test_find_code_with_non_string(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="Value must be a string"):
            raw_status_codes.find_code(123)

    def test_find_code_with_unknown_code(self):
        """Test that unknown code triggers warning and returns None."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = raw_status_codes.find_code("UNKNOWN_CODE_XYZ")
            assert result is None
            assert len(w) == 1
            assert "Unknown FCA API status code" in str(w[0].message)
