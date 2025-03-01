from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator, root_validator, constr
from datetime import datetime

class OCGAlternativeBase(BaseModel):
    """Base schema for OCG section alternatives"""
    id: str
    title: str
    content: str
    points: int

class OCGSectionBase(BaseModel):
    """Base schema for OCG sections"""
    id: str
    title: str
    content: str
    is_negotiable: bool
    alternatives: List[OCGAlternativeBase] = []

class OCGFirmSelectionBase(BaseModel):
    """Base schema for law firm selections in OCG negotiation"""
    section_id: str
    alternative_id: str
    points_used: int

class OCGBase(BaseModel):
    """Base schema for Outside Counsel Guidelines"""
    id: str
    client_id: str
    name: str
    version: int
    status: str  # Draft, Published, Negotiating, Signed
    sections: List[OCGSectionBase]
    firm_selections: Dict[str, Dict[str, str]] = {}  # firm_id -> {section_id: alternative_id}
    total_points: int
    created_at: datetime
    updated_at: datetime

class OCGCreate(BaseModel):
    """Schema for creating a new OCG"""
    name: str
    version: int = 1
    sections: List[OCGSectionBase]
    total_points: int
    
    @validator('total_points')
    def validate_total_points(cls, v):
        if v <= 0:
            raise ValueError('Total points must be greater than 0')
        return v

class OCGUpdate(BaseModel):
    """Schema for updating an existing OCG"""
    name: Optional[str] = None
    sections: Optional[List[OCGSectionBase]] = None
    total_points: Optional[int] = None
    status: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['Draft', 'Published', 'Negotiating', 'Signed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

class OCGPublish(BaseModel):
    """Schema for publishing an OCG"""
    id: str
    firm_point_budgets: Dict[str, int]  # firm_id -> point_budget

class OCGNegotiationSubmit(BaseModel):
    """Schema for submitting OCG negotiation selections"""
    ocg_id: str
    firm_id: str
    section_selections: Dict[str, str]  # section_id -> alternative_id
    comments: Optional[str] = ""
    
    @root_validator
    def validate_points_budget(cls, values, **kwargs):
        # In a real implementation, we would:
        # 1. Fetch the OCG using ocg_id
        # 2. Check the firm's point budget
        # 3. Calculate total points used from section selections
        # 4. Ensure points used <= points available
        # Since we can't access the database here, this would be implemented in the service layer
        return values

class OCGResponse(OCGBase):
    """Schema for OCG API responses"""
    pass

class OCGListResponse(BaseModel):
    """Schema for OCG list API responses"""
    items: List[OCGResponse]
    total: int
    page: int
    size: int

class OCGNegotiationStatus(BaseModel):
    """Schema for OCG negotiation status"""
    ocg_id: str
    firm_id: str
    status: str
    section_selections: Dict[str, str]  # section_id -> alternative_id
    points_used: int
    points_available: int
    comments: Optional[str] = ""
    last_updated: datetime

class OCGFirmPointBudget(BaseModel):
    """Schema for setting a firm's point budget for OCG negotiation"""
    firm_id: str
    point_budget: int
    
    @validator('point_budget')
    def validate_point_budget(cls, v):
        if v <= 0:
            raise ValueError('Point budget must be greater than 0')
        return v

class OCGStatusUpdate(BaseModel):
    """Schema for updating only the status of an OCG"""
    status: str
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['Draft', 'Published', 'Negotiating', 'Signed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v