"""
Pydantic models for organization-related API operations in the Justice Bid Rate Negotiation System.

This module defines schemas for organization data validation, including law firms, clients,
offices, departments, and peer groups. These schemas ensure data integrity and provide
a structured interface for organization-related API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator, EmailStr, constr

from ...utils.constants import (
    OrganizationType, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, ExperienceType
)
from ...utils.validators import (
    validate_email, validate_string, validate_required, validate_enum_value
)


class OrganizationBase(BaseModel):
    """Base schema for organization data with common fields."""
    name: str
    type: OrganizationType
    domain: Optional[str] = None

    @validator('name')
    def validate_name(cls, value):
        """Validate organization name."""
        validate_required(value, "name")
        validate_string(value, "name", min_length=2, max_length=255)
        return value

    @validator('type')
    def validate_type(cls, value):
        """Validate organization type."""
        validate_enum_value(value, OrganizationType, "type")
        return value

    @validator('domain')
    def validate_domain(cls, value):
        """Validate organization domain if provided."""
        if value is not None:
            validate_string(value, "domain", min_length=4, max_length=255)
            # Simple domain validation - could be enhanced with regex pattern
            if '.' not in value:
                raise ValueError("Domain must be a valid domain name (e.g., example.com)")
        return value

    class Config:
        orm_mode = True


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    settings: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class OrganizationUpdate(BaseModel):
    """Schema for updating an existing organization."""
    name: Optional[str] = None
    domain: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    @validator('name')
    def validate_name(cls, value):
        """Validate name if provided."""
        if value is not None:
            validate_string(value, "name", min_length=2, max_length=255)
        return value

    @validator('domain')
    def validate_domain(cls, value):
        """Validate domain if provided."""
        if value is not None:
            validate_string(value, "domain", min_length=4, max_length=255)
            if '.' not in value:
                raise ValueError("Domain must be a valid domain name (e.g., example.com)")
        return value

    class Config:
        orm_mode = True


class OrganizationInDB(OrganizationBase):
    """Schema for organization data in the database."""
    id: UUID
    settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[UUID] = None

    class Config:
        orm_mode = True


class OrganizationOut(BaseModel):
    """Schema for organization data in API responses."""
    id: UUID
    name: str
    type: OrganizationType
    domain: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    offices: List['OfficeOut'] = []
    departments: List['DepartmentOut'] = []

    class Config:
        orm_mode = True


class OrganizationList(BaseModel):
    """Schema for paginated list of organizations."""
    items: List[OrganizationOut]
    total: int
    page: int
    size: int
    pages: int


class OrganizationSearchParams(BaseModel):
    """Schema for organization search parameters."""
    name: Optional[str] = None
    domain: Optional[str] = None
    type: Optional[OrganizationType] = None
    active_only: Optional[bool] = True
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE

    class Config:
        extra = "ignore"


class OfficeBase(BaseModel):
    """Base schema for office data with common fields."""
    name: str
    city: str
    country: str
    state: Optional[str] = None
    region: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('name')
    def validate_name(cls, value):
        """Validate office name."""
        validate_required(value, "name")
        validate_string(value, "name", min_length=2, max_length=255)
        return value

    @validator('city')
    def validate_city(cls, value):
        """Validate city name."""
        validate_required(value, "city")
        validate_string(value, "city", min_length=2, max_length=255)
        return value

    @validator('country')
    def validate_country(cls, value):
        """Validate country name."""
        validate_required(value, "country")
        validate_string(value, "country", min_length=2, max_length=255)
        return value

    class Config:
        orm_mode = True


class OfficeCreate(OfficeBase):
    """Schema for creating a new office."""
    organization_id: UUID

    class Config:
        orm_mode = True


class OfficeUpdate(BaseModel):
    """Schema for updating an existing office."""
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True


class OfficeOut(BaseModel):
    """Schema for office data in API responses."""
    id: UUID
    organization_id: UUID
    name: str
    city: str
    country: str
    state: Optional[str] = None
    region: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DepartmentBase(BaseModel):
    """Base schema for department data with common fields."""
    name: str
    metadata: Optional[Dict[str, Any]] = None

    @validator('name')
    def validate_name(cls, value):
        """Validate department name."""
        validate_required(value, "name")
        validate_string(value, "name", min_length=2, max_length=255)
        return value

    class Config:
        orm_mode = True


class DepartmentCreate(DepartmentBase):
    """Schema for creating a new department."""
    organization_id: UUID

    class Config:
        orm_mode = True


class DepartmentUpdate(BaseModel):
    """Schema for updating an existing department."""
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True


class DepartmentOut(BaseModel):
    """Schema for department data in API responses."""
    id: UUID
    organization_id: UUID
    name: str
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PeerGroupBase(BaseModel):
    """Base schema for peer group data with common fields."""
    name: str
    organization_id: UUID
    criteria: Optional[Dict[str, Any]] = None

    @validator('name')
    def validate_name(cls, value):
        """Validate peer group name."""
        validate_required(value, "name")
        validate_string(value, "name", min_length=2, max_length=255)
        return value

    class Config:
        orm_mode = True


class PeerGroupCreate(PeerGroupBase):
    """Schema for creating a new peer group."""

    class Config:
        orm_mode = True


class PeerGroupUpdate(BaseModel):
    """Schema for updating an existing peer group."""
    name: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class PeerGroupOut(BaseModel):
    """Schema for peer group data in API responses."""
    id: UUID
    name: str
    organization_id: UUID
    criteria: Dict[str, Any]
    member_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PeerGroupMemberAdd(BaseModel):
    """Schema for adding a member to a peer group."""
    organization_id: UUID
    member_id: UUID

    class Config:
        orm_mode = True


class PeerGroupMemberRemove(BaseModel):
    """Schema for removing a member from a peer group."""
    organization_id: UUID
    member_id: UUID

    class Config:
        orm_mode = True


class RateRulesUpdate(BaseModel):
    """Schema for updating organization rate rules."""
    freeze_period_days: Optional[int] = None
    notice_period_days: Optional[int] = None
    max_increase_percent: Optional[float] = None
    submission_window: Optional[Dict[str, Any]] = None
    staff_class_rules: Optional[Dict[str, Any]] = None

    @validator('max_increase_percent')
    def validate_max_increase(cls, value):
        """Validate maximum increase percentage."""
        if value is not None and value < 0:
            raise ValueError("Maximum increase percentage must be non-negative")
        return value

    class Config:
        orm_mode = True