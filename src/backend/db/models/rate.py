"""
SQLAlchemy model for attorney billing rates in the Justice Bid Rate Negotiation System.

This model provides a comprehensive representation of rate information including 
historical tracking, validation, and analysis capabilities to support the core 
rate negotiation functionality.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Union
import uuid

from sqlalchemy import Column, ForeignKey, String, Numeric, Date, Enum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates

from ..base import Base
from .common import TimestampMixin
from ...utils.constants import RateStatus, RateType
from ...utils.validators import validate_currency


class Rate(Base, TimestampMixin):
    """
    SQLAlchemy model for attorney billing rates, supporting the rate negotiation process
    with historical tracking and validation capabilities.
    
    Attributes:
        id (UUID): Primary key
        attorney_id (UUID): Foreign key to attorney
        client_id (UUID): Foreign key to client organization
        firm_id (UUID): Foreign key to law firm organization
        office_id (UUID): Foreign key to office location
        staff_class_id (UUID): Foreign key to staff class (e.g., Partner, Associate)
        amount (Numeric): Rate amount
        currency (String): Currency code (e.g., USD, EUR)
        type (Enum): Rate type (Standard, Approved, Proposed, CounterProposed)
        effective_date (Date): Start date for the rate
        expiration_date (Date): End date for the rate
        status (Enum): Current status (Draft, Submitted, UnderReview, Approved, Rejected)
        history (JSONB): Historical record of rate changes
    """
    __tablename__ = 'rates'

    # Primary key
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    attorney_id = Column(UUID, ForeignKey('attorneys.id'), nullable=False)
    client_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    firm_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    office_id = Column(UUID, ForeignKey('offices.id'), nullable=False)
    staff_class_id = Column(UUID, ForeignKey('staff_classes.id'), nullable=False)
    
    # Rate information
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    type = Column(Enum(RateType), nullable=False, default=RateType.STANDARD)
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=True)
    status = Column(Enum(RateStatus), nullable=False, default=RateStatus.DRAFT)
    
    # Historical record
    history = Column(JSONB, nullable=False, default=list)
    
    # Relationships
    attorney = relationship("Attorney", back_populates="rates")
    client = relationship("Organization", foreign_keys=[client_id])
    firm = relationship("Organization", foreign_keys=[firm_id])
    office = relationship("Office")
    staff_class = relationship("StaffClass")
    negotiations = relationship("Negotiation", secondary="negotiation_rates")
    
    def __init__(self, 
                 attorney_id: uuid.UUID,
                 client_id: uuid.UUID,
                 firm_id: uuid.UUID,
                 office_id: uuid.UUID,
                 staff_class_id: uuid.UUID,
                 amount: Decimal,
                 currency: str,
                 effective_date: date,
                 expiration_date: Optional[date] = None,
                 type: Union[RateType, str] = RateType.STANDARD,
                 status: Union[RateStatus, str] = RateStatus.DRAFT):
        """
        Initialize a new Rate instance with validation.
        
        Args:
            attorney_id: UUID of the attorney
            client_id: UUID of the client organization
            firm_id: UUID of the law firm organization
            office_id: UUID of the office location
            staff_class_id: UUID of the staff class
            amount: Rate amount
            currency: Currency code
            effective_date: Start date for the rate
            expiration_date: Optional end date for the rate
            type: Rate type (defaults to STANDARD)
            status: Rate status (defaults to DRAFT)
        """
        self.attorney_id = attorney_id
        self.client_id = client_id
        self.firm_id = firm_id
        self.office_id = office_id
        self.staff_class_id = staff_class_id
        self.amount = amount
        self.currency = currency
        
        # Handle string or enum for type and status
        if isinstance(type, str):
            self.type = RateType(type)
        else:
            self.type = type
            
        if isinstance(status, str):
            self.status = RateStatus(status)
        else:
            self.status = status
            
        self.effective_date = effective_date
        self.expiration_date = expiration_date
        self.history = []
    
    @validates('currency')
    def validate_currency(self, key, currency):
        """
        Validates that the currency code is in a valid format.
        
        Args:
            key: Field name being validated
            currency: Currency code to validate
            
        Returns:
            Validated currency code
            
        Raises:
            ValueError: If currency code is invalid
        """
        return validate_currency(currency)
    
    @validates('amount')
    def validate_amount(self, key, amount):
        """
        Validates that the rate amount is positive.
        
        Args:
            key: Field name being validated
            amount: Rate amount to validate
            
        Returns:
            Validated amount
            
        Raises:
            ValueError: If amount is negative or zero
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
            
        if amount <= 0:
            raise ValueError("Rate amount must be greater than zero")
        
        return amount
    
    @validates('effective_date', 'expiration_date')
    def validate_dates(self, key, date_value):
        """
        Validates that effective_date is before expiration_date when both are set.
        
        Args:
            key: Field name being validated
            date_value: Date value to validate
            
        Returns:
            Validated date
            
        Raises:
            ValueError: If dates are invalid
        """
        if key == 'expiration_date' and date_value is not None:
            if self.effective_date and date_value <= self.effective_date:
                raise ValueError("Expiration date must be after effective date")
        
        if key == 'effective_date' and self.expiration_date is not None:
            if date_value >= self.expiration_date:
                raise ValueError("Effective date must be before expiration date")
        
        return date_value
    
    def add_history_entry(self, previous_amount: Decimal, previous_status: str, 
                         previous_type: str, user_id: uuid.UUID, message: str):
        """
        Adds an entry to the rate change history.
        
        Args:
            previous_amount: Previous rate amount
            previous_status: Previous rate status
            previous_type: Previous rate type
            user_id: ID of user making the change
            message: Comment or explanation for the change
            
        Returns:
            None
        """
        # Create history entry
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': str(user_id),
            'previous_amount': str(previous_amount),
            'new_amount': str(self.amount),
            'previous_status': previous_status,
            'new_status': self.status.value,
            'previous_type': previous_type,
            'new_type': self.type.value,
            'message': message
        }
        
        # Initialize history if it doesn't exist
        if self.history is None:
            self.history = []
        
        # Add entry to history
        self.history.append(entry)
        
        # Update the updated_at timestamp
        self.updated_at = datetime.utcnow()
    
    def is_active(self, reference_date: Optional[date] = None) -> bool:
        """
        Checks if the rate is currently active based on date range.
        
        Args:
            reference_date: Date to check against (default is current date)
            
        Returns:
            True if the rate is active, False otherwise
        """
        if reference_date is None:
            reference_date = date.today()
        
        if reference_date < self.effective_date:
            return False
        
        if self.expiration_date and reference_date > self.expiration_date:
            return False
        
        return True
    
    def is_approved(self) -> bool:
        """
        Checks if the rate has been approved.
        
        Returns:
            True if the rate is approved, False otherwise
        """
        return self.status == RateStatus.APPROVED
    
    def calculate_increase_percentage(self, previous_rate: Decimal) -> Optional[float]:
        """
        Calculates the percentage increase from a previous rate.
        
        Args:
            previous_rate: Amount of the previous rate
            
        Returns:
            Percentage increase (or decrease if negative)
        """
        if not previous_rate or previous_rate == 0:
            return None
        
        if not isinstance(previous_rate, Decimal):
            previous_rate = Decimal(str(previous_rate))
        
        percentage = ((self.amount - previous_rate) / previous_rate) * 100
        return round(float(percentage), 2)
    
    def get_history_timeline(self) -> List[Dict[str, Any]]:
        """
        Returns a formatted timeline of rate changes.
        
        Returns:
            Chronological list of rate change events with formatted details
        """
        timeline = []
        
        # Add creation event
        timeline.append({
            'timestamp': self.created_at.isoformat(),
            'event_type': 'creation',
            'amount': str(self.amount),
            'currency': self.currency,
            'status': self.status.value,
            'type': self.type.value,
            'user_id': None,
            'message': 'Rate created'
        })
        
        # Add history entries
        for entry in self.history:
            timeline_entry = {
                'timestamp': entry.get('timestamp'),
                'event_type': 'update',
                'previous_amount': entry.get('previous_amount'),
                'new_amount': entry.get('new_amount'),
                'previous_status': entry.get('previous_status'),
                'new_status': entry.get('new_status'),
                'previous_type': entry.get('previous_type'),
                'new_type': entry.get('new_type'),
                'user_id': entry.get('user_id'),
                'message': entry.get('message')
            }
            timeline.append(timeline_entry)
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        
        return timeline