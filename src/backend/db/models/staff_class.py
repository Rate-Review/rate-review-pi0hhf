"""
SQLAlchemy ORM model defining staff classes for attorney classification in the Justice Bid Rate Negotiation System.
Staff classes categorize attorneys based on experience levels and provide a structured approach to rate management.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import Column, String, ForeignKey, Enum, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates

from ..base import Base
from .common import TimestampMixin, AuditMixin, OrganizationScopedMixin, generate_uuid
from ...utils.constants import ExperienceType


class StaffClass(Base, TimestampMixin, AuditMixin, OrganizationScopedMixin):
    """
    SQLAlchemy model representing attorney staff classification in the Justice Bid system.
    Staff classes categorize attorneys based on experience level and provide a structured
    approach to rate management and analytics.
    """
    __tablename__ = 'staff_classes'

    id = Column(UUID, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    experience_type = Column(Enum(ExperienceType), nullable=False)
    min_experience = Column(Integer, nullable=False)
    max_experience = Column(Integer, nullable=True)
    practice_area = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata = Column(JSONB, nullable=True)

    # Relationships (organization relationship is provided by OrganizationScopedMixin)
    attorneys = relationship('Attorney', back_populates='staff_class')
    rates = relationship('Rate', back_populates='staff_class')

    def __init__(self, organization_id: uuid.UUID, name: str, experience_type: ExperienceType, 
                 min_experience: int, max_experience: Optional[int] = None, 
                 practice_area: Optional[str] = None):
        """
        Initialize a new StaffClass instance.
        
        Args:
            organization_id: UUID of the organization this staff class belongs to
            name: Name of the staff class (e.g., 'Partner', 'Senior Associate')
            experience_type: Type of experience metric used for classification
            min_experience: Minimum years/value of experience required
            max_experience: Maximum years/value of experience allowed (optional)
            practice_area: Practice area this staff class applies to (optional)
        """
        self.organization_id = organization_id
        self.name = name
        self.experience_type = experience_type
        self.min_experience = min_experience
        self.max_experience = max_experience
        self.practice_area = practice_area
        self.metadata = {}
        self.is_active = True

    @validates('min_experience', 'max_experience')
    def validate_experience_range(self, key: str, value: int) -> int:
        """
        Validates that min_experience is less than or equal to max_experience if max_experience is provided.
        
        Args:
            key: The attribute being validated ('min_experience' or 'max_experience')
            value: The proposed value for the attribute
            
        Returns:
            The validated value
            
        Raises:
            ValueError: If the validation fails
        """
        if key == 'min_experience' and self.max_experience is not None and value > self.max_experience:
            raise ValueError("Minimum experience cannot be greater than maximum experience")
        
        if key == 'max_experience' and value is not None and self.min_experience > value:
            raise ValueError("Maximum experience cannot be less than minimum experience")
            
        return value

    def is_attorney_eligible(self, attorney) -> bool:
        """
        Determines if an attorney is eligible for this staff class based on experience criteria.
        
        Args:
            attorney: The attorney object to check eligibility for
            
        Returns:
            True if the attorney is eligible for this staff class, False otherwise
        """
        # Calculate years of experience based on the experience type
        years = None
        today = datetime.utcnow().date()
        
        if self.experience_type == ExperienceType.GRADUATION_YEAR and attorney.graduation_date:
            years = today.year - attorney.graduation_date.year
        elif self.experience_type == ExperienceType.BAR_YEAR and attorney.bar_date:
            years = today.year - attorney.bar_date.year
        elif self.experience_type == ExperienceType.YEARS_IN_ROLE and attorney.promotion_date:
            years = today.year - attorney.promotion_date.year
        else:
            return False  # Missing required date field
            
        # Check if experience is within range
        if years is None:
            return False
            
        if years < self.min_experience:
            return False
            
        if self.max_experience is not None and years > self.max_experience:
            return False
            
        return True

    def get_eligible_attorneys(self) -> List['Attorney']:
        """
        Gets all attorneys in the organization who are eligible for this staff class.
        
        Returns:
            List of eligible Attorney objects
        """
        from sqlalchemy import select
        from sqlalchemy.orm import Session
        from .attorney import Attorney  # Import here to avoid circular imports
        
        session = Session.object_session(self)
        if not session:
            return []
            
        # Query all attorneys in the organization
        stmt = select(Attorney).where(Attorney.organization_id == self.organization_id)
        attorneys = session.execute(stmt).scalars().all()
        
        # Filter to only those who are eligible
        eligible_attorneys = [attorney for attorney in attorneys if self.is_attorney_eligible(attorney)]
        
        return eligible_attorneys

    def get_current_rates(self) -> List['Rate']:
        """
        Gets all current active rates for this staff class.
        
        Returns:
            List of active Rate objects
        """
        from sqlalchemy import select
        from sqlalchemy.orm import Session
        from .rate import Rate  # Import here to avoid circular imports
        from ...utils.constants import RateStatus
        
        session = Session.object_session(self)
        if not session:
            return []
            
        # Get current date for filtering active rates
        today = datetime.utcnow().date()
        
        # Query rates for this staff class
        stmt = select(Rate).where(
            Rate.staff_class_id == self.id,
            Rate.status == RateStatus.ACTIVE,
            Rate.effective_date <= today,
            (Rate.expiration_date == None) | (Rate.expiration_date >= today)  # noqa: E711
        )
        
        return session.execute(stmt).scalars().all()

    def activate(self) -> None:
        """
        Activates the staff class.
        """
        self.is_active = True

    def deactivate(self) -> None:
        """
        Deactivates the staff class.
        """
        self.is_active = False

    def update_metadata(self, new_metadata: Dict[str, Any]) -> None:
        """
        Updates the metadata for the staff class.
        
        Args:
            new_metadata: Dictionary containing metadata to update or add
        """
        if self.metadata is None:
            self.metadata = {}
            
        self.metadata.update(new_metadata)