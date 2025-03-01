import os  # standard library
import uuid  # standard library
from typing import Union, Optional, Dict, Tuple, List  # standard library
import io  # standard library
import datetime  # standard library
import mimetypes  # standard library
from typing import Any

from src.backend.utils.storage import upload_file, download_file, delete_file, generate_presigned_url, check_file_exists, get_file_metadata, get_file_url, copy_file  # internal
from src.backend.db.models.document import Document, DocumentType  # internal
from src.backend.utils.logging import get_logger  # internal
from src.backend.db.repositories.document_repository import DocumentRepository  # internal
from src.backend.utils.file_handling import create_temp_file, safe_file_name  # internal
from src.backend.utils.encryption import encrypt_data, decrypt_data  # internal

# Initialize logger
logger = get_logger(__name__)

# Define the base path for document storage
DOCUMENT_STORAGE_PATH = os.getenv('DOCUMENT_STORAGE_PATH', 'documents')

# Default expiration time for pre-signed URLs (in seconds)
DEFAULT_PRESIGNED_URL_EXPIRATION = 3600

# List of document types that should be encrypted
ENCRYPTED_DOCUMENT_TYPES = [DocumentType.OCG, DocumentType.CONTRACT]


class DocumentStorageError(Exception):
    """Base exception class for document storage errors"""

    def __init__(self, message: str):
        """Initialize the error with a message"""
        super().__init__(message)


class DocumentNotFoundError(DocumentStorageError):
    """Exception raised when a document is not found"""

    def __init__(self, document_id: Union[str, uuid.UUID]):
        """Initialize the error with a document identifier"""
        message = f"Document with ID '{document_id}' not found"
        super().__init__(message)


class DocumentAccessError(DocumentStorageError):
    """Exception raised when access to a document is denied"""

    def __init__(self, user_id: str, document_id: Union[str, uuid.UUID]):
        """Initialize the error with user and document information"""
        message = f"Access denied for user '{user_id}' to document '{document_id}'"
        super().__init__(message)


class DocumentStorageMetadata:
    """Helper class for managing document metadata"""

    def __init__(self, metadata: Optional[dict] = None):
        """Initialize with optional metadata dictionary"""
        self._metadata = {} if metadata is None else metadata

    def get(self, key: str, default: Any):
        """Get a metadata value by key"""
        return self._metadata.get(key, default)

    def set(self, key: str, value: Any):
        """Set a metadata value"""
        self._metadata[key] = value

    def update(self, data: dict):
        """Update metadata with a dictionary"""
        self._metadata.update(data)

    def to_dict(self) -> dict:
        """Convert metadata to dictionary"""
        return self._metadata.copy()

    def to_json(self) -> str:
        """Convert metadata to JSON string"""
        import json  # third-party library: json
        return json.dumps(self._metadata)


def store_document(
    file_data: Union[bytes, str, io.IOBase],
    filename: str,
    document_type: DocumentType,
    organization_id: str,
    name: str,
    mime_type: Optional[str] = None,
    metadata: Optional[dict] = None,
    encrypt: Optional[bool] = None
) -> Tuple[Document, str]:
    """Stores a document file in the storage backend and creates a Document record in the database"""
    # Determine MIME type from file extension if not provided
    if mime_type is None:
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    # Sanitize filename using safe_file_name utility
    safe_filename = safe_file_name(filename)

    # Generate a unique storage key with organization_id, document_type, and UUID
    storage_key = f"{organization_id}/{document_type.value}/{uuid.uuid4()}/{safe_filename}"

    # Generate full storage path by joining DOCUMENT_STORAGE_PATH and the storage key
    full_storage_path = os.path.join(DOCUMENT_STORAGE_PATH, storage_key)

    # Determine if encryption is needed based on document_type or explicit parameter
    should_encrypt = encrypt if encrypt is not None else document_type in ENCRYPTED_DOCUMENT_TYPES

    # If encryption is needed, encrypt the file data
    if should_encrypt:
        file_data = encrypt_data(file_data)

    # Upload the file to storage backend using upload_file
    upload_file_url = upload_file(file_data, full_storage_path, content_type=mime_type, metadata=metadata)

    # Get file size from uploaded data
    file_size = len(file_data) if isinstance(file_data, bytes) else 0  # needs better implementation

    # Create Document record with repository
    from flask import current_app  # third-party library: flask
    db = current_app.db
    document_repository = DocumentRepository(db.session)

    document = document_repository.create_document(
        organization_id=organization_id,
        document_type=document_type.value,
        file_name=name,
        file_path=full_storage_path,
        content_type=mime_type,
        status='active',
        version=1,
        metadata=metadata
    )

    # Return the created Document instance and storage key
    return document, storage_key


