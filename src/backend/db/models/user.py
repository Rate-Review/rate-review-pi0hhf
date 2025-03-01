"""
SQLAlchemy ORM model for user entities in the Justice Bid Rate Negotiation System.
Defines the database schema for users with authentication, authorization, and organization relationships.
Supports role-based access control, MFA, and permission management.
"""

import datetime
import uuid
from typing import Any, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from ..base import Base
from .common import BaseModel, TimestampMixin, AuditMixin, SoftDeleteMixin, OrganizationScopedMixin, generate_uuid
from ...utils.constants import UserRole
from ...utils.security import hash_password, verify_password


class User(Base, TimestampMixin, SoftDeleteMixin):
    """
    SQLAlchemy model representing a user in the Justice Bid Rate Negotiation System.
    Users belong to organizations and have roles that determine their permissions.
    """
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True, default=generate_uuid)
    organization_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STANDARD_USER)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    permissions = Column(JSONB, nullable=True)  # Stores custom permissions
    preferences = Column(JSONB, nullable=True)  # Stores user preferences

    # Relationships
    organization = relationship('Organization', back_populates='users')
    deleted_by = relationship('User', foreign_keys=[deleted_by_id])

    def __init__(self, email: str, name: str, password: str, organization_id: uuid.UUID, 
                 role: UserRole = UserRole.STANDARD_USER):
        """
        Initialize a new User instance.
        
        Args:
            email: User's email address
            name: User's full name
            password: Plain text password (will be hashed)
            organization_id: ID of the organization this user belongs to
            role: User's role within the system
        """
        self.email = email
        self.name = name
        self.password_hash = hash_password(password)
        self.organization_id = organization_id
        self.role = role
        self.is_active = True
        self.password_changed_at = datetime.datetime.utcnow()
        self.permissions = {}
        self.preferences = {}

    def set_password(self, password: str) -> None:
        """
        Set user password with proper hashing.
        
        Args:
            password: Plain text password to set
        """
        self.password_hash = hash_password(password)
        self.password_changed_at = datetime.datetime.utcnow()

    def verify_password(self, password: str) -> bool:
        """
        Verify a password against stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        return verify_password(password, self.password_hash)
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            permission: Permission name to check
            
        Returns:
            True if user has permission, False otherwise
        """
        if self.permissions is None:
            return False
        return permission in self.permissions
    
    def add_permission(self, permission: str) -> bool:
        """
        Add a permission to the user.
        
        Args:
            permission: Permission name to add
            
        Returns:
            True if permission was added, False if already exists
        """
        if self.permissions is None:
            self.permissions = {}
        
        if permission in self.permissions:
            return False
        
        self.permissions[permission] = True
        return True
    
    def remove_permission(self, permission: str) -> bool:
        """
        Remove a permission from the user.
        
        Args:
            permission: Permission name to remove
            
        Returns:
            True if permission was removed, False if not found
        """
        if self.permissions is None or permission not in self.permissions:
            return False
        
        del self.permissions[permission]
        return True
    
    def update_last_login(self) -> None:
        """
        Update the last login timestamp to current time.
        """
        self.last_login = datetime.datetime.utcnow()
    
    def enable_mfa(self, mfa_secret: str) -> None:
        """
        Enable multi-factor authentication for user.
        
        Args:
            mfa_secret: Secret key for MFA
        """
        self.mfa_enabled = True
        self.mfa_secret = mfa_secret
    
    def disable_mfa(self) -> None:
        """
        Disable multi-factor authentication for user.
        """
        self.mfa_enabled = False
        self.mfa_secret = None
    
    def activate(self) -> None:
        """
        Activate the user account.
        """
        self.is_active = True
    
    def deactivate(self) -> None:
        """
        Deactivate the user account.
        """
        self.is_active = False
    
    def delete(self, deleted_by_id: Optional[uuid.UUID] = None) -> None:
        """
        Soft delete the user.
        
        Args:
            deleted_by_id: ID of the user performing the deletion
        
        Returns:
            None: Updates is_deleted and related fields
        """
        self.is_deleted = True
        self.deleted_at = datetime.datetime.utcnow()
        if deleted_by_id:
            self.deleted_by_id = deleted_by_id
    
    def restore(self) -> None:
        """
        Restore a soft-deleted user.
        
        Returns:
            None: Updates is_deleted and related fields
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by_id = None
    
    def is_administrator(self) -> bool:
        """
        Check if user has an administrator role.
        
        Returns:
            bool: True if user is an administrator, False otherwise
        """
        return self.role in [UserRole.SYSTEM_ADMINISTRATOR, UserRole.ORGANIZATION_ADMINISTRATOR]
    
    def set_preference(self, key: str, value: Any) -> None:
        """
        Set a user preference value.
        
        Args:
            key: Preference key
            value: Preference value
        """
        if self.preferences is None:
            self.preferences = {}
        
        self.preferences[key] = value
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference value.
        
        Args:
            key: Preference key
            default: Default value if preference not found
            
        Returns:
            Any: Preference value or default
        """
        if self.preferences is None or key not in self.preferences:
            return default
        
        return self.preferences[key]