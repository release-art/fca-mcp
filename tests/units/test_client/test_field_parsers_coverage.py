"""Tests for field parsers to achieve 100% coverage."""

import datetime
import pytest
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from fca_api.types.field_parsers import ParseFcaDate, StrOrNone, FixIncompleteUrl


class TestParseFcaDate:
    """Test date parsing edge cases."""

    def test_non_string_input(self):
        """Test that non-string input raises TypeError."""
        # Get the underlying function from the validator
        parse_func = ParseFcaDate.func
        with pytest.raises(TypeError, match="Expected a string"):
            parse_func(123)

    def test_unrecognized_format(self):
        """Test that unrecognized date format raises ValueError."""
        parse_func = ParseFcaDate.func
        with pytest.raises(ValueError, match="not in a recognized format"):
            parse_func("invalid-date-format-xyz")


class TestStrOrNone:
    """Test string normalization edge cases."""

    def test_strip_whitespace_with_content(self):
        """Test that values with whitespace are stripped but preserved."""
        str_func = StrOrNone.func
        result = str_func("  some text  ")
        assert result == "some text"

    def test_url_type_values(self):
        """Test with URL-like strings."""
        str_func = StrOrNone.func
        result = str_func("https://example.com")
        assert result == "https://example.com"


class TestFixIncompleteUrl:
    """Test URL fixing edge cases."""

    def test_ftp_protocol(self):
        """Test that FTP URLs are preserved."""
        url_func = FixIncompleteUrl.func
        result = url_func("ftp://files.example.com")
        assert result == "ftp://files.example.com"

    def test_http_protocol(self):
        """Test that HTTP URLs are preserved."""
        url_func = FixIncompleteUrl.func
        result = url_func("http://example.com")
        assert result == "http://example.com"
