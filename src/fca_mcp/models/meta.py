from __future__ import annotations

"""Metadata models for TOON responses."""

import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ResponseMeta(BaseModel):
    """Metadata for TOON response."""

    pages_loaded: int = Field(..., description="Number of pages loaded")
    items_returned: int = Field(..., description="Total items returned")
    truncated: bool = Field(..., description="Whether response was truncated")
    total_available: int | None = Field(None, description="Total items available")
    execution_time_ms: float | None = Field(None, description="Execution time in milliseconds")
