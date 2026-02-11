"""TOON response models."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from fca_mcp.models.meta import ResponseMeta

T = TypeVar("T")


class ToonResponse(BaseModel, Generic[T]):
    """TOON formatted response.

    Type-Object-Object-Namespace format ensures structured, versioned responses.
    """

    model_config = ConfigDict(
        json_encoders={},
        ser_json_timedelta="iso8601",
    )

    type: str = Field(..., description="Type identifier (e.g., 'fca.firm.names')")
    version: str = Field(default="1.0", description="Schema version")
    data: T = Field(..., description="Response data")
    meta: ResponseMeta = Field(..., description="Response metadata")
