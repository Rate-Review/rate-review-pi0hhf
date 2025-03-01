"""
Pydantic models for billing-related API operations in the Justice Bid Rate Negotiation System.
These schemas handle validation for billing data import/export, filtering, and response
serialization for the billing API endpoints.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator, constr, condecimal

from ...utils.validators import (
    validate_currency, validate_uuid, validate_date, 
    validate_string, validate_number
)
from ...utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from ...utils.formatting import format_currency


class BillingBase(BaseModel):
    """Base schema for billing data with common fields"""
    attorney_id: UUID
    client_id: UUID
    hours: Decimal
    fees: Decimal
    billing_date: date
    matter_id: Optional[UUID] = None
    is_afa: bool = False  # Alternative Fee Arrangement flag
    currency: str = "USD"
    department_id: Optional[UUID] = None
    practice_area: Optional[str] = None
    office_id: Optional[UUID] = None
    office_location: Optional[str] = None

    @validator('attorney_id')
    def validate_attorney_id(cls, value):
        validate_uuid(value, "attorney_id")
        return value

    @validator('client_id')
    def validate_client_id(cls, value):
        validate_uuid(value, "client_id")
        return value

    @validator('hours')
    def validate_hours(cls, value):
        validate_number(value, "hours", min_value=Decimal('0'))
        return value

    @validator('fees')
    def validate_fees(cls, value):
        validate_number(value, "fees", min_value=Decimal('0'))
        return value

    @validator('billing_date')
    def validate_billing_date(cls, value):
        validate_date(value, "billing_date")
        # Ensure date is not in the future
        if value > date.today():
            raise ValueError("billing_date cannot be in the future")
        return value

    @validator('currency')
    def validate_currency(cls, value):
        validate_currency(value, "currency")
        return value

    class Config:
        orm_mode = True


class BillingCreate(BillingBase):
    """Schema for creating new billing records"""
    
    class Config:
        schema_extra = {
            "example": {
                "attorney_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "client_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "hours": 5.5,
                "fees": 2750.00,
                "billing_date": "2023-01-15",
                "matter_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "is_afa": False,
                "currency": "USD",
                "practice_area": "Litigation",
                "office_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "office_location": "New York"
            }
        }
        # Default values
        schema_extra["example"]["is_afa"] = False
        schema_extra["example"]["currency"] = "USD"


class BillingUpdate(BaseModel):
    """Schema for updating existing billing records"""
    hours: Optional[Decimal] = None
    fees: Optional[Decimal] = None
    billing_date: Optional[date] = None
    matter_id: Optional[UUID] = None
    is_afa: Optional[bool] = None
    currency: Optional[str] = None
    department_id: Optional[UUID] = None
    practice_area: Optional[str] = None
    office_id: Optional[UUID] = None
    office_location: Optional[str] = None

    @validator('hours')
    def validate_hours(cls, value):
        if value is not None:
            validate_number(value, "hours", min_value=Decimal('0'))
        return value

    @validator('fees')
    def validate_fees(cls, value):
        if value is not None:
            validate_number(value, "fees", min_value=Decimal('0'))
        return value

    @validator('currency')
    def validate_currency(cls, value):
        if value is not None:
            validate_currency(value, "currency")
        return value

    class Config:
        orm_mode = True


class BillingInDB(BillingBase):
    """Schema for billing data in the database"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[UUID] = None
    is_deleted: bool = False

    class Config:
        orm_mode = True


class BillingResponse(BaseModel):
    """Schema for billing data in API responses"""
    id: UUID
    attorney_id: UUID
    attorney_name: str
    client_id: UUID
    client_name: str
    matter_id: Optional[UUID] = None
    matter_name: Optional[str] = None
    hours: Decimal
    fees: Decimal
    billing_date: date
    is_afa: bool
    currency: str
    department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    practice_area: Optional[str] = None
    office_id: Optional[UUID] = None
    office_name: Optional[str] = None
    office_location: Optional[str] = None
    effective_rate: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    @root_validator
    def calculate_effective_rate(cls, values):
        hours = values.get("hours")
        fees = values.get("fees")
        
        if hours and fees and hours > 0:
            values["effective_rate"] = fees / hours
        else:
            values["effective_rate"] = None
        
        return values

    class Config:
        orm_mode = True


