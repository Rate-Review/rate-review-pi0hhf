"""
SQLAlchemy model for billing history data in the Justice Bid Rate Negotiation System.
Stores historical billing records for attorneys, clients, and matters to support
rate impact analysis and historical data analysis.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, ForeignKey, String, Numeric, Date, Boolean, JSONB, relationship
from sqlalchemy.orm import validates

from ..base import Base, UUID
from .common import TimestampMixin, BaseModel, OrganizationScopedMixin, SoftDeleteMixin, AuditMixin
from ...utils.validators import validate_currency


class BillingHistory(Base, TimestampMixin):
    """
    SQLAlchemy model for historical billing records, tracking hours billed and fees
    for attorneys, clients, and matters.
    """
    __tablename__ = 'billing_history'

    id = Column(UUID, primary_key=True)
    attorney_id = Column(UUID, ForeignKey('attorneys.id'), nullable=False)
    client_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    matter_id = Column(UUID, ForeignKey('matters.id'), nullable=True)
    hours = Column(Numeric(10, 2), nullable=False)
    fees = Column(Numeric(10, 2), nullable=False)
    billing_date = Column(Date, nullable=False)
    is_afa = Column(Boolean, default=False, nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    department_id = Column(UUID, ForeignKey('departments.id'), nullable=True)
    practice_area = Column(String(100), nullable=True)
    office_id = Column(UUID, ForeignKey('offices.id'), nullable=True)
    office_location = Column(String(100), nullable=True)

    # Relationships
    attorney = relationship('Attorney', back_populates='billing_history')
    client = relationship('Organization', back_populates='client_billing_history')
    matter = relationship('Matter', back_populates='billing_history')

    def __init__(self, attorney_id, client_id, hours, fees, billing_date, matter_id=None, 
                 is_afa=False, currency='USD', department_id=None, practice_area=None, 
                 office_id=None, office_location=None):
        """
        Initializes a new BillingHistory instance.
        
        Args:
            attorney_id: UUID of the attorney
            client_id: UUID of the client organization
            hours: Number of hours billed
            fees: Amount of fees billed
            billing_date: Date of the billing
            matter_id: Optional UUID of the matter
            is_afa: Whether this is an Alternative Fee Arrangement
            currency: Currency code (default: USD)
            department_id: Optional UUID of the department
            practice_area: Optional practice area
            office_id: Optional UUID of the office
            office_location: Optional office location
        """
        self.attorney_id = attorney_id
        self.client_id = client_id
        self.hours = hours
        self.fees = fees
        self.billing_date = billing_date
        self.matter_id = matter_id
        self.is_afa = is_afa
        self.currency = currency
        self.department_id = department_id
        self.practice_area = practice_area
        self.office_id = office_id
        self.office_location = office_location

    @validates('currency')
    def validate_currency(self, key, currency):
        """
        Validates that the currency code is in a valid format.
        
        Args:
            key: Field name
            currency: Currency code to validate
            
        Returns:
            Validated currency code
            
        Raises:
            ValueError: If currency code is invalid
        """
        return validate_currency(currency, 'currency')

    @validates('hours')
    def validate_hours(self, key, hours):
        """
        Validates that the hours value is non-negative.
        
        Args:
            key: Field name
            hours: Hours value to validate
            
        Returns:
            Validated hours
            
        Raises:
            ValueError: If hours is negative
        """
        if hours < 0:
            raise ValueError("Hours cannot be negative")
        return hours

    @validates('fees')
    def validate_fees(self, key, fees):
        """
        Validates that the fees value is non-negative.
        
        Args:
            key: Field name
            fees: Fees value to validate
            
        Returns:
            Validated fees
            
        Raises:
            ValueError: If fees is negative
        """
        if fees < 0:
            raise ValueError("Fees cannot be negative")
        return fees

    def get_effective_rate(self):
        """
        Calculates the effective hourly rate for this billing record.
        
        Returns:
            Decimal: Calculated effective rate or None if hours is zero
        """
        if self.hours == 0:
            return None
        return round(self.fees / self.hours, 2)

    def to_dict(self):
        """
        Convert the model instance to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the billing history record
        """
        result = {
            'id': str(self.id),
            'attorney_id': str(self.attorney_id),
            'client_id': str(self.client_id),
            'matter_id': str(self.matter_id) if self.matter_id else None,
            'hours': float(self.hours) if self.hours else 0,
            'fees': float(self.fees) if self.fees else 0,
            'billing_date': self.billing_date.isoformat() if self.billing_date else None,
            'is_afa': self.is_afa,
            'currency': self.currency,
            'department_id': str(self.department_id) if self.department_id else None,
            'practice_area': self.practice_area,
            'office_id': str(self.office_id) if self.office_id else None,
            'office_location': self.office_location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Add calculated effective rate if hours > 0
        if self.hours and self.hours > 0:
            result['effective_rate'] = float(self.get_effective_rate())
            
        return result

    @classmethod
    def from_dict(cls, data):
        """
        Create a BillingHistory instance from a dictionary.
        
        Args:
            data: Dictionary containing billing history attributes
            
        Returns:
            BillingHistory: New BillingHistory instance
        """
        return cls(
            attorney_id=data.get('attorney_id'),
            client_id=data.get('client_id'),
            hours=data.get('hours'),
            fees=data.get('fees'),
            billing_date=data.get('billing_date'),
            matter_id=data.get('matter_id'),
            is_afa=data.get('is_afa', False),
            currency=data.get('currency', 'USD'),
            department_id=data.get('department_id'),
            practice_area=data.get('practice_area'),
            office_id=data.get('office_id'),
            office_location=data.get('office_location')
        )


class MatterBillingSummary(Base, TimestampMixin):
    """
    SQLAlchemy model for aggregated billing summaries by matter, providing 
    pre-calculated metrics for performance analysis.
    """
    __tablename__ = 'matter_billing_summaries'

    id = Column(UUID, primary_key=True)
    matter_id = Column(UUID, ForeignKey('matters.id'), nullable=False)
    client_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_hours = Column(Numeric(12, 2), nullable=False)
    total_fees = Column(Numeric(14, 2), nullable=False)
    afa_hours = Column(Numeric(12, 2), default=0, nullable=False)
    afa_fees = Column(Numeric(14, 2), default=0, nullable=False)
    attorney_count = Column(Numeric(5, 0), default=0, nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    metrics = Column(JSONB, default={}, nullable=True)

    # Relationships
    client = relationship('Organization', back_populates='matter_billing_summaries')
    matter = relationship('Matter', back_populates='billing_summaries')

    def __init__(self, matter_id, client_id, start_date, end_date, total_hours, total_fees,
                 afa_hours=0, afa_fees=0, attorney_count=0, currency='USD', metrics=None):
        """
        Initializes a new MatterBillingSummary instance.
        
        Args:
            matter_id: UUID of the matter
            client_id: UUID of the client organization
            start_date: Start date of the billing period
            end_date: End date of the billing period
            total_hours: Total hours billed for the matter
            total_fees: Total fees billed for the matter
            afa_hours: Hours billed under AFA
            afa_fees: Fees billed under AFA
            attorney_count: Number of attorneys who worked on the matter
            currency: Currency code (default: USD)
            metrics: Additional metrics stored as JSON
        """
        self.matter_id = matter_id
        self.client_id = client_id
        self.start_date = start_date
        self.end_date = end_date
        self.total_hours = total_hours
        self.total_fees = total_fees
        self.afa_hours = afa_hours
        self.afa_fees = afa_fees
        self.attorney_count = attorney_count
        self.currency = currency
        self.metrics = metrics or {}

    @validates('currency')
    def validate_currency(self, key, currency):
        """
        Validates that the currency code is in a valid format.
        
        Args:
            key: Field name
            currency: Currency code to validate
            
        Returns:
            Validated currency code
            
        Raises:
            ValueError: If currency code is invalid
        """
        return validate_currency(currency, 'currency')

    def get_afa_percentage(self):
        """
        Calculate the percentage of hours and fees billed under AFA.
        
        Returns:
            dict: Dictionary with hours_percentage and fees_percentage
        """
        hours_percentage = 0
        fees_percentage = 0
        
        if self.total_hours > 0:
            hours_percentage = (self.afa_hours / self.total_hours) * 100
            
        if self.total_fees > 0:
            fees_percentage = (self.afa_fees / self.total_fees) * 100
            
        return {
            'hours_percentage': round(hours_percentage, 2),
            'fees_percentage': round(fees_percentage, 2)
        }

    def get_effective_rate(self):
        """
        Calculate the effective hourly rate for this matter.
        
        Returns:
            Decimal: Calculated effective rate or None if total_hours is zero
        """
        if self.total_hours == 0:
            return None
        return round(self.total_fees / self.total_hours, 2)

    def update_metrics(self, new_metrics):
        """
        Update or add additional metrics to the summary.
        
        Args:
            new_metrics: Dictionary of metrics to update or add
            
        Returns:
            None: Updates the metrics attribute in place
        """
        if self.metrics is None:
            self.metrics = {}
            
        self.metrics.update(new_metrics)
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """
        Convert the model instance to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the matter billing summary
        """
        result = {
            'id': str(self.id),
            'matter_id': str(self.matter_id),
            'client_id': str(self.client_id),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_hours': float(self.total_hours) if self.total_hours else 0,
            'total_fees': float(self.total_fees) if self.total_fees else 0,
            'afa_hours': float(self.afa_hours) if self.afa_hours else 0,
            'afa_fees': float(self.afa_fees) if self.afa_fees else 0,
            'attorney_count': int(self.attorney_count) if self.attorney_count else 0,
            'currency': self.currency,
            'metrics': self.metrics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Add calculated fields
        result['effective_rate'] = float(self.get_effective_rate()) if self.total_hours > 0 else None
        result['afa_percentage'] = self.get_afa_percentage()
            
        return result