def store_ocg_document(
    file_data: Union[bytes, str, io.IOBase],
    filename: str,
    organization_id: str,
    ocg_id: str,
    ocg_name: str,
    mime_type: Optional[str] = None,
    version: Optional[int] = None,
    metadata: Optional[dict] = None
) -> Tuple[Document, str]:
    """Specialized function for storing OCG documents with appropriate metadata"""
    # Initialize or update metadata dictionary with OCG-specific information
    if metadata is None:
        metadata = {}
    metadata.update({
        'ocg_id': ocg_id,
        'ocg_name': ocg_name,
        'version': version if version is not None else 1
    })

    # Add OCG ID, version, and other relevant metadata
    # Call store_document with document_type=DocumentType.OCG
    document, storage_key = store_document(
        file_data=file_data,
        filename=filename,
        document_type=DocumentType.OCG,
        organization_id=organization_id,
        name=ocg_name,
        mime_type=mime_type,
        metadata=metadata
    )

    # Return the result from store_document
    return document, storage_key


def retrieve_document(
    document_id: Union[str, uuid.UUID],
    download_path: Optional[str] = None,
    decrypt: Optional[bool] = None
) -> Tuple[Document, Union[bytes, str]]:
    """Retrieves a document by its ID"""
    # Get Document record from repository by ID
    from flask import current_app  # third-party library: flask
    db = current_app.db
    document_repository = DocumentRepository(db.session)

    document = document_repository.get_document_by_id(str(document_id))

    # If document not found, raise DocumentNotFoundError
    if document is None:
        raise DocumentNotFoundError(document_id)

    # Determine if decryption is needed based on document_type or explicit parameter
    should_decrypt = decrypt if decrypt is not None else document.document_type in ENCRYPTED_DOCUMENT_TYPES

    # Download the document content using download_file
    file_path = document.file_path
    file_content = download_file(file_path)

    # If decryption is needed, decrypt the content
    if should_decrypt:
        file_content = decrypt_data(file_content)

    # If download_path is provided, write content to that path and return path
    if download_path:
        with open(download_path, 'wb') as f:
            f.write(file_content)
        return document, download_path

    # Otherwise, return the document content as bytes
    return document, file_content


def retrieve_document_by_path(
    file_path: str,
    download_path: Optional[str] = None,
    decrypt: Optional[bool] = None
) -> Tuple[Document, Union[bytes, str]]:
    """Retrieves a document by its storage path"""
    # Get Document record from repository by file_path
    from flask import current_app  # third-party library: flask
    db = current_app.db
    document_repository = DocumentRepository(db.session)
    
    # Get Document record from repository by file_path
    # This method is not implemented in the repository, so we need to query all documents and filter
    all_documents = document_repository._session.query(Document).all()
    document = next((doc for doc in all_documents if doc.file_path == file_path), None)

    # If document not found, raise DocumentNotFoundError
    if document is None:
        raise DocumentNotFoundError(file_path)

    # Use retrieve_document to get the content
    return retrieve_document(document.id, download_path, decrypt)


def get_document_url(
    document: Union[str, uuid.UUID, Document],
    expiration_seconds: Optional[int] = None,
    download: Optional[bool] = False
) -> str:
    """Generates a URL for accessing a document"""
    # If document is a Document instance, use its ID
    document_id = str(document.id) if isinstance(document, Document) else str(document)

    # If document is a string, try to parse as UUID
    try:
        uuid.UUID(document_id)
    except ValueError:
        raise ValueError("Invalid document identifier format")

    # Get Document record from repository
    from flask import current_app  # third-party library: flask
    db = current_app.db
    document_repository = DocumentRepository(db.session)

    document = document_repository.get_document_by_id(document_id)

    # If document not found, raise DocumentNotFoundError
    if document is None:
        raise DocumentNotFoundError(document_id)

    # Set appropriate content disposition based on download parameter
    content_disposition = 'attachment' if download else 'inline'

    # If document's document_type is in ENCRYPTED_DOCUMENT_TYPES, handle authorization separately
    # Generate presigned URL with expiration (default to DEFAULT_PRESIGNED_URL_EXPIRATION)
    expiration = expiration_seconds if expiration_seconds is not None else DEFAULT_PRESIGNED_URL_EXPIRATION
    presigned_url = generate_presigned_url(document.file_path, expiration_seconds=expiration)

    # Return the generated URL
    return presigned_url


def delete_document(
    document: Union[str, uuid.UUID, Document],
    soft_delete: Optional[bool] = False
) -> bool:
    """Deletes a document from storage and database"""
    # If document is a Document instance, use it directly
    document_record = document if isinstance(document, Document) else None

    # Otherwise, get Document record from repository
    if document_record is None:
        from flask import current_app  # third-party library: flask
        db = current_app.db
        document_repository = DocumentRepository(db.session)
        document_record = document_repository.get_document_by_id(str(document))

    # If document not found, raise DocumentNotFoundError
    if document_record is None:
        raise DocumentNotFoundError(str(document))

    # If soft_delete is True, mark document as inactive in database
    if soft_delete:
        from flask import current_app  # third-party library: flask
        db = current_app.db
        document_repository = DocumentRepository(db.session)
        document_repository.update_document(document_record.id, status='inactive')
        return True

    # Otherwise, delete the file from storage using delete_file
    file_path = document_record.file_path
    storage_deletion_successful = delete_file(file_path)

    # If storage deletion successful, delete database record
    if storage_deletion_successful:
        from flask import current_app  # third-party library: flask
        db = current_app.db
        document_repository = DocumentRepository(db.session)
        document_repository.delete_document(document_record.id)
        return True

    # Return success status
    return False


