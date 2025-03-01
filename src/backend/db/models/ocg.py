"""
SQLAlchemy ORM models for Outside Counsel Guidelines (OCG) in the Justice Bid Rate Negotiation System.

This module defines the database models for managing Outside Counsel Guidelines, which are documents
created by clients to establish rules and requirements for law firms. The models support hierarchical 
sections, negotiable alternatives with point values, and tracking law firm selections during negotiation.
"""

import uuid
import datetime
from typing import Dict, List, Optional, Any, Union

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum, Text, DateTime, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSONB, UUID

from ..base import Base
from .common import BaseModel, TimestampMixin, AuditMixin, SoftDeleteMixin
from ...utils.constants import OCGStatus, OrganizationType


# Association table for tracking custom point budgets for firms
ocg_firm_point_budgets = Table(
    'ocg_firm_point_budgets',
    Base.metadata,
    Column('ocg_id', UUID, ForeignKey('ocgs.id'), primary_key=True),
    Column('firm_id', UUID, ForeignKey('organizations.id'), primary_key=True),
    Column('points', Integer, nullable=False),
    Column('created_at', DateTime, default=datetime.datetime.utcnow, nullable=False),
    Column('updated_at', DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
)


def generate_default_settings() -> Dict[str, Any]:
    """
    Generate default settings for a new OCG.
    
    Returns:
        Dict[str, Any]: Default OCG settings
    """
    return {
        'document_template': None,
        'signature_required': True,
        'notification_settings': {
            'email_notifications': True,
            'notification_recipients': []
        }
    }


class OCG(Base):
    """
    SQLAlchemy model representing Outside Counsel Guidelines (OCGs) that define the rules 
    and requirements for law firms working with clients. OCGs contain sections that can be 
    negotiable with alternative options.
    """
    __tablename__ = 'ocgs'
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    status = Column(Enum(OCGStatus), default=OCGStatus.DRAFT, nullable=False)
    total_points = Column(Integer, default=10, nullable=False)
    default_firm_point_budget = Column(Integer, default=5, nullable=False)
    published_at = Column(DateTime, nullable=True)
    signed_at = Column(DateTime, nullable=True)
    settings = Column(JSONB, nullable=True, default=generate_default_settings)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    client = relationship('Organization', foreign_keys=[client_id], backref='ocgs')
    sections = relationship('OCGSection', back_populates='ocg', cascade='all, delete-orphan', order_by='OCGSection.order')
    firm_selections = relationship('OCGFirmSelection', back_populates='ocg', cascade='all, delete-orphan')
    
    def __init__(self, client_id: uuid.UUID, name: str, version: Optional[int] = None, 
                 total_points: Optional[int] = None, default_firm_point_budget: Optional[int] = None):
        """
        Initialize a new OCG instance.
        
        Args:
            client_id: UUID of the client organization
            name: Name of the OCG
            version: Version number (defaults to 1)
            total_points: Total points available for negotiations (defaults to 10)
            default_firm_point_budget: Default point budget for firms (defaults to 5)
        """
        self.client_id = client_id
        self.name = name
        self.version = version or 1
        self.status = OCGStatus.DRAFT
        self.total_points = total_points or 10
        self.default_firm_point_budget = default_firm_point_budget or 5
        self.settings = generate_default_settings()
    
    def add_section(self, title: str, content: str, is_negotiable: bool = False, 
                    parent_id: Optional[uuid.UUID] = None) -> 'OCGSection':
        """
        Add a new section to the OCG.
        
        Args:
            title: Section title
            content: Section content text
            is_negotiable: Whether the section can be negotiated
            parent_id: ID of parent section if this is a subsection
            
        Returns:
            OCGSection: The newly created section
        """
        # Calculate next order value
        if parent_id:
            parent = next((s for s in self.sections if s.id == parent_id), None)
            if parent:
                max_order = max([s.order for s in parent.subsections], default=-1)
                order = max_order + 1
            else:
                order = 0
        else:
            max_order = max([s.order for s in self.sections if s.parent_id is None], default=-1)
            order = max_order + 1
        
        section = OCGSection(
            ocg_id=self.id,
            title=title,
            content=content,
            is_negotiable=is_negotiable,
            parent_id=parent_id,
            order=order
        )
        
        self.sections.append(section)
        return section
    
    def get_sections_hierarchy(self) -> List['OCGSection']:
        """
        Get OCG sections organized in a hierarchical structure.
        
        Returns:
            List[OCGSection]: Top-level sections with nested subsections
        """
        top_level_sections = [s for s in self.sections if s.parent_id is None]
        # Sort by order
        top_level_sections.sort(key=lambda x: x.order)
        return top_level_sections
    
    def publish(self) -> bool:
        """
        Publish the OCG, making it available for negotiation.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.status != OCGStatus.DRAFT:
            return False
        
        self.status = OCGStatus.PUBLISHED
        self.published_at = datetime.datetime.utcnow()
        return True
    
    def start_negotiation(self) -> bool:
        """
        Start the negotiation process with a law firm.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.status != OCGStatus.PUBLISHED:
            return False
        
        self.status = OCGStatus.NEGOTIATING
        return True
    
    def sign(self) -> bool:
        """
        Mark the OCG as signed, finalizing the negotiation.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.status != OCGStatus.NEGOTIATING:
            return False
        
        self.status = OCGStatus.SIGNED
        self.signed_at = datetime.datetime.utcnow()
        return True
    
    def get_negotiable_sections(self) -> List['OCGSection']:
        """
        Get all negotiable sections in the OCG.
        
        Returns:
            List[OCGSection]: List of negotiable sections
        """
        return [s for s in self.sections if s.is_negotiable]
    
    def get_firm_point_budget(self, firm_id: uuid.UUID) -> int:
        """
        Get the point budget for a specific law firm.
        
        Args:
            firm_id: UUID of the law firm
            
        Returns:
            int: Point budget for the firm
        """
        # Check for custom budget
        from sqlalchemy.orm import Session
        from sqlalchemy import select
        
        session = Session.object_session(self)
        if session:
            stmt = select(ocg_firm_point_budgets.c.points).where(
                ocg_firm_point_budgets.c.ocg_id == self.id,
                ocg_firm_point_budgets.c.firm_id == firm_id
            )
            result = session.execute(stmt).scalar_one_or_none()
            if result is not None:
                return result
        
        return self.default_firm_point_budget
    
    def set_firm_point_budget(self, firm_id: uuid.UUID, points: int) -> bool:
        """
        Set a custom point budget for a specific law firm.
        
        Args:
            firm_id: UUID of the law firm
            points: Point budget to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        if points < 0:
            return False
        
        from sqlalchemy.orm import Session
        from sqlalchemy import select
        
        session = Session.object_session(self)
        if not session:
            return False
        
        # Check if record exists
        stmt = select(ocg_firm_point_budgets).where(
            ocg_firm_point_budgets.c.ocg_id == self.id,
            ocg_firm_point_budgets.c.firm_id == firm_id
        )
        existing = session.execute(stmt).scalar_one_or_none()
        
        if existing:
            # Update existing record
            stmt = ocg_firm_point_budgets.update().where(
                ocg_firm_point_budgets.c.ocg_id == self.id,
                ocg_firm_point_budgets.c.firm_id == firm_id
            ).values(points=points, updated_at=datetime.datetime.utcnow())
            session.execute(stmt)
        else:
            # Insert new record
            stmt = ocg_firm_point_budgets.insert().values(
                ocg_id=self.id,
                firm_id=firm_id,
                points=points,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            session.execute(stmt)
        
        return True
    
    def get_firm_selections(self, firm_id: uuid.UUID) -> List['OCGFirmSelection']:
        """
        Get all selections made by a specific law firm.
        
        Args:
            firm_id: UUID of the law firm
            
        Returns:
            List[OCGFirmSelection]: List of firm selections
        """
        return [s for s in self.firm_selections if s.firm_id == firm_id]
    
    def get_firm_points_used(self, firm_id: uuid.UUID) -> int:
        """
        Calculate the total points used by a specific law firm.
        
        Args:
            firm_id: UUID of the law firm
            
        Returns:
            int: Total points used by the firm
        """
        selections = self.get_firm_selections(firm_id)
        return sum(s.points_used for s in selections)
    
    def get_remaining_point_budget(self, firm_id: uuid.UUID) -> int:
        """
        Calculate the remaining point budget for a specific law firm.
        
        Args:
            firm_id: UUID of the law firm
            
        Returns:
            int: Remaining point budget
        """
        budget = self.get_firm_point_budget(firm_id)
        used = self.get_firm_points_used(firm_id)
        return max(0, budget - used)
    
    def clone(self) -> 'OCG':
        """
        Create a new version of this OCG.
        
        Returns:
            OCG: The newly created OCG version
        """
        new_ocg = OCG(
            client_id=self.client_id,
            name=self.name,
            version=self.version + 1,
            total_points=self.total_points,
            default_firm_point_budget=self.default_firm_point_budget
        )
        
        # Copy settings
        if self.settings:
            new_ocg.settings = self.settings.copy()
        
        # Create section copies
        section_map = {}  # Maps old section IDs to new section objects
        
        # First, create all sections (without subsections to avoid circular references)
        for section in self.sections:
            new_section = OCGSection(
                ocg_id=new_ocg.id,
                title=section.title,
                content=section.content,
                is_negotiable=section.is_negotiable,
                order=section.order
            )
            new_ocg.sections.append(new_section)
            section_map[section.id] = new_section
        
        # Now set parent_id for subsections
        for section in self.sections:
            if section.parent_id:
                section_map[section.id].parent_id = section_map[section.parent_id].id
        
        # Create alternatives for each section
        for section in self.sections:
            if section.is_negotiable:
                for alt in section.alternatives:
                    new_alt = OCGAlternative(
                        section_id=section_map[section.id].id,
                        title=alt.title,
                        content=alt.content,
                        points=alt.points,
                        is_default=alt.is_default,
                        order=alt.order
                    )
                    section_map[section.id].alternatives.append(new_alt)
        
        return new_ocg
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value by key.
        
        Args:
            key: Setting key
            default: Default value if key is not found
            
        Returns:
            Any: The value for the specified key or the default if not found
        """
        if not self.settings:
            return default
        
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a specific setting value by key.
        
        Args:
            key: Setting key
            value: Setting value
        """
        if not self.settings:
            self.settings = {}
        
        self.settings[key] = value


class OCGSection(Base):
    """
    SQLAlchemy model representing a section within an OCG document. Sections can be hierarchical
    with parent-child relationships and can be marked as negotiable with alternatives.
    """
    __tablename__ = 'ocg_sections'
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    ocg_id = Column(UUID, ForeignKey('ocgs.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_negotiable = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    parent_id = Column(UUID, ForeignKey('ocg_sections.id'), nullable=True)
    
    # Relationships
    ocg = relationship('OCG', back_populates='sections')
    subsections = relationship('OCGSection', backref=backref('parent', remote_side=[id]), cascade='all, delete-orphan')
    alternatives = relationship('OCGAlternative', back_populates='section', cascade='all, delete-orphan', order_by='OCGAlternative.order')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    def __init__(self, ocg_id: uuid.UUID, title: str, content: str, 
                 is_negotiable: Optional[bool] = False, parent_id: Optional[uuid.UUID] = None, 
                 order: Optional[int] = 0):
        """
        Initialize a new OCGSection instance.
        
        Args:
            ocg_id: UUID of the parent OCG
            title: Section title
            content: Section content text
            is_negotiable: Whether the section can be negotiated
            parent_id: UUID of parent section if this is a subsection
            order: Order of this section within its parent
        """
        self.ocg_id = ocg_id
        self.title = title
        self.content = content
        self.is_negotiable = is_negotiable
        self.parent_id = parent_id
        self.order = order
    
    def add_alternative(self, title: str, content: str, points: int, 
                         is_default: Optional[bool] = None) -> 'OCGAlternative':
        """
        Add a new alternative option to this section.
        
        Args:
            title: Alternative title
            content: Alternative content text
            points: Point cost of this alternative
            is_default: Whether this is the default alternative
            
        Returns:
            OCGAlternative: The newly created alternative
        """
        if not self.is_negotiable:
            self.is_negotiable = True
        
        # Calculate next order value
        max_order = max([a.order for a in self.alternatives], default=-1)
        order = max_order + 1
        
        # Determine if this should be the default
        if is_default is None:
            is_default = len(self.alternatives) == 0
        
        alternative = OCGAlternative(
            section_id=self.id,
            title=title,
            content=content,
            points=points,
            is_default=is_default,
            order=order
        )
        
        self.alternatives.append(alternative)
        return alternative
    
    def add_subsection(self, title: str, content: str, 
                       is_negotiable: Optional[bool] = False) -> 'OCGSection':
        """
        Add a new subsection to this section.
        
        Args:
            title: Subsection title
            content: Subsection content text
            is_negotiable: Whether the subsection can be negotiated
            
        Returns:
            OCGSection: The newly created subsection
        """
        # Calculate next order value
        max_order = max([s.order for s in self.subsections], default=-1)
        order = max_order + 1
        
        subsection = OCGSection(
            ocg_id=self.ocg_id,
            title=title,
            content=content,
            is_negotiable=is_negotiable,
            parent_id=self.id,
            order=order
        )
        
        self.subsections.append(subsection)
        return subsection
    
    def get_default_alternative(self) -> Optional['OCGAlternative']:
        """
        Get the default alternative for this section.
        
        Returns:
            Optional[OCGAlternative]: The default alternative or None if not found
        """
        if not self.is_negotiable:
            return None
            
        for alt in self.alternatives:
            if alt.is_default:
                return alt
        
        return None
    
    def make_negotiable(self) -> 'OCGAlternative':
        """
        Make this section negotiable and add a default alternative.
        
        Returns:
            OCGAlternative: The default alternative
        """
        self.is_negotiable = True
        
        # Check if there's already a default alternative
        default_alt = self.get_default_alternative()
        if default_alt:
            return default_alt
        
        # Create default alternative with same content
        return self.add_alternative(
            title="Standard",
            content=self.content,
            points=0,
            is_default=True
        )


class OCGAlternative(Base):
    """
    SQLAlchemy model representing an alternative option for a negotiable section in an OCG.
    Each alternative has a point value that counts against a law firm's point budget when selected.
    """
    __tablename__ = 'ocg_alternatives'
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID, ForeignKey('ocg_sections.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    points = Column(Integer, default=0, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    section = relationship('OCGSection', back_populates='alternatives')
    selections = relationship('OCGFirmSelection', back_populates='alternative')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    def __init__(self, section_id: uuid.UUID, title: str, content: str, points: int,
                 is_default: Optional[bool] = False, order: Optional[int] = 0):
        """
        Initialize a new OCGAlternative instance.
        
        Args:
            section_id: UUID of the parent section
            title: Alternative title
            content: Alternative content text
            points: Point cost of this alternative
            is_default: Whether this is the default alternative
            order: Order of this alternative within its section
        """
        self.section_id = section_id
        self.title = title
        self.content = content
        self.points = points
        self.is_default = is_default
        self.order = order


class OCGFirmSelection(Base):
    """
    SQLAlchemy model representing a law firm's selection of an alternative for a negotiable
    section in an OCG. Tracks the points used from the firm's point budget.
    """
    __tablename__ = 'ocg_firm_selections'
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    ocg_id = Column(UUID, ForeignKey('ocgs.id'), nullable=False)
    firm_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    section_id = Column(UUID, ForeignKey('ocg_sections.id'), nullable=False)
    alternative_id = Column(UUID, ForeignKey('ocg_alternatives.id'), nullable=False)
    points_used = Column(Integer, nullable=False)
    selected_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    
    # Relationships
    ocg = relationship('OCG', back_populates='firm_selections')
    firm = relationship('Organization', foreign_keys=[firm_id])
    section = relationship('OCGSection', foreign_keys=[section_id])
    alternative = relationship('OCGAlternative', foreign_keys=[alternative_id])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    def __init__(self, ocg_id: uuid.UUID, firm_id: uuid.UUID, 
                 section_id: uuid.UUID, alternative_id: uuid.UUID, 
                 points_used: int):
        """
        Initialize a new OCGFirmSelection instance.
        
        Args:
            ocg_id: UUID of the OCG
            firm_id: UUID of the law firm
            section_id: UUID of the section
            alternative_id: UUID of the selected alternative
            points_used: Points used for this selection
        """
        self.ocg_id = ocg_id
        self.firm_id = firm_id
        self.section_id = section_id
        self.alternative_id = alternative_id
        self.points_used = points_used
        self.selected_at = datetime.datetime.utcnow()