"""
Document model for storing and managing documents in the system.

This module defines the Document model which represents various types
of documents in the Justice Bid system, including Outside Counsel Guidelines (OCGs),
rate sheets, contracts, and other document types used in rate negotiations.
"""

import enum
import json
import uuid
from datetime import datetime, timedelta

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text, Enum, LargeBinary, DateTime
from sqlalchemy.orm import relationship

from ..base import Base


# Define document types as an enumeration
DocumentType = enum.Enum('DocumentType', ['OCG', 'RATE_SHEET', 'CONTRACT', 'INVOICE', 'OTHER'])


class Document(Base):
    """SQLAlchemy model representing a document in the system.
    
    This model is used to store various types of documents such as Outside Counsel Guidelines (OCGs),
    rate sheets, contracts, or other document types used in rate negotiations.
    """
    __tablename__ = 'documents'

    # Primary key and document identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    
    # File storage information
    file_path = Column(String(512))
    mime_type = Column(String(128))
    size_bytes = Column(Integer)
    
    # Document content - either as text or binary
    content = Column(Text)
    binary_content = Column(LargeBinary)
    
    # Metadata stored as JSON string
    metadata_json = Column(String(4096))
    
    # Ownership and relations
    organization_id = Column(String(36), ForeignKey('organizations.id'))
    organization = relationship("Organization")
    
    # Versioning and status
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converts the document model to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the document
        """
        result = {
            'id': self.id,
            'name': self.name,
            'document_type': self.document_type.value if self.document_type else None,
            'file_path': self.file_path,
            'mime_type': self.mime_type,
            'size_bytes': self.size_bytes,
            'organization_id': self.organization_id,
            'version': self.version,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include metadata if it exists
        metadata = self.get_metadata()
        if metadata:
            result['metadata'] = metadata
            
        return result
    
    def get_metadata(self):
        """Retrieves the document metadata as a Python dictionary.
        
        Returns:
            dict: Metadata as a dictionary
        """
        if not self.metadata_json:
            return {}
        try:
            return json.loads(self.metadata_json)
        except json.JSONDecodeError:
            return {}
    
    def set_metadata(self, metadata):
        """Sets the document metadata from a Python dictionary.
        
        Args:
            metadata (dict): Metadata to store
        """
        if metadata:
            self.metadata_json = json.dumps(metadata)
        else:
            self.metadata_json = None
    
    def get_file_url(self, temporary=False):
        """Generates a URL for accessing the document file.
        
        Args:
            temporary (bool): Whether to generate a temporary URL with time limitations
            
        Returns:
            str: URL to access the document file
        """
        if not self.file_path:
            return None
            
        # This is a placeholder implementation
        # In a real implementation, this would generate URLs using a storage service like S3
        base_url = "/api/v1/documents/{document_id}/download"
        url = base_url.format(document_id=self.id)
        
        if temporary:
            # Add query parameters for temporary access
            expiry = int((datetime.utcnow() + timedelta(hours=1)).timestamp())
            url = f"{url}?expires={expiry}"
            
        return url
    
    def create_new_version(self, file_path=None, content=None, binary_content=None, size_bytes=None, metadata=None):
        """Creates a new version of the document with updated content.
        
        Args:
            file_path (str, optional): New file path
            content (str, optional): New text content
            binary_content (bytes, optional): New binary content
            size_bytes (int, optional): New file size
            metadata (dict, optional): New metadata
            
        Returns:
            Document: New version of the document
        """
        # Create a new document instance
        new_version = Document()
        
        # Copy essential properties
        new_version.id = self.id
        new_version.name = self.name
        new_version.document_type = self.document_type
        new_version.organization_id = self.organization_id
        
        # Set version number
        new_version.version = self.version + 1
        
        # Update with new values if provided
        if file_path:
            new_version.file_path = file_path
        else:
            new_version.file_path = self.file_path
            
        if content is not None:
            new_version.content = content
        else:
            new_version.content = self.content
            
        if binary_content is not None:
            new_version.binary_content = binary_content
        else:
            new_version.binary_content = self.binary_content
            
        if size_bytes is not None:
            new_version.size_bytes = size_bytes
        else:
            new_version.size_bytes = self.size_bytes
            
        if metadata is not None:
            new_version.set_metadata(metadata)
        else:
            new_version.metadata_json = self.metadata_json
        
        # Set status and timestamps
        new_version.is_active = True
        self.is_active = False  # Mark current version as inactive
        
        new_version.created_at = datetime.utcnow()
        new_version.updated_at = datetime.utcnow()
        
        return new_version