def create_document_version(
    document: Union[str, uuid.UUID, Document],
    file_data: Union[bytes, str, io.IOBase],
    filename: Optional[str] = None,
    mime_type: Optional[str] = None,
    metadata: Optional[dict] = None
) -> Tuple[Document, str]:
    """Creates a new version of an existing document"""
    # If document is not a Document instance, retrieve it from repository
    from flask import current_app  # third-party library: flask
    db = current_app.db
    document_repository = DocumentRepository(db.session)
    document_record = document if isinstance(document, Document) else document_repository.get_document_by_id(str(document))

    # If document not found, raise DocumentNotFoundError
    if document_record is None:
        raise DocumentNotFoundError(str(document))

    # If filename not provided, use original document's name
    filename = filename if filename is not None else document_record.name

    # If mime_type not provided, use original document's mime_type
    mime_type = mime_type if mime_type is not None else document_record.mime_type

    # Generate new storage key for the versioned document
    storage_key = f"{document_record.organization_id}/{document_record.document_type.value}/{uuid.uuid4()}/{safe_filename(filename)}"

    # Generate full storage path by joining DOCUMENT_STORAGE_PATH and the storage key
    full_storage_path = os.path.join(DOCUMENT_STORAGE_PATH, storage_key)

    # Determine if encryption is needed based on document_type
    should_encrypt = document_record.document_type in ENCRYPTED_DOCUMENT_TYPES

    # If encryption is needed, encrypt the file data
    if should_encrypt:
        file_data = encrypt_data(file_data)

    # Upload the file to storage backend using upload_file
    upload_file_url = upload_file(file_data, full_storage_path, content_type=mime_type, metadata=metadata)

    # Get file size from uploaded data
    file_size = len(file_data) if isinstance(file_data, bytes) else 0  # needs better implementation

    # Use document.create_new_version() to create a new version in the database
    new_version = document_record.create_new_version(
        file_path=full_storage_path,
        content=None,  # Assuming content is not directly stored in the model
        binary_content=None,  # Assuming binary_content is not directly stored in the model
        size_bytes=file_size,
        metadata=metadata
    )

    # Mark the original document as inactive
    document_repository._session.add(new_version)
    document_repository._session.commit()
    document_repository.update_document(document_record.id, status='inactive')

    # Return the created Document version and storage key
    return new_version, storage_key


def list_documents(
    organization_id: str,
    document_type: Optional[DocumentType] = None,
    active_only: Optional[bool] = True,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
) -> Tuple[List[Document], int]:
    """Lists documents for an organization with optional filtering"""
    # Prepare filter criteria based on parameters
    from flask import current_app  # third-party library: flask
    db = current_app.db
    document_repository = DocumentRepository(db.session)

    # Query DocumentRepository with filters
    filter_criteria = {
        'organization_id': organization_id,
        'document_type': document_type,
        'active_only': active_only,
        'limit': limit,
        'offset': offset
    }
    
    # Convert DocumentType to string for querying
    document_type_str = document_type.value if document_type else None

    # Query the database with the filter criteria
    documents = document_repository.get_documents_by_organization(
        organization_id=organization_id,
        document_type=document_type_str,
        status='active' if active_only else None
    )
    
    total_count = document_repository.count_documents(
        organization_id=organization_id,
        document_type=document_type_str,
        status='active' if active_only else None
    )

    # Return list of documents and total count
    return documents, total_count


def validate_document_access(
    document: Union[str, uuid.UUID, Document],
    user_id: str,
    user_organizations: List[str]
) -> bool:
    """Validates if a user has access to a document"""
    # If document is not a Document instance, retrieve it from repository
    from flask import current_app  # third-party library: flask
    db = current_app.db
    document_repository = DocumentRepository(db.session)
    document_record = document if isinstance(document, Document) else document_repository.get_document_by_id(str(document))

    # Check if user's organizations include the document's organization_id
    if document_record and document_record.organization_id in user_organizations:
        return True
    else:
        raise DocumentAccessError(user_id, str(document))


def get_document_versions(
    name: str,
    organization_id: str,
    document_type: Optional[DocumentType] = None
) -> List[Document]:
    """Gets all versions of a document by its name and organization"""
    # Query DocumentRepository for documents matching name and organization_id
    from flask import current_app  # third-party library: flask
    db = current_app.db
    document_repository = DocumentRepository(db.session)
    
    # Convert DocumentType to string for querying
    document_type_str = document_type.value if document_type else None

    # Query the database with the filter criteria
    documents = document_repository.get_document_versions(
        organization_id=organization_id,
        document_type=document_type_str,
        metadata_filter={'name': name}
    )

    # Return the list of document versions
    return documents