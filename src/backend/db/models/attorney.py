"""
SQLAlchemy model for Attorney entities in the Justice Bid Rate Negotiation System.
"""

import uuid
from datetime import date, datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import Column, String, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from ..base import Base
from .common import TimestampMixin
from .organization import Organization
from .staff_class import StaffClass


class Attorney(Base, TimestampMixin):
    """
    SQLAlchemy model representing an attorney in the Justice Bid system.
    """
    __tablename__ = 'attorneys'
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    bar_date = Column(Date, nullable=True)
    graduation_date = Column(Date, nullable=True)
    promotion_date = Column(Date, nullable=True)
    office_ids = Column(ARRAY(UUID), nullable=True)
    timekeeper_ids = Column(JSONB, nullable=True)  # Maps client_id to timekeeper_id
    unicourt_id = Column(UUID, nullable=True)
    performance_data = Column(JSONB, nullable=True)
    staff_class_id = Column(UUID, ForeignKey('staff_classes.id'), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="attorneys")
    rates = relationship("Rate", back_populates="attorney")
    staff_class = relationship("StaffClass", back_populates="attorneys")
    
    def __init__(self, organization_id: uuid.UUID, name: str, bar_date: Optional[date] = None,
                 graduation_date: Optional[date] = None, promotion_date: Optional[date] = None,
                 office_ids: Optional[List[uuid.UUID]] = None, 
                 timekeeper_ids: Optional[Dict[str, str]] = None,
                 unicourt_id: Optional[uuid.UUID] = None,
                 staff_class_id: Optional[uuid.UUID] = None):
        """
        Initialize an Attorney instance.
        
        Args:
            organization_id: UUID of the law firm the attorney belongs to
            name: Full name of the attorney
            bar_date: Date when the attorney was admitted to the bar
            graduation_date: Date when the attorney graduated from law school
            promotion_date: Date when the attorney was last promoted
            office_ids: List of office UUIDs the attorney is associated with
            timekeeper_ids: Dictionary mapping client IDs to timekeeper IDs
            unicourt_id: UUID of the attorney in UniCourt system
            staff_class_id: UUID of the staff class the attorney belongs to
        """
        self.id = uuid.uuid4()
        self.organization_id = organization_id
        self.name = name
        self.bar_date = bar_date
        self.graduation_date = graduation_date
        self.promotion_date = promotion_date
        self.office_ids = office_ids or []
        self.timekeeper_ids = timekeeper_ids or {}
        self.unicourt_id = unicourt_id
        self.staff_class_id = staff_class_id
        self.performance_data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Attorney instance to a dictionary.
        
        Returns:
            Dictionary representation of the attorney
        """
        result = {
            'id': str(self.id),
            'organization_id': str(self.organization_id),
            'name': self.name,
            'bar_date': self.bar_date.isoformat() if self.bar_date else None,
            'graduation_date': self.graduation_date.isoformat() if self.graduation_date else None,
            'promotion_date': self.promotion_date.isoformat() if self.promotion_date else None,
            'office_ids': [str(office_id) for office_id in self.office_ids] if self.office_ids else [],
            'timekeeper_ids': self.timekeeper_ids,
            'unicourt_id': str(self.unicourt_id) if self.unicourt_id else None,
            'performance_data': self.performance_data,
            'staff_class_id': str(self.staff_class_id) if self.staff_class_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Attorney':
        """
        Create an Attorney instance from a dictionary.
        
        Args:
            data: Dictionary containing attorney attributes
            
        Returns:
            New Attorney instance
        """
        # Parse date fields
        bar_date = date.fromisoformat(data['bar_date']) if data.get('bar_date') else None
        graduation_date = date.fromisoformat(data['graduation_date']) if data.get('graduation_date') else None
        promotion_date = date.fromisoformat(data['promotion_date']) if data.get('promotion_date') else None
        
        # Parse UUID fields
        organization_id = uuid.UUID(data['organization_id'])
        unicourt_id = uuid.UUID(data['unicourt_id']) if data.get('unicourt_id') else None
        staff_class_id = uuid.UUID(data['staff_class_id']) if data.get('staff_class_id') else None
        
        # Parse office_ids
        office_ids = [uuid.UUID(office_id) for office_id in data.get('office_ids', [])]
        
        return cls(
            organization_id=organization_id,
            name=data['name'],
            bar_date=bar_date,
            graduation_date=graduation_date,
            promotion_date=promotion_date,
            office_ids=office_ids,
            timekeeper_ids=data.get('timekeeper_ids', {}),
            unicourt_id=unicourt_id,
            staff_class_id=staff_class_id
        )
    
    def update_performance_data(self, new_data: Dict[str, Any]) -> None:
        """
        Update attorney performance data from UniCourt or other sources.
        
        Args:
            new_data: New performance data to incorporate
        """
        if self.performance_data is None:
            self.performance_data = {}
        
        # Merge new data with existing data
        self.performance_data.update(new_data)
    
    def add_timekeeper_id(self, client_id: str, timekeeper_id: str) -> None:
        """
        Add a client-specific timekeeper ID.
        
        Args:
            client_id: String ID of the client
            timekeeper_id: Timekeeper ID used by the client
        """
        if self.timekeeper_ids is None:
            self.timekeeper_ids = {}
        
        self.timekeeper_ids[client_id] = timekeeper_id
    
    def get_timekeeper_id(self, client_id: str) -> Optional[str]:
        """
        Get timekeeper ID for a specific client.
        
        Args:
            client_id: String ID of the client
            
        Returns:
            Timekeeper ID or None if not found
        """
        if not self.timekeeper_ids:
            return None
        
        return self.timekeeper_ids.get(client_id)
    
    def get_current_rates(self) -> List:
        """
        Get current active rates for this attorney.
        
        Returns:
            List of active Rate objects
        """
        from sqlalchemy import select
        from sqlalchemy.orm import Session
        
        session = Session.object_session(self)
        if not session:
            return []
        
        # Importing here to avoid circular imports
        from .rate import Rate
        from ...utils.constants import RateStatus
        
        # Get current date for filtering active rates
        today = datetime.utcnow().date()
        
        # Query rates for this attorney that are currently active
        stmt = select(Rate).where(
            Rate.attorney_id == self.id,
            Rate.status == RateStatus.ACTIVE,
            Rate.effective_date <= today,
            (Rate.expiration_date == None) | (Rate.expiration_date >= today)  # noqa: E711
        )
        
        return session.execute(stmt).scalars().all()