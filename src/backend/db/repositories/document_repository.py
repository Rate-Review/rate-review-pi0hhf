"""
Repository for handling CRUD operations for documents in the Justice Bid system,
including Outside Counsel Guidelines (OCGs) and other rate negotiation related documents.
"""

from typing import List, Optional, Any, Dict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.document import Document, DocumentType
from ...utils.logging import logger


class DocumentRepository:
    """Repository class for handling CRUD operations and queries related to documents"""

    def __init__(self, session: Session):
        """Initialize the document repository with a database session
        
        Args:
            session: SQLAlchemy database session
        """
        self._session = session

    def create_document(
        self,
        organization_id: str,
        document_type: str,
        file_name: str,
        file_path: str,
        content_type: str,
        status: str,
        version: int,
        metadata: Dict[str, Any]
    ) -> Document:
        """Create a new document in the database
        
        Args:
            organization_id: ID of the organization that owns the document
            document_type: Type of document (e.g., OCG, RATE_SHEET)
            file_name: Name of the document file
            file_path: Path to the stored document file
            content_type: MIME type of the document
            status: Current status of the document
            version: Version number of the document
            metadata: Additional metadata for the document
            
        Returns:
            Newly created document
        """
        try:
            # Convert string document_type to enum
            doc_type = getattr(DocumentType, document_type, None)
            if not doc_type:
                logger.error(
                    f"Invalid document type: {document_type}",
                    extra={"additional_data": {"document_type": document_type}}
                )
                raise ValueError(f"Invalid document type: {document_type}")
            
            # Create document
            document = Document(
                organization_id=organization_id,
                document_type=doc_type,
                name=file_name,
                file_path=file_path,
                mime_type=content_type,
                is_active=(status.lower() == 'active'),
                version=version
            )
            
            # Set metadata
            document.set_metadata(metadata)
            
            # Add to session and commit
            self._session.add(document)
            self._session.commit()
            
            logger.info(
                f"Created document {document.id} for organization {organization_id}",
                extra={"additional_data": {"document_id": document.id, "document_type": document_type}}
            )
            
            return document
        except Exception as e:
            self._session.rollback()
            logger.error(
                f"Error creating document: {str(e)}",
                extra={"additional_data": {"organization_id": organization_id, "document_type": document_type}}
            )
            raise

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by its ID
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            The document with the specified ID or None if not found
        """
        try:
            return self._session.query(Document).filter(Document.id == document_id).first()
        except Exception as e:
            logger.error(
                f"Error retrieving document by ID: {str(e)}",
                extra={"additional_data": {"document_id": document_id}}
            )
            raise

    def get_documents_by_organization(
        self,
        organization_id: str,
        document_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Document]:
        """Retrieve all documents belonging to a specific organization
        
        Args:
            organization_id: ID of the organization
            document_type: Optional filter for document type
            status: Optional filter for document status
            
        Returns:
            List of documents matching the criteria
        """
        try:
            query = self._session.query(Document).filter(Document.organization_id == organization_id)
            
            if document_type:
                doc_type = getattr(DocumentType, document_type, None)
                if doc_type:
                    query = query.filter(Document.document_type == doc_type)
                
            if status:
                is_active = (status.lower() == 'active')
                query = query.filter(Document.is_active == is_active)
                
            return query.all()
        except Exception as e:
            logger.error(
                f"Error retrieving documents by organization: {str(e)}",
                extra={"additional_data": {"organization_id": organization_id}}
            )
            raise

    def update_document(
        self,
        document_id: str,
        file_name: Optional[str] = None,
        file_path: Optional[str] = None,
        content_type: Optional[str] = None,
        status: Optional[str] = None,
        version: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Document]:
        """Update an existing document
        
        Args:
            document_id: ID of the document to update
            file_name: New name for the document
            file_path: New file path
            content_type: New content type
            status: New status
            version: New version number
            metadata: New metadata
            
        Returns:
            The updated document or None if not found
        """
        try:
            document = self.get_document_by_id(document_id)
            
            if not document:
                logger.warning(
                    f"Document not found for update: {document_id}",
                    extra={"additional_data": {"document_id": document_id}}
                )
                return None
                
            # Update fields if provided
            if file_name is not None:
                document.name = file_name
                
            if file_path is not None:
                document.file_path = file_path
                
            if content_type is not None:
                document.mime_type = content_type
                
            if status is not None:
                document.is_active = (status.lower() == 'active')
                
            if version is not None:
                document.version = version
                
            if metadata is not None:
                document.set_metadata(metadata)
                
            # Commit changes
            self._session.commit()
            
            logger.info(
                f"Updated document {document_id}",
                extra={"additional_data": {"document_id": document_id}}
            )
            
            return document
        except Exception as e:
            self._session.rollback()
            logger.error(
                f"Error updating document: {str(e)}",
                extra={"additional_data": {"document_id": document_id}}
            )
            raise

    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the database
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if the document was deleted, False if not found
        """
        try:
            document = self.get_document_by_id(document_id)
            
            if not document:
                logger.warning(
                    f"Document not found for deletion: {document_id}",
                    extra={"additional_data": {"document_id": document_id}}
                )
                return False
                
            # Delete the document
            self._session.delete(document)
            self._session.commit()
            
            logger.info(
                f"Deleted document {document_id}",
                extra={"additional_data": {"document_id": document_id}}
            )
            
            return True
        except Exception as e:
            self._session.rollback()
            logger.error(
                f"Error deleting document: {str(e)}",
                extra={"additional_data": {"document_id": document_id}}
            )
            raise

    def get_latest_document_version(
        self,
        organization_id: str,
        document_type: str,
        metadata_filter: Dict[str, Any]
    ) -> Optional[Document]:
        """Get the latest version of a document based on document type and metadata
        
        Args:
            organization_id: ID of the organization
            document_type: Type of document
            metadata_filter: Dictionary of metadata key-value pairs to filter by
            
        Returns:
            The latest version of the document or None if not found
        """
        try:
            # Convert string document_type to enum
            doc_type = getattr(DocumentType, document_type, None)
            if not doc_type:
                logger.error(
                    f"Invalid document type: {document_type}",
                    extra={"additional_data": {"document_type": document_type}}
                )
                raise ValueError(f"Invalid document type: {document_type}")
            
            # Start with basic query
            query = self._session.query(Document).filter(
                Document.organization_id == organization_id,
                Document.document_type == doc_type
            )
            
            # For PostgreSQL, we could use JSONB operators for metadata filtering
            # This implementation uses application-level filtering for compatibility
            documents = query.all()
            filtered_documents = []
            
            for doc in documents:
                metadata = doc.get_metadata()
                matches = True
                
                for key, value in metadata_filter.items():
                    if key not in metadata or metadata[key] != value:
                        matches = False
                        break
                        
                if matches:
                    filtered_documents.append(doc)
            
            # Sort by version and return the latest
            if filtered_documents:
                filtered_documents.sort(key=lambda x: x.version, reverse=True)
                return filtered_documents[0]
                
            return None
        except Exception as e:
            logger.error(
                f"Error getting latest document version: {str(e)}",
                extra={"additional_data": {"organization_id": organization_id, "document_type": document_type}}
            )
            raise

    def get_document_versions(
        self,
        organization_id: str,
        document_type: str,
        metadata_filter: Dict[str, Any]
    ) -> List[Document]:
        """Get all versions of a document based on document type and metadata
        
        Args:
            organization_id: ID of the organization
            document_type: Type of document
            metadata_filter: Dictionary of metadata key-value pairs to filter by
            
        Returns:
            List of all versions of the document
        """
        try:
            # Convert string document_type to enum
            doc_type = getattr(DocumentType, document_type, None)
            if not doc_type:
                logger.error(
                    f"Invalid document type: {document_type}",
                    extra={"additional_data": {"document_type": document_type}}
                )
                raise ValueError(f"Invalid document type: {document_type}")
            
            # Start with basic query
            query = self._session.query(Document).filter(
                Document.organization_id == organization_id,
                Document.document_type == doc_type
            )
            
            # For PostgreSQL, we could use JSONB operators for metadata filtering
            # This implementation uses application-level filtering for compatibility
            documents = query.all()
            filtered_documents = []
            
            for doc in documents:
                metadata = doc.get_metadata()
                matches = True
                
                for key, value in metadata_filter.items():
                    if key not in metadata or metadata[key] != value:
                        matches = False
                        break
                        
                if matches:
                    filtered_documents.append(doc)
            
            # Sort by version and return
            filtered_documents.sort(key=lambda x: x.version, reverse=True)
            return filtered_documents
        except Exception as e:
            logger.error(
                f"Error getting document versions: {str(e)}",
                extra={"additional_data": {"organization_id": organization_id, "document_type": document_type}}
            )
            raise

    def get_documents_by_type(
        self,
        document_type: str,
        status: Optional[str] = None
    ) -> List[Document]:
        """Retrieve all documents of a specific type
        
        Args:
            document_type: Type of document to retrieve
            status: Optional filter for document status
            
        Returns:
            List of documents of the specified type
        """
        try:
            # Convert string document_type to enum
            doc_type = getattr(DocumentType, document_type, None)
            if not doc_type:
                logger.error(
                    f"Invalid document type: {document_type}",
                    extra={"additional_data": {"document_type": document_type}}
                )
                raise ValueError(f"Invalid document type: {document_type}")
            
            query = self._session.query(Document).filter(Document.document_type == doc_type)
            
            if status:
                is_active = (status.lower() == 'active')
                query = query.filter(Document.is_active == is_active)
                
            return query.all()
        except Exception as e:
            logger.error(
                f"Error getting documents by type: {str(e)}",
                extra={"additional_data": {"document_type": document_type}}
            )
            raise

    def count_documents(
        self,
        organization_id: Optional[str] = None,
        document_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """Count documents based on filters
        
        Args:
            organization_id: Optional filter for organization
            document_type: Optional filter for document type
            status: Optional filter for document status
            
        Returns:
            Count of documents matching the criteria
        """
        try:
            query = self._session.query(Document)
            
            if organization_id:
                query = query.filter(Document.organization_id == organization_id)
                
            if document_type:
                doc_type = getattr(DocumentType, document_type, None)
                if doc_type:
                    query = query.filter(Document.document_type == doc_type)
                
            if status:
                is_active = (status.lower() == 'active')
                query = query.filter(Document.is_active == is_active)
                
            return query.count()
        except Exception as e:
            logger.error(
                f"Error counting documents: {str(e)}",
                extra={"additional_data": {"organization_id": organization_id, "document_type": document_type}}
            )
            raise