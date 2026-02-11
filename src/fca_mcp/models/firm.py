"""Firm data models."""

import logging
from datetime import datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FirmSearchResult(BaseModel):
    """Firm search result."""

    firm_id: str = Field(..., description="FCA Firm Reference Number (FRN)")
    firm_name: str = Field(..., description="Name of the firm")
    status: str = Field(..., description="Current regulatory status")
    firm_type: str | None = Field(None, description="Type of firm")


class FirmDetails(BaseModel):
    """Core firm details."""

    firm_id: str
    firm_name: str
    status: str
    firm_type: str | None = None
    effective_date: datetime | None = None
    registered_date: datetime | None = None


class FirmName(BaseModel):
    """Firm name record."""

    name: str
    name_type: str
    effective_from: datetime | None = None
    effective_to: datetime | None = None


class Address(BaseModel):
    """Address record."""

    address_lines: list[str]
    postcode: str | None = None
    country: str | None = None
    address_type: str | None = None


class Permission(BaseModel):
    """Regulatory permission."""

    permission_name: str
    status: str
    granted_date: datetime | None = None


class Individual(BaseModel):
    """Individual associated with firm."""

    individual_id: str
    full_name: str
    role: str | None = None
    status: str | None = None


class DisciplinaryAction(BaseModel):
    """Disciplinary history record."""

    action_type: str
    action_date: datetime | None = None
    description: str | None = None
    outcome: str | None = None


class Passport(BaseModel):
    """Passport information."""

    country: str
    passport_type: str
    services: list[str] = Field(default_factory=list)


class Regulator(BaseModel):
    """Regulator information."""

    regulator_name: str
    regulator_type: str | None = None


class Requirement(BaseModel):
    """Requirement information."""

    requirement_text: str
    requirement_type: str | None = None
    imposed_date: datetime | None = None


class Waiver(BaseModel):
    """Waiver information."""

    waiver_text: str
    waiver_type: str | None = None
    granted_date: datetime | None = None


class AppointedRepresentative(BaseModel):
    """Appointed representative information."""

    firm_id: str
    firm_name: str
    status: str | None = None


class ControlledFunction(BaseModel):
    """Controlled function information."""

    function_name: str
    individual_id: str | None = None
    individual_name: str | None = None
