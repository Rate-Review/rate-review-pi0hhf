"""
Pydantic schema models for negotiation-related API requests and responses in the Justice Bid Rate Negotiation System.

These schemas validate and structure data for negotiation endpoints, ensuring proper data integrity for the rate
negotiation workflow between law firms and clients.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, validator, constr

from ...utils.constants import NegotiationStatus, ApprovalStatus, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from ...utils.constants import RateStatus
from ...utils.validators import validate_uuid, validate_non_empty_string
from .rates import RateResponse, RateCounterProposal, RateBatchAction
from .messages import MessageResponse
from .organizations import OrganizationOut


class PageParams(BaseModel):
    """Base model for pagination parameters in negotiation list requests"""
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE

    @validator('page')
    def page_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Page must be >= 1')
        return v

    @validator('page_size')
    def page_size_must_be_in_range(cls, v):
        if v < 1 or v > MAX_PAGE_SIZE:
            raise ValueError(f'Page size must be between 1 and {MAX_PAGE_SIZE}')
        return v


class NegotiationBase(BaseModel):
    """Base schema for negotiation data with common fields"""
    client_id: UUID
    firm_id: UUID
    status: Optional[NegotiationStatus] = None
    request_date: Optional[date] = None
    submission_deadline: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('client_id')
    def validate_client_id(cls, v):
        """Validate client organization ID"""
        return validate_uuid(v, 'client_id')

    @validator('firm_id')
    def validate_firm_id(cls, v):
        """Validate law firm organization ID"""
        return validate_uuid(v, 'firm_id')

    @validator('submission_deadline', 'request_date', each_item=False)
    def validate_dates(cls, values):
        """Validate date fields have logical relationships"""
        if 'request_date' in values and 'submission_deadline' in values:
            if values['request_date'] and values['submission_deadline']:
                if values['request_date'] > values['submission_deadline']:
                    raise ValueError('Request date must be before or equal to submission deadline')
        return values

    class Config:
        orm_mode = True


class NegotiationCreate(NegotiationBase):
    """Schema for creating a new negotiation"""
    approval_workflow_id: Optional[UUID] = None


class NegotiationRequestCreate(BaseModel):
    """Schema for creating a rate negotiation request"""
    client_id: UUID
    firm_id: UUID
    message: Optional[str] = None
    submission_deadline: Optional[date] = None

    @validator('message')
    def validate_message(cls, v):
        """Validate optional message"""
        if v is not None:
            return validate_non_empty_string(v, 'message')
        return v


class NegotiationUpdate(BaseModel):
    """Schema for updating an existing negotiation"""
    submission_deadline: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('submission_deadline')
    def validate_deadline(cls, v):
        """Validate submission deadline is in the future"""
        if v is not None:
            today = date.today()
            if v < today:
                raise ValueError('Submission deadline must be in the future')
        return v


class NegotiationStatusUpdate(BaseModel):
    """Schema for updating a negotiation's status"""
    status: NegotiationStatus
    comment: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate the negotiation status"""
        if v not in [NegotiationStatus.REQUESTED, NegotiationStatus.IN_PROGRESS, 
                    NegotiationStatus.COMPLETED, NegotiationStatus.REJECTED]:
            raise ValueError('Invalid negotiation status')
        return v


class ApprovalStatusUpdate(BaseModel):
    """Schema for updating a negotiation's approval status"""
    status: ApprovalStatus
    comment: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate the approval status"""
        if v not in [ApprovalStatus.PENDING, ApprovalStatus.IN_PROGRESS, 
                   ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
            raise ValueError('Invalid approval status')
        return v


class NegotiationHistoryEntry(BaseModel):
    """Schema for a negotiation history event entry"""
    action: str
    user_id: UUID
    timestamp: datetime
    comment: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NegotiationResponse(BaseModel):
    """Schema for negotiation data in API responses"""
    id: UUID
    client_id: UUID
    firm_id: UUID
    status: NegotiationStatus
    request_date: date
    submission_deadline: Optional[date] = None
    completion_date: Optional[date] = None
    approval_workflow_id: Optional[UUID] = None
    approval_status: Optional[ApprovalStatus] = None
    metadata: Optional[Dict[str, Any]] = None
    history: Optional[List[NegotiationHistoryEntry]] = None
    client: Optional[OrganizationOut] = None
    firm: Optional[OrganizationOut] = None
    rate_count: int
    rates: Optional[List[RateResponse]] = None
    messages: Optional[List[MessageResponse]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class NegotiationAddRates(BaseModel):
    """Schema for adding rates to a negotiation"""
    rate_ids: List[UUID]
    message: Optional[str] = None

    @validator('rate_ids')
    def validate_rate_ids(cls, v):
        """Validate list of rate IDs"""
        if not v:
            raise ValueError('At least one rate ID must be provided')
        for rate_id in v:
            validate_uuid(rate_id, 'rate_id')
        return v


class CounterProposalCreate(BaseModel):
    """Schema for creating counter-proposals in a negotiation"""
    counter_proposals: List[RateCounterProposal]
    message: Optional[str] = None

    @validator('counter_proposals')
    def validate_counter_proposals(cls, v):
        """Validate list of counter-proposals"""
        if not v:
            raise ValueError('At least one counter-proposal must be provided')
        return v


class NegotiationRateActionRequest(BaseModel):
    """Schema for taking actions on rates in a negotiation"""
    rate_ids: Union[UUID, List[UUID]]
    action: str  # approve, reject, counter
    counter_amount: Optional[float] = None
    counter_percentage: Optional[float] = None
    justification: Optional[str] = None

    @validator('action')
    def validate_action(cls, v, values):
        """Validate the action and required fields"""
        if v not in ['approve', 'reject', 'counter']:
            raise ValueError('Action must be one of: approve, reject, counter')
        
        if v == 'counter' and 'counter_amount' not in values and 'counter_percentage' not in values:
            raise ValueError('Counter action requires either counter_amount or counter_percentage')
        
        return v


class NegotiationFilter(BaseModel):
    """Schema for filtering negotiations in list operations"""
    client_id: Optional[UUID] = None
    firm_id: Optional[UUID] = None
    status: Optional[NegotiationStatus] = None
    approval_status: Optional[ApprovalStatus] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    overdue_only: Optional[bool] = None
    search: Optional[str] = None


class NegotiationListRequest(PageParams, NegotiationFilter):
    """Schema for negotiation list API requests with pagination"""
    pass


class NegotiationListResponse(BaseModel):
    """Schema for paginated negotiation list in API responses"""
    items: List[NegotiationResponse]
    total: int
    page: int
    page_size: int
    pages: int


class NegotiationAnalytics(BaseModel):
    """Schema for negotiation analytics data"""
    total_impact: float
    percentage_increase: float
    breakdown_by_staff_class: Dict[str, Any]
    breakdown_by_attorney: Dict[str, Any]
    peer_comparison: Optional[Dict[str, Any]] = None
    rate_status_counts: Dict[str, int]


class NegotiationDeadlineUpdate(BaseModel):
    """Schema for updating a negotiation's submission deadline"""
    deadline: date
    comment: Optional[str] = None

    @validator('deadline')
    def validate_deadline(cls, v):
        """Validate submission deadline is in the future"""
        today = date.today()
        if v < today:
            raise ValueError('Deadline must be in the future')
        return v


class NegotiationFinalize(BaseModel):
    """Schema for finalizing a negotiation"""
    status: NegotiationStatus
    comment: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate the final status"""
        if v not in [NegotiationStatus.COMPLETED, NegotiationStatus.REJECTED]:
            raise ValueError('Final status must be either COMPLETED or REJECTED')
        return v