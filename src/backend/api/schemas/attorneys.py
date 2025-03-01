from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator, root_validator, EmailStr

from ...utils.constants import ExperienceType, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from ...utils.validators import validate_required, validate_string, validate_date, validate_uuid, validate_email, validate_list
from .staff_classes import StaffClassOut


class AttorneyBase(BaseModel):
    """Base schema for attorney data with common fields"""
    name: str
    bar_date: Optional[date] = None
    graduation_date: Optional[date] = None
    promotion_date: Optional[date] = None
    office_ids: Optional[List[UUID]] = None
    timekeeper_ids: Optional[Dict[str, str]] = None
    staff_class_id: Optional[UUID] = None
    
    @validator('name')
    def validate_name(cls, value):
        """Validate attorney name"""
        validate_required(value, 'name')
        validate_string(value, 'name', min_length=1, max_length=255)
        return value
    
    @root_validator
    def validate_dates(cls, values):
        """Validate date fields are properly formatted and logical"""
        bar_date = values.get('bar_date')
        graduation_date = values.get('graduation_date')
        promotion_date = values.get('promotion_date')
        
        if graduation_date and bar_date and graduation_date > bar_date:
            raise ValueError('Graduation date must be before or equal to bar date')
        
        if bar_date and promotion_date and bar_date > promotion_date:
            raise ValueError('Bar date must be before or equal to promotion date')
            
        return values
    
    class Config:
        arbitrary_types_allowed = True


class AttorneyCreate(AttorneyBase):
    """Schema for creating a new attorney"""
    organization_id: UUID
    
    @validator('organization_id')
    def validate_organization_id(cls, value):
        """Validate organization ID is provided"""
        validate_required(value, 'organization_id')
        validate_uuid(value, 'organization_id')
        return value
    
    class Config:
        arbitrary_types_allowed = True


class AttorneyUpdate(BaseModel):
    """Schema for updating an existing attorney"""
    name: Optional[str] = None
    bar_date: Optional[date] = None
    graduation_date: Optional[date] = None
    promotion_date: Optional[date] = None
    office_ids: Optional[List[UUID]] = None
    timekeeper_ids: Optional[Dict[str, str]] = None
    staff_class_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    
    @root_validator
    def validate_dates(cls, values):
        """Validate date fields are properly formatted and logical"""
        bar_date = values.get('bar_date')
        graduation_date = values.get('graduation_date')
        promotion_date = values.get('promotion_date')
        
        if graduation_date and bar_date and graduation_date > bar_date:
            raise ValueError('Graduation date must be before or equal to bar date')
        
        if bar_date and promotion_date and bar_date > promotion_date:
            raise ValueError('Bar date must be before or equal to promotion date')
            
        return values
    
    class Config:
        arbitrary_types_allowed = True


class AttorneyInDB(AttorneyBase):
    """Schema for attorney data in the database"""
    id: UUID
    organization_id: UUID
    unicourt_id: UUID
    performance_data: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class AttorneyOut(BaseModel):
    """Schema for attorney data in API responses"""
    id: UUID
    organization_id: UUID
    name: str
    bar_date: Optional[date] = None
    graduation_date: Optional[date] = None
    promotion_date: Optional[date] = None
    office_ids: List[UUID] = Field(default_factory=list)
    timekeeper_ids: Dict[str, str] = Field(default_factory=dict)
    staff_class_id: Optional[UUID] = None
    staff_class: Optional[StaffClassOut] = None
    unicourt_id: Optional[UUID] = None
    performance_data: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class AttorneyWithRatesOut(BaseModel):
    """Schema for attorney data with associated rates"""
    attorney: AttorneyOut
    rates: List[Dict] = Field(default_factory=list)
    rate_analytics: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class AttorneyList(BaseModel):
    """Schema for paginated list of attorneys"""
    items: List[AttorneyOut]
    total: int
    page: int
    size: int
    pages: int


class AttorneySearchParams(BaseModel):
    """Schema for attorney search parameters"""
    name: Optional[str] = None
    organization_id: Optional[UUID] = None
    staff_class_id: Optional[UUID] = None
    bar_date_after: Optional[date] = None
    bar_date_before: Optional[date] = None
    office_ids: Optional[List[UUID]] = None
    active_only: Optional[bool] = True
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE
    
    class Config:
        default_factory = dict(page=1, page_size=DEFAULT_PAGE_SIZE, active_only=True)


class UniCourtAttorneyMapping(BaseModel):
    """Schema for mapping Justice Bid attorneys to UniCourt attorneys"""
    attorney_id: UUID
    unicourt_id: str
    fetch_performance_data: bool = True
    
    @validator('attorney_id')
    def validate_attorney_id(cls, value):
        """Validate attorney ID is provided and valid UUID"""
        validate_required(value, 'attorney_id')
        validate_uuid(value, 'attorney_id')
        return value
    
    @validator('unicourt_id')
    def validate_unicourt_id(cls, value):
        """Validate UniCourt ID is provided"""
        validate_required(value, 'unicourt_id')
        validate_string(value, 'unicourt_id')
        return value
    
    class Config:
        default_factory = dict(fetch_performance_data=True)


class TimekeeperIdUpdate(BaseModel):
    """Schema for updating attorney timekeeper IDs"""
    attorney_id: UUID
    client_id: UUID
    timekeeper_id: str
    
    @validator('attorney_id')
    def validate_attorney_id(cls, value):
        """Validate attorney ID is provided and valid UUID"""
        validate_required(value, 'attorney_id')
        validate_uuid(value, 'attorney_id')
        return value
    
    @validator('client_id')
    def validate_client_id(cls, value):
        """Validate client ID is provided and valid UUID"""
        validate_required(value, 'client_id')
        validate_uuid(value, 'client_id')
        return value
    
    @validator('timekeeper_id')
    def validate_timekeeper_id(cls, value):
        """Validate timekeeper ID is provided"""
        validate_required(value, 'timekeeper_id')
        validate_string(value, 'timekeeper_id')
        return value
    
    class Config:
        arbitrary_types_allowed = True


class StaffClassAssignment(BaseModel):
    """Schema for attorney staff class assignment"""
    attorney_id: UUID
    staff_class_id: UUID
    
    @validator('attorney_id')
    def validate_attorney_id(cls, value):
        """Validate attorney ID is provided and valid UUID"""
        validate_required(value, 'attorney_id')
        validate_uuid(value, 'attorney_id')
        return value
    
    @validator('staff_class_id')
    def validate_staff_class_id(cls, value):
        """Validate staff class ID is provided and valid UUID"""
        validate_required(value, 'staff_class_id')
        validate_uuid(value, 'staff_class_id')
        return value
    
    class Config:
        arbitrary_types_allowed = True


class UniCourtSearchParams(BaseModel):
    """Schema for UniCourt attorney search parameters"""
    name: str
    bar_number: Optional[str] = None
    state: Optional[str] = None
    limit: int = 20
    
    @validator('name')
    def validate_name(cls, value):
        """Validate name is provided"""
        validate_required(value, 'name')
        validate_string(value, 'name', min_length=2)
        return value
    
    class Config:
        default_factory = dict(limit=20)