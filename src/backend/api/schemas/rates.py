"""
Pydantic schemas for rate-related API requests and responses.

This module defines the data validation and serialization schemas for rate-related
operations in the Justice Bid Rate Negotiation System, including rate submission,
negotiation, filtering, and analytics.
"""

from typing import List, Optional, Dict, Any, TypeVar, Generic
from uuid import UUID
from datetime import date, datetime

from pydantic import BaseModel, validator, condecimal

from src.backend.utils.constants import RateType, RateStatus
from src.backend.utils.validators import validate_currency_code


class PageParams(BaseModel):
    """Base Pydantic model for pagination parameters."""
    page: int = 1
    page_size: int = 20

    @validator('page')
    def page_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Page must be >= 1')
        return v

    @validator('page_size')
    def page_size_must_be_in_range(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Page size must be between 1 and 100')
        return v


T = TypeVar('T')


class Page(Generic[T], BaseModel):
    """Generic Pydantic model for paginated responses."""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


class RateBase(BaseModel):
    """Base Pydantic model for rate data with common fields used across rate schemas."""
    attorney_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    firm_id: Optional[UUID] = None
    office_id: Optional[UUID] = None
    staff_class_id: Optional[UUID] = None
    amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    currency: Optional[str] = None
    type: Optional[RateType] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    status: Optional[RateStatus] = None

    @validator('currency')
    def validate_currency(cls, v):
        if v is not None:
            return validate_currency_code(v, 'currency')
        return v

    @validator('expiration_date')
    def validate_dates(cls, v, values):
        effective_date = values.get('effective_date')
        if effective_date and v and effective_date > v:
            raise ValueError('Effective date must be before or equal to expiration date')
        return v


class RateCreate(RateBase):
    """Schema for creating a new rate in the system."""
    attorney_id: UUID
    client_id: UUID
    firm_id: UUID
    amount: condecimal(ge=0, decimal_places=2)
    currency: str
    type: RateType
    effective_date: date
    expiration_date: Optional[date] = None
    status: Optional[RateStatus] = None
    justification: Optional[str] = None


class RateUpdate(BaseModel):
    """Schema for updating an existing rate in the system."""
    amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    currency: Optional[str] = None
    type: Optional[RateType] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    status: Optional[RateStatus] = None
    justification: Optional[str] = None


class RateHistoryEntry(BaseModel):
    """Schema for a historical rate change entry."""
    amount: condecimal(ge=0, decimal_places=2)
    type: RateType
    status: RateStatus
    timestamp: datetime
    user_id: UUID
    message: Optional[str] = None


class RateResponse(RateBase):
    """Schema for rate data in API responses."""
    id: UUID
    attorney_id: UUID
    client_id: UUID
    firm_id: UUID
    amount: condecimal(ge=0, decimal_places=2)
    currency: str
    type: RateType
    effective_date: date
    expiration_date: Optional[date] = None
    status: RateStatus
    history: Optional[List[RateHistoryEntry]] = None
    created_at: datetime
    updated_at: datetime
    attorney_name: Optional[str] = None
    staff_class_name: Optional[str] = None


class RateCounterProposal(BaseModel):
    """Schema for counter-proposing a rate during negotiation."""
    rate_id: UUID
    counter_amount: condecimal(ge=0, decimal_places=2)
    justification: Optional[str] = None


class RateBatchAction(BaseModel):
    """Schema for performing batch actions on multiple rates."""
    rate_ids: List[UUID]
    action: str  # approve, reject, counter
    counter_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    counter_percentage: Optional[float] = None
    justification: Optional[str] = None

    @validator('action')
    def validate_action(cls, action, values):
        if action not in ['approve', 'reject', 'counter']:
            raise ValueError('Action must be one of: approve, reject, counter')
        
        if action == 'counter' and values.get('counter_amount') is None and values.get('counter_percentage') is None:
            raise ValueError('Counter action requires either counter_amount or counter_percentage')
        
        return action


class RateFilter(BaseModel):
    """Schema for filtering rates in list operations."""
    attorney_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    firm_id: Optional[UUID] = None
    office_id: Optional[UUID] = None
    staff_class_id: Optional[UUID] = None
    type: Optional[RateType] = None
    status: Optional[RateStatus] = None
    effective_date_from: Optional[date] = None
    effective_date_to: Optional[date] = None
    negotiation_id: Optional[UUID] = None
    search: Optional[str] = None


class RateListRequest(PageParams, RateFilter):
    """Schema combining pagination and filter parameters for rate listing."""
    pass


class RateListResponse(Page[RateResponse]):
    """Schema for paginated list of rates in API responses."""
    pass


class RateSubmissionRequest(BaseModel):
    """Schema for submitting multiple rates in a single request."""
    client_id: UUID
    firm_id: UUID
    negotiation_id: Optional[UUID] = None
    rates: List[RateCreate]
    message: Optional[str] = None


class RateImpactAnalysis(BaseModel):
    """Schema for rate impact analysis results."""
    total_impact: condecimal(ge=0, decimal_places=2)
    percentage_increase: float
    breakdown_by_staff_class: Dict[str, Any]
    breakdown_by_office: Dict[str, Any]
    peer_comparison: Optional[Dict[str, Any]] = None


class RateActionRequest(BaseModel):
    """Schema for taking action on a single rate."""
    action: str  # approve, reject, counter
    counter_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    justification: Optional[str] = None

    @validator('action')
    def validate_action(cls, action, values):
        if action not in ['approve', 'reject', 'counter']:
            raise ValueError('Action must be one of: approve, reject, counter')
        
        if action == 'counter' and values.get('counter_amount') is None:
            raise ValueError('Counter action requires counter_amount')
        
        return action