class BillingFilter(BaseModel):
    """Schema for filtering billing records"""
    attorney_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    matter_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_afa: Optional[bool] = None
    currency: Optional[str] = None
    department_id: Optional[UUID] = None
    practice_area: Optional[str] = None
    office_id: Optional[UUID] = None
    office_location: Optional[str] = None

    @root_validator
    def validate_date_range(cls, values):
        start_date = values.get("start_date")
        end_date = values.get("end_date")
        
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")
        
        return values

    class Config:
        orm_mode = True


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"

    @root_validator
    def validate_pagination(cls, values):
        page = values.get("page", 1)
        page_size = values.get("page_size", DEFAULT_PAGE_SIZE)
        sort_order = values.get("sort_order", "asc")
        
        if page < 1:
            raise ValueError("page must be greater than or equal to 1")
        
        if page_size < 1 or page_size > MAX_PAGE_SIZE:
            raise ValueError(f"page_size must be between 1 and {MAX_PAGE_SIZE}")
        
        # Normalize sort_order
        if sort_order and sort_order.lower() not in ("asc", "desc"):
            raise ValueError("sort_order must be 'asc' or 'desc'")
        
        values["sort_order"] = sort_order.lower() if sort_order else "asc"
        
        return values

    class Config:
        # Set default values
        page = 1
        page_size = DEFAULT_PAGE_SIZE
        sort_order = "asc"


class PaginatedBillingResponse(BaseModel):
    """Schema for paginated list of billing records"""
    items: List[BillingResponse]
    total: int
    page: int
    page_size: int
    pages: int
    summary: Optional['BillingStatistics'] = None

    class Config:
        orm_mode = True


class BillingStatistics(BaseModel):
    """Schema for billing summary statistics"""
    total_hours: Decimal
    total_fees: Decimal
    afa_hours: Decimal
    afa_fees: Decimal
    attorney_count: int
    matter_count: int
    currency: str
    effective_rate: Optional[Decimal] = None
    afa_percentage_hours: Optional[Decimal] = None
    afa_percentage_fees: Optional[Decimal] = None
    practice_area_breakdown: Optional[Dict[str, Any]] = None
    monthly_breakdown: Optional[Dict[str, Any]] = None

    @root_validator
    def calculate_derived_metrics(cls, values):
        total_hours = values.get("total_hours")
        total_fees = values.get("total_fees")
        afa_hours = values.get("afa_hours")
        afa_fees = values.get("afa_fees")
        
        # Calculate effective rate
        if total_hours and total_hours > 0:
            values["effective_rate"] = total_fees / total_hours
        else:
            values["effective_rate"] = None
        
        # Calculate AFA percentages
        if total_hours and total_hours > 0:
            values["afa_percentage_hours"] = (afa_hours / total_hours) * 100
        else:
            values["afa_percentage_hours"] = None
            
        if total_fees and total_fees > 0:
            values["afa_percentage_fees"] = (afa_fees / total_fees) * 100
        else:
            values["afa_percentage_fees"] = None
        
        return values

    class Config:
        orm_mode = True


