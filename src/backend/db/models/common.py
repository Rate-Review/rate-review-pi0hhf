"""
Common database model classes, mixins, and utilities used across all database models in the Justice Bid system.
Provides base functionality for audit trails, timestamps, UUID generation, and soft deletion.
"""

import uuid
import datetime
from typing import Dict, Any, Optional, TypeVar

from sqlalchemy import Column, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Create the SQLAlchemy declarative base
Base = declarative_base()

T = TypeVar('T', bound='BaseModel')

def generate_uuid() -> uuid.UUID:
    """
    Generates a random UUID for use as a primary key.
    
    Returns:
        uuid.UUID: A new random UUID
    """
    return uuid.uuid4()


class TimestampMixin:
    """
    Mixin class that adds created_at and updated_at timestamp fields to models.
    """
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)


class AuditMixin:
    """
    Mixin class that adds audit trail capabilities including tracking the user who created or modified the record.
    """
    created_by_id = Column(UUID, ForeignKey('users.id'), nullable=True)
    updated_by_id = Column(UUID, ForeignKey('users.id'), nullable=True)
    
    created_by = relationship('User', foreign_keys=[created_by_id])
    updated_by = relationship('User', foreign_keys=[updated_by_id])


class SoftDeleteMixin:
    """
    Mixin class that adds soft deletion capability to models, allowing records to be marked as deleted 
    without actually removing them from the database.
    """
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by_id = Column(UUID, ForeignKey('users.id'), nullable=True)
    
    deleted_by = relationship('User', foreign_keys=[deleted_by_id])
    
    def delete(self, user_id: Optional[uuid.UUID] = None) -> None:
        """
        Mark the record as deleted with timestamp and user information.
        
        Args:
            user_id: The ID of the user performing the deletion
            
        Returns:
            None
        """
        self.is_deleted = True
        self.deleted_at = datetime.datetime.utcnow()
        if user_id:
            self.deleted_by_id = user_id
    
    def restore(self) -> None:
        """
        Restore a soft-deleted record.
        
        Returns:
            None
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by_id = None


class OrganizationScopedMixin:
    """
    Mixin class that adds organization scoping to models, supporting multi-tenancy and data isolation.
    """
    organization_id = Column(UUID, ForeignKey('organizations.id'), nullable=False)
    organization = relationship('Organization')


class BaseModel(Base):
    """
    Base model class that all other models should inherit from. 
    Includes ID generation and common functionality.
    """
    __abstract__ = True  # This makes it an abstract base class that won't create a table
    
    id = Column(UUID, primary_key=True, default=generate_uuid)
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Convert the model instance to a dictionary for serialization.
        
        Returns:
            dict: Model attributes as a dictionary
        """
        result = {}
        for column in self.__table__.columns:
            result[column.name] = getattr(self, column.name)
        return result
    
    def from_dict(self, data: Dict[str, Any]) -> T:
        """
        Update the model instance from a dictionary.
        
        Args:
            data: Dictionary containing attribute values to set
            
        Returns:
            BaseModel: Self for method chaining
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self