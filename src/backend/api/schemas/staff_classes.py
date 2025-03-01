from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, constr, Schema


class ExperienceTypeEnum(str, Enum):
    """Enum for different experience measurement types"""
    BAR_YEAR = "BAR_YEAR"
    GRADUATION_YEAR = "GRADUATION_YEAR"
    YEARS_IN_ROLE = "YEARS_IN_ROLE"


class StaffClassBase(BaseModel):
    """Base schema for staff class data shared between requests and responses"""
    name: str
    experience_type: ExperienceTypeEnum
    min_experience: int
    max_experience: int
    practice_area: Optional[str] = None
    geography: Optional[str] = None
    is_active: Optional[bool] = True
    
    @validator('min_experience')
    def validate_experience_range(cls, min_experience, values):
        """Validates that min_experience is less than max_experience"""
        if 'max_experience' in values and values['max_experience'] is not None and min_experience > values['max_experience']:
            raise ValueError('min_experience must be less than max_experience')
        return min_experience
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class StaffClassCreate(StaffClassBase):
    """Schema for creating a new staff class, extending StaffClassBase"""
    organization_id: UUID
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Senior Associate",
                "organization_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "experience_type": "BAR_YEAR",
                "min_experience": 3,
                "max_experience": 6,
                "practice_area": "Litigation",
                "geography": "Northeast",
                "is_active": True
            }
        }


class StaffClassUpdate(BaseModel):
    """Schema for updating an existing staff class with all optional fields"""
    name: Optional[str] = None
    experience_type: Optional[ExperienceTypeEnum] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    practice_area: Optional[str] = None
    geography: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('min_experience')
    def validate_experience_range(cls, min_experience, values):
        """Validates that min_experience is less than max_experience when both are provided"""
        if min_experience is None:
            return None
        if 'max_experience' in values and values['max_experience'] is not None and min_experience > values['max_experience']:
            raise ValueError('min_experience must be less than max_experience')
        return min_experience
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class StaffClass(StaffClassBase):
    """Schema for staff class responses including database ID and timestamps, extending StaffClassBase"""
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Senior Associate",
                "organization_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "experience_type": "BAR_YEAR",
                "min_experience": 3,
                "max_experience": 6,
                "practice_area": "Litigation",
                "geography": "Northeast",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z"
            }
        }


class StaffClassFilter(BaseModel):
    """Schema for filtering staff classes in list queries"""
    name: Optional[str] = None
    experience_type: Optional[ExperienceTypeEnum] = None
    practice_area: Optional[str] = None
    geography: Optional[str] = None
    is_active: Optional[bool] = None
    page: Optional[int] = 1
    size: Optional[int] = 50


class StaffClassList(BaseModel):
    """Schema for paginated list of staff classes"""
    items: List[StaffClass]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        orm_mode = True