class MatterBillingResponse(BaseModel):
    """Schema for matter billing summary response"""
    id: UUID
    matter_id: UUID
    matter_name: str
    client_id: UUID
    client_name: str
    start_date: date
    end_date: date
    total_hours: Decimal
    total_fees: Decimal
    afa_hours: Decimal
    afa_fees: Decimal
    attorney_count: int
    currency: str
    effective_rate: Optional[Decimal] = None
    afa_percentage_hours: Optional[Decimal] = None
    afa_percentage_fees: Optional[Decimal] = None
    metrics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @root_validator
    def calculate_derived_metrics(cls, values):
        total_hours = values.get("total_hours")
        total_fees = values.get("total_fees")
        afa_hours = values.get("afa_hours")
        afa_fees = values.get("afa_fees")
        
        # Calculate effective rate
        if total_hours and total_hours > 0:
            values["effective_rate"] = total_fees / total_hours
        else:
            values["effective_rate"] = None
        
        # Calculate AFA percentages
        if total_hours and total_hours > 0:
            values["afa_percentage_hours"] = (afa_hours / total_hours) * 100
        else:
            values["afa_percentage_hours"] = None
            
        if total_fees and total_fees > 0:
            values["afa_percentage_fees"] = (afa_fees / total_fees) * 100
        else:
            values["afa_percentage_fees"] = None
        
        return values

    class Config:
        orm_mode = True


class BillingImport(BaseModel):
    """Schema for importing billing data"""
    records: List[Dict[str, Any]]
    field_mapping: Optional[Dict[str, str]] = None
    update_existing: Optional[bool] = False
    default_currency: Optional[str] = "USD"

    @validator('records')
    def validate_records(cls, value):
        if not value or len(value) == 0:
            raise ValueError("records list cannot be empty")
        return value

    class Config:
        # Default values
        update_existing = False
        default_currency = "USD"


class BillingImportResponse(BaseModel):
    """Schema for billing import operation response"""
    total_records: int
    imported_records: int
    updated_records: int
    skipped_records: int
    error_records: int
    errors: List[Dict[str, Any]]
    success: bool

    @root_validator
    def calculate_success(cls, values):
        error_records = values.get("error_records", 0)
        values["success"] = error_records == 0
        return values

    class Config:
        orm_mode = True


class BillingExport(BaseModel):
    """Schema for exporting billing data"""
    format: str
    filter: Optional[BillingFilter] = None
    fields: Optional[List[str]] = None
    filename: Optional[str] = None

    @validator('format')
    def validate_format(cls, value):
        allowed_formats = ['csv', 'excel', 'json']
        if value.lower() not in allowed_formats:
            raise ValueError(f"format must be one of: {', '.join(allowed_formats)}")
        return value.lower()

    class Config:
        orm_mode = True


class RateImpactRequest(BaseModel):
    """Schema for rate impact analysis request"""
    client_id: UUID
    firm_id: Optional[UUID] = None
    current_rates: List[Dict[str, Any]]
    proposed_rates: List[Dict[str, Any]]
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    currency: Optional[str] = "USD"

    @root_validator
    def validate_rate_data(cls, values):
        current_rates = values.get("current_rates")
        proposed_rates = values.get("proposed_rates")
        
        if not current_rates or len(current_rates) == 0:
            raise ValueError("current_rates list cannot be empty")
            
        if not proposed_rates or len(proposed_rates) == 0:
            raise ValueError("proposed_rates list cannot be empty")
        
        # Validate that rate data contains required fields
        required_fields = ["attorney_id", "rate"]
        for rate in current_rates + proposed_rates:
            missing_fields = [field for field in required_fields if field not in rate]
            if missing_fields:
                raise ValueError(f"Rate data missing required fields: {', '.join(missing_fields)}")
        
        # Ensure rate arrays have matching attorney IDs (each attorney in proposed should be in current)
        current_attorney_ids = {r["attorney_id"] for r in current_rates}
        proposed_attorney_ids = {r["attorney_id"] for r in proposed_rates}
        
        missing_attorneys = proposed_attorney_ids - current_attorney_ids
        if missing_attorneys:
            raise ValueError(f"Proposed rates include attorneys not in current rates: {missing_attorneys}")
        
        return values

    class Config:
        # Default values
        currency = "USD"


