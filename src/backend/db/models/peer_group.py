"""
SQLAlchemy ORM model defining peer groups, which allow organizations to create collections of
similar organizations (law firms or clients) for benchmarking and comparative analysis purposes.
"""

import uuid
import datetime
from typing import Any, Optional

from sqlalchemy import Column, String, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID

from ..base import Base
from .common import BaseModel, TimestampMixin, AuditMixin, SoftDeleteMixin


# Association table for the many-to-many relationship between peer groups and member organizations
peer_group_members = Table(
    'peer_group_members',
    Base.metadata,
    Column('id', UUID, primary_key=True, default=uuid.uuid4),
    Column('peer_group_id', UUID, ForeignKey('peer_groups.id'), nullable=False),
    Column('organization_id', UUID, ForeignKey('organizations.id'), nullable=False),
    Column('created_at', DateTime, default=datetime.datetime.utcnow, nullable=False),
    Column('updated_at', DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
)


class PeerGroup(BaseModel, TimestampMixin, AuditMixin, SoftDeleteMixin):
    """
    SQLAlchemy model representing a peer group, which is a collection of similar organizations
    (law firms or clients) used for comparison and benchmarking purposes during analytics and
    rate negotiations.
    """
    __tablename__ = 'peer_groups'
    
    # The organization that owns/created this peer group
    organization_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    
    # Peer group name and criteria
    name = Column(String(255), nullable=False)
    
    # Criteria stored as JSON to allow for flexible filtering options
    criteria = Column(JSONB, nullable=True)
    
    # Whether this peer group is active
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    # The organization that owns this peer group
    organization = relationship('Organization', foreign_keys=[organization_id], back_populates='peer_groups')
    
    # Organizations that are members of this peer group
    member_organizations = relationship(
        'Organization',
        secondary=peer_group_members,
        back_populates='member_of_peer_groups'
    )
    
    def __init__(self, organization_id: uuid.UUID, name: str, criteria: Optional[dict] = None):
        """
        Initialize a new PeerGroup instance.
        
        Args:
            organization_id: The UUID of the organization that owns this peer group
            name: The name of the peer group
            criteria: Optional criteria for automatic peer group membership
        """
        super().__init__()
        self.organization_id = organization_id
        self.name = name
        self.criteria = criteria or {}
        self.is_active = True
    
    def add_member(self, organization_id: uuid.UUID) -> bool:
        """
        Add an organization to this peer group.
        
        Args:
            organization_id: The UUID of the organization to add as a member
            
        Returns:
            bool: True if organization was added, False if it was already a member
        """
        from .organization import Organization
        
        organization = Organization.query.get(organization_id)
        if organization:
            if organization not in self.member_organizations:
                self.member_organizations.append(organization)
                return True
        return False
    
    def remove_member(self, organization_id: uuid.UUID) -> bool:
        """
        Remove an organization from this peer group.
        
        Args:
            organization_id: The UUID of the organization to remove
            
        Returns:
            bool: True if organization was removed, False if it wasn't a member
        """
        from .organization import Organization
        
        organization = Organization.query.get(organization_id)
        if organization:
            if organization in self.member_organizations:
                self.member_organizations.remove(organization)
                return True
        return False
    
    def is_member(self, organization_id: uuid.UUID) -> bool:
        """
        Check if an organization is a member of this peer group.
        
        Args:
            organization_id: The UUID of the organization to check
            
        Returns:
            bool: True if the organization is a member, False otherwise
        """
        from .organization import Organization
        
        organization = Organization.query.get(organization_id)
        return organization in self.member_organizations if organization else False
    
    def get_criteria_value(self, key: str, default: Any = None) -> Any:
        """
        Get a specific criteria value by key.
        
        Args:
            key: The criteria key to retrieve
            default: The default value to return if the key is not found
            
        Returns:
            Any: The value for the specified key or the default if not found
        """
        if self.criteria:
            return self.criteria.get(key, default)
        return default
    
    def set_criteria_value(self, key: str, value: Any) -> None:
        """
        Set a specific criteria value by key.
        
        Args:
            key: The criteria key to set
            value: The value to set for the specified key
        """
        if self.criteria is None:
            self.criteria = {}
        self.criteria[key] = value
    
    def activate(self) -> None:
        """
        Activate the peer group.
        """
        self.is_active = True
    
    def deactivate(self) -> None:
        """
        Deactivate the peer group.
        """
        self.is_active = False