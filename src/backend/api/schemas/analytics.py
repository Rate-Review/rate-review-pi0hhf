"""
Pydantic schema definitions for analytics API requests and responses.

This module defines schemas for various analytics operations in the Justice Bid
Rate Negotiation System, including rate impact analysis, historical trends, 
peer comparison, attorney performance metrics, and custom reporting.
"""

from typing import List, Dict, Any, Optional, Union
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, validator, Field, root_validator, condecimal

from .rates import PageParams, Page
from ...utils.constants import RateType, RateStatus
from ...utils.validators import validate_currency_code


class ImpactAnalysisRequest(BaseModel):
    """Schema for requesting rate impact analysis calculations."""
    client_id: UUID
    firm_id: UUID
    rate_ids: List[UUID]
    view_type: Optional[str] = "total"
    currency: Optional[str] = "USD"
    reference_start_date: Optional[date] = None
    reference_end_date: Optional[date] = None
    filters: Optional[Dict[str, Any]] = None

    @validator('currency')
    def validate_currency(cls, v):
        """Validates that the currency code is valid."""
        return validate_currency_code(v, 'currency')

    @validator('view_type')
    def validate_view_type(cls, v):
        """Validates that the view_type is one of the supported options."""
        valid_types = ['total', 'incremental', 'multi-year']
        if v not in valid_types:
            raise ValueError(f"view_type must be one of {valid_types}")
        return v


class ImpactAnalysisResponse(BaseModel):
    """Schema for rate impact analysis results."""
    client_id: UUID
    firm_id: UUID
    view_type: str
    currency: str
    total_impact: condecimal(ge=0, decimal_places=2)
    percentage_increase: float
    breakdown_by_staff_class: Dict[str, Any]
    breakdown_by_office: Dict[str, Any]
    peer_comparison: Optional[Dict[str, Any]] = None
    visualization_data: Dict[str, Any]


class MultiYearImpactRequest(BaseModel):
    """Schema for requesting multi-year impact projections."""
    client_id: UUID
    firm_id: UUID
    rate_ids: List[UUID]
    projection_years: int
    currency: Optional[str] = "USD"
    reference_start_date: Optional[date] = None
    reference_end_date: Optional[date] = None
    growth_assumptions: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None

    @validator('projection_years')
    def validate_projection_years(cls, v):
        """Validates that projection_years is within a reasonable range."""
        if v < 1 or v > 10:
            raise ValueError("projection_years must be between 1 and 10")
        return v

    @validator('currency')
    def validate_currency(cls, v):
        """Validates that the currency code is valid."""
        return validate_currency_code(v, 'currency')


class MultiYearImpactResponse(BaseModel):
    """Schema for multi-year impact projection results."""
    client_id: UUID
    firm_id: UUID
    currency: str
    projection_years: int
    cumulative_impact: condecimal(ge=0, decimal_places=2)
    average_annual_increase: float
    yearly_projections: List[Dict[str, Any]]
    visualization_data: Dict[str, Any]


class RateTrendRequest(BaseModel):
    """Schema for requesting historical rate trend analysis."""
    entity_type: str
    entity_id: UUID
    related_id: Optional[UUID] = None
    years: Optional[int] = 5
    currency: Optional[str] = "USD"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    group_by: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

    @validator('entity_type')
    def validate_entity_type(cls, v):
        """Validates that entity_type is one of the supported options."""
        valid_types = ['attorney', 'client', 'firm']
        if v not in valid_types:
            raise ValueError(f"entity_type must be one of {valid_types}")
        return v

    @validator('currency')
    def validate_currency(cls, v):
        """Validates that the currency code is valid."""
        return validate_currency_code(v, 'currency')

    @validator('group_by')
    def validate_group_by(cls, v):
        """Validates that group_by is one of the supported options."""
        if v is None:
            return v
        valid_options = ['staff_class', 'practice_area', 'office', 'attorney']
        if v not in valid_options:
            raise ValueError(f"group_by must be one of {valid_options}")
        return v


class RateTrendResponse(BaseModel):
    """Schema for historical rate trend analysis results."""
    entity_type: str
    entity_id: UUID
    entity_name: str
    years: int
    currency: str
    cagr: float
    inflation_comparison: Dict[str, float]
    yearly_rates: Dict[str, List[Dict[str, Any]]]
    visualization_data: Dict[str, Any]
    grouped_trends: Optional[Dict[str, Any]] = None
    seasonal_patterns: Optional[Dict[str, Any]] = None


class PeerComparisonRequest(BaseModel):
    """Schema for requesting peer comparison analytics."""
    organization_id: UUID
    peer_group_id: UUID
    comparison_type: Optional[str] = "overall"
    currency: Optional[str] = "USD"
    as_of_date: Optional[date] = None
    filters: Optional[Dict[str, Any]] = None

    @validator('comparison_type')
    def validate_comparison_type(cls, v):
        """Validates that comparison_type is one of the supported options."""
        valid_types = ['overall', 'staff_class', 'practice_area', 'geography']
        if v not in valid_types:
            raise ValueError(f"comparison_type must be one of {valid_types}")
        return v

    @validator('currency')
    def validate_currency(cls, v):
        """Validates that the currency code is valid."""
        return validate_currency_code(v, 'currency')


class PeerComparisonResponse(BaseModel):
    """Schema for peer comparison analytics results."""
    organization_id: UUID
    organization_name: str
    peer_group_id: UUID
    peer_group_name: str
    comparison_type: str
    currency: str
    as_of_date: date
    overall_comparison: Dict[str, Any]
    detailed_comparison: Optional[Dict[str, Dict[str, Any]]] = None
    visualization_data: Dict[str, Any]