class RateImpactResponse(BaseModel):
    """Schema for rate impact analysis response"""
    client_id: UUID
    firm_id: Optional[UUID] = None
    total_hours: Decimal
    current_total: Decimal
    proposed_total: Decimal
    total_impact: Decimal
    impact_percentage: Decimal
    currency: str
    attorney_impact: List[Dict[str, Any]]
    staff_class_impact: Dict[str, Any]
    practice_area_impact: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class BillingTrendRequest(BaseModel):
    """Schema for billing trend analysis request"""
    attorney_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    firm_id: Optional[UUID] = None
    start_date: date
    end_date: date
    grouping: str = "month"
    currency: Optional[str] = "USD"

    @validator('grouping')
    def validate_grouping(cls, value):
        allowed_groupings = ['month', 'quarter', 'year']
        if value.lower() not in allowed_groupings:
            raise ValueError(f"grouping must be one of: {', '.join(allowed_groupings)}")
        return value.lower()

    @root_validator
    def validate_date_range(cls, values):
        start_date = values.get("start_date")
        end_date = values.get("end_date")
        grouping = values.get("grouping", "month")
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValueError("start_date must be before or equal to end_date")
            
            # Check that date range is not too large for selected grouping
            from dateutil.relativedelta import relativedelta
            
            if grouping == "month":
                # Limit to 60 months (5 years) for monthly grouping
                max_months = 60
                months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                if months_diff > max_months:
                    raise ValueError(f"Date range too large for monthly grouping (max {max_months} months)")
            
            elif grouping == "quarter":
                # Limit to 40 quarters (10 years) for quarterly grouping
                max_quarters = 40
                quarters_diff = ((end_date.year - start_date.year) * 4 + 
                                ((end_date.month - 1) // 3) - ((start_date.month - 1) // 3))
                if quarters_diff > max_quarters:
                    raise ValueError(f"Date range too large for quarterly grouping (max {max_quarters} quarters)")
            
            elif grouping == "year":
                # Limit to 20 years for yearly grouping
                max_years = 20
                years_diff = end_date.year - start_date.year
                if years_diff > max_years:
                    raise ValueError(f"Date range too large for yearly grouping (max {max_years} years)")
        
        return values

    class Config:
        # Default values
        grouping = "month"
        currency = "USD"


class BillingTrendPoint(BaseModel):
    """Schema for a single point in billing trend data"""
    period: str
    hours: Decimal
    fees: Decimal
    afa_hours: Decimal
    afa_fees: Decimal
    attorney_count: int
    matter_count: int
    effective_rate: Optional[Decimal] = None
    afa_percentage_hours: Optional[Decimal] = None
    afa_percentage_fees: Optional[Decimal] = None

    @root_validator
    def calculate_derived_metrics(cls, values):
        hours = values.get("hours")
        fees = values.get("fees")
        afa_hours = values.get("afa_hours")
        afa_fees = values.get("afa_fees")
        
        # Calculate effective rate
        if hours and hours > 0:
            values["effective_rate"] = fees / hours
        else:
            values["effective_rate"] = None
        
        # Calculate AFA percentages
        if hours and hours > 0:
            values["afa_percentage_hours"] = (afa_hours / hours) * 100
        else:
            values["afa_percentage_hours"] = None
            
        if fees and fees > 0:
            values["afa_percentage_fees"] = (afa_fees / fees) * 100
        else:
            values["afa_percentage_fees"] = None
        
        return values

    class Config:
        orm_mode = True


class AFAUtilizationResponse(BaseModel):
    """Schema for AFA utilization metrics response"""
    client_id: UUID
    client_name: str
    total_hours: Decimal
    total_fees: Decimal
    afa_hours: Decimal
    afa_fees: Decimal
    afa_percentage_hours: Decimal
    afa_percentage_fees: Decimal
    currency: str
    target: Dict[str, Decimal]
    firm_breakdown: Dict[str, Dict[str, Decimal]]
    practice_area_breakdown: Dict[str, Dict[str, Decimal]]

    class Config:
        orm_mode = True