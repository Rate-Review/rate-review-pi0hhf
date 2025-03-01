"""
SQLAlchemy ORM model defining the Organization entity in the Justice Bid Rate Negotiation System.
Organizations represent either law firms or clients that participate in rate negotiations.
This model provides the core data structure and relationships for organizational data,
supporting multi-tenancy and various organizational attributes.
"""

import uuid
from typing import Dict, Any, Optional
import datetime

from sqlalchemy import Column, String, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from ..base import Base
from .common import TimestampMixin, AuditMixin, SoftDeleteMixin, generate_uuid
from ...utils.constants import OrganizationType


class Organization(Base, TimestampMixin, SoftDeleteMixin):
    """
    SQLAlchemy model representing an organization in the Justice Bid system.
    Organizations can be law firms, clients, or system administrators,
    with each type having specific capabilities and relationships.
    """
    __tablename__ = 'organizations'
    
    id = Column(UUID, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    type = Column(Enum(OrganizationType), nullable=False)
    domain = Column(String(255), nullable=True)
    settings = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    users = relationship('User', back_populates='organization')
    attorneys = relationship('Attorney', back_populates='organization')
    offices = relationship('Office', back_populates='organization')
    departments = relationship('Department', back_populates='organization')
    staff_classes = relationship('StaffClass', back_populates='organization')
    peer_groups = relationship('PeerGroup', 
                             foreign_keys='PeerGroup.organization_id',
                             back_populates='organization')
    member_of_peer_groups = relationship('PeerGroup',
                                       secondary='peer_group_members',
                                       back_populates='member_organizations')
    client_negotiations = relationship('Negotiation',
                                     foreign_keys='Negotiation.client_id',
                                     back_populates='client')
    firm_negotiations = relationship('Negotiation',
                                   foreign_keys='Negotiation.firm_id',
                                   back_populates='firm')
    ocgs = relationship('OCG',
                       foreign_keys='OCG.client_id',
                       back_populates='client')
    
    def __init__(self, name: str, type: OrganizationType, domain: str = None):
        """Initialize a new Organization instance"""
        self.name = name
        self.type = type
        self.domain = domain
        self.settings = {}
        self.is_active = True
    
    def is_law_firm(self) -> bool:
        """Check if the organization is a law firm"""
        return self.type == OrganizationType.LAW_FIRM
    
    def is_client(self) -> bool:
        """Check if the organization is a client"""
        return self.type == OrganizationType.CLIENT
    
    def is_admin(self) -> bool:
        """Check if the organization is an admin organization"""
        return self.type == OrganizationType.ADMIN
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value by key"""
        if self.settings is None:
            return default
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a specific setting value by key"""
        if self.settings is None:
            self.settings = {}
        self.settings[key] = value
    
    def get_rate_rules(self) -> Dict:
        """Get the organization's rate rules from settings"""
        return self.settings.get('rate_rules', {}) if self.settings else {}
    
    def set_rate_rules(self, rate_rules: Dict) -> None:
        """Set the organization's rate rules"""
        if self.settings is None:
            self.settings = {}
        self.settings['rate_rules'] = rate_rules
    
    def add_department(self, name: str, metadata: Dict = None) -> 'Department':
        """Add a new department to the organization"""
        department = Department(organization_id=self.id, name=name, metadata=metadata)
        self.departments.append(department)
        return department
    
    def add_office(self, name: str, city: str, state: str = None, country: str = None, region: str = None) -> 'Office':
        """Add a new office to the organization"""
        office = Office(
            organization_id=self.id,
            name=name,
            city=city,
            state=state,
            country=country or "United States",
            region=region
        )
        self.offices.append(office)
        return office
    
    def activate(self) -> None:
        """Activate the organization"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the organization"""
        self.is_active = False
    
    def delete(self, deleted_by_id: Optional[uuid.UUID] = None) -> None:
        """Soft delete the organization"""
        self.is_deleted = True
        self.deleted_at = datetime.datetime.utcnow()
        if deleted_by_id:
            self.deleted_by_id = deleted_by_id
    
    def restore(self) -> None:
        """Restore a soft-deleted organization"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by_id = None


class Office(Base, TimestampMixin):
    """
    SQLAlchemy model representing an office location for an organization.
    Organizations can have multiple offices with geographic information.
    """
    __tablename__ = 'offices'
    
    id = Column(UUID, primary_key=True, default=generate_uuid)
    organization_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    region = Column(String(100), nullable=True)
    metadata = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    organization = relationship('Organization', back_populates='offices')
    attorneys = relationship('Attorney', secondary='attorney_offices')
    
    def __init__(self, organization_id: uuid.UUID, name: str, city: str, country: str, 
                state: str = None, region: str = None):
        """Initialize a new Office instance"""
        self.organization_id = organization_id
        self.name = name
        self.city = city
        self.country = country
        self.state = state
        self.region = region
        self.metadata = {}
        self.is_active = True
    
    def format_address(self) -> str:
        """Format office location as an address string"""
        address = self.city
        if self.state:
            address += f", {self.state}"
        address += f", {self.country}"
        return address
    
    def activate(self) -> None:
        """Activate the office"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the office"""
        self.is_active = False


class Department(Base, TimestampMixin):
    """
    SQLAlchemy model representing a department within an organization.
    Organizations can have multiple departments for organizational structure.
    """
    __tablename__ = 'departments'
    
    id = Column(UUID, primary_key=True, default=generate_uuid)
    organization_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    metadata = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    organization = relationship('Organization', back_populates='departments')
    
    def __init__(self, organization_id: uuid.UUID, name: str, metadata: Dict = None):
        """Initialize a new Department instance"""
        self.organization_id = organization_id
        self.name = name
        self.metadata = metadata or {}
        self.is_active = True
    
    def activate(self) -> None:
        """Activate the department"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the department"""
        self.is_active = False