class AttorneyPerformanceRequest(BaseModel):
    """Schema for requesting attorney performance analytics."""
    attorney_id: UUID
    client_id: Optional[UUID] = None
    metrics: Optional[List[str]] = None
    include_unicourt: Optional[bool] = True
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    filters: Optional[Dict[str, Any]] = None

    @validator('metrics')
    def validate_metrics(cls, v):
        """Validates that requested metrics are supported."""
        if v is None:
            return ['utilization', 'efficiency', 'realization', 'court_activity', 'win_rate']
        
        supported_metrics = ['utilization', 'efficiency', 'realization', 'court_activity', 'win_rate']
        for metric in v:
            if metric not in supported_metrics:
                raise ValueError(f"Unsupported metric: {metric}. Must be one of {supported_metrics}")
        return v


class AttorneyPerformanceResponse(BaseModel):
    """Schema for attorney performance analytics results."""
    attorney_id: UUID
    attorney_name: str
    client_id: Optional[UUID] = None
    client_name: Optional[str] = None
    billing_metrics: Dict[str, Any]
    unicourt_metrics: Optional[Dict[str, Any]] = None
    performance_trends: Dict[str, Any]
    visualization_data: Dict[str, Any]
    peer_percentiles: Dict[str, Any]


class CustomReportDefinition(BaseModel):
    """Schema for defining custom analytics reports."""
    id: Optional[UUID] = None
    name: str
    description: str
    owner_id: UUID
    organization_id: Optional[UUID] = None
    report_type: str
    parameters: Dict[str, Any]
    visualizations: List[Dict[str, Any]]
    schedule: Optional[Dict[str, Any]] = None
    shared_with: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('report_type')
    def validate_report_type(cls, v):
        """Validates that report_type is one of the supported options."""
        valid_types = ['impact', 'trends', 'comparison', 'performance', 'custom']
        if v not in valid_types:
            raise ValueError(f"report_type must be one of {valid_types}")
        return v


class CustomReportRequest(BaseModel):
    """Schema for requesting execution of a custom report."""
    report_id: Optional[UUID] = None
    report_definition: Optional[CustomReportDefinition] = None
    parameters_override: Optional[Dict[str, Any]] = None
    output_format: Optional[str] = "json"

    @root_validator
    def validate_request(cls, values):
        """Validates that either report_id or report_definition is provided."""
        report_id = values.get('report_id')
        report_definition = values.get('report_definition')
        
        if report_id is None and report_definition is None:
            raise ValueError("Either report_id or report_definition must be provided")
        
        if report_id is not None and report_definition is not None:
            raise ValueError("Only one of report_id or report_definition should be provided")
            
        return values

    @validator('output_format')
    def validate_output_format(cls, v):
        """Validates that output_format is one of the supported options."""
        valid_formats = ['json', 'csv', 'excel', 'pdf']
        if v not in valid_formats:
            raise ValueError(f"output_format must be one of {valid_formats}")
        return v


class CustomReportResponse(BaseModel):
    """Schema for custom report execution results."""
    report_id: UUID
    report_name: str
    parameters: Dict[str, Any]
    results: Dict[str, Any]
    visualizations: List[Dict[str, Any]]
    execution_time: datetime
    output_format: Optional[str] = None
    file_content: Optional[bytes] = None


class SavedReportListRequest(PageParams):
    """Schema for requesting list of saved reports."""
    organization_id: Optional[UUID] = None
    report_type: Optional[str] = None
    search: Optional[str] = None
    include_shared: Optional[bool] = True


class SavedReportListResponse(Page[CustomReportDefinition]):
    """Schema for paginated list of saved reports."""
    pass


class TimeSeriesPoint(BaseModel):
    """Schema for a single data point in a time series."""
    x: Union[date, str]
    y: float
    metadata: Optional[Dict[str, Any]] = None


class TimeSeriesSeries(BaseModel):
    """Schema for a series of data points in a visualization."""
    name: str
    color: Optional[str] = None
    data: List[TimeSeriesPoint]
    metadata: Optional[Dict[str, Any]] = None


class Visualization(BaseModel):
    """Schema for visualization data structure used across analytics responses."""
    type: str
    title: str
    subtitle: Optional[str] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    series: List[TimeSeriesSeries]
    options: Optional[Dict[str, Any]] = None

    @validator('type')
    def validate_type(cls, v):
        """Validates that visualization type is supported."""
        valid_types = ['line', 'bar', 'stacked_bar', 'pie', 'scatter', 'heatmap', 'radar']
        if v not in valid_types:
            raise ValueError(f"type must be one of {valid_types}")
        return v


class TopAttorneysRequest(BaseModel):
    """Schema for requesting top-performing attorneys based on metrics."""
    organization_id: UUID
    organization_type: Optional[str] = "firm"
    metrics: Optional[List[str]] = None
    limit: Optional[int] = 10
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    filters: Optional[Dict[str, Any]] = None

    @validator('organization_type')
    def validate_organization_type(cls, v):
        """Validates that organization_type is valid."""
        valid_types = ['firm', 'client']
        if v not in valid_types:
            raise ValueError(f"organization_type must be one of {valid_types}")
        return v

    @validator('limit')
    def validate_limit(cls, v):
        """Validates that limit is within acceptable range."""
        if v < 1 or v > 100:
            raise ValueError("limit must be between 1 and 100")
        return v


class TopAttorneysResponse(BaseModel):
    """Schema for results of top attorneys analysis."""
    organization_id: UUID
    organization_name: str
    organization_type: str
    attorneys: List[Dict[str, Any]]
    metrics: List[str]
    start_date: date
    end_date: date
    visualization_data: Dict[str, Any]