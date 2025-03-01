"""
API endpoints for document management in the Justice Bid system, particularly focused on Outside Counsel Guidelines (OCG) document handling, file uploads/downloads, and document metadata management.
"""
import io  # latest
import uuid  # latest
from datetime import datetime  # latest
from typing import List, Optional  # latest

import magic  # package_version: 0.4.27
from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile, File, Form  # package_version: 0.95.0
from pydantic import BaseModel  # package_version: 1.10.7

from src.backend.api.core.auth import get_current_user, require_auth  # internal
from src.backend.services.auth.permissions import check_permission  # internal
from src.backend.services.documents import storage as storage_service  # internal
from src.backend.services.documents import pdf_generator  # internal
from src.backend.services.documents import ocg_generation  # internal
from src.backend.utils.logging import logger  # internal
from src.backend.utils.pagination import PaginationParams  # internal
from src.backend.utils.validators import validate_file_type  # internal

router = APIRouter(prefix='/documents', tags=['documents'])

ALLOWED_EXTENSIONS = ['pdf', 'docx', 'xlsx', 'pptx', 'txt']
ALLOWED_MIME_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                       'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'text/plain']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post('/', status_code=status.HTTP_201_CREATED)
@require_auth
async def create_document(
    file: UploadFile = File(...),
    name: str = Form(...),
    document_type: str = Form(...),
    related_entity_type: str = Form(...),
    related_entity_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Upload a new document to the system with metadata"""
    # Validate current user has permission to create documents
    if not check_permission(current_user, "documents:create"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Check if file is provided, if not raise HTTPException with 400 status
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    # Validate file size does not exceed MAX_FILE_SIZE, if exceeds raise HTTPException with 413 status
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File size exceeds maximum allowed size")

    # Detect MIME type of file using python-magic
    try:
        file_content = await file.read()
        mime_type = magic.from_buffer(file_content, mime=True)
    except Exception as e:
        logger.error(f"Error detecting MIME type: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error detecting MIME type")

    # Validate MIME type is in ALLOWED_MIME_TYPES, if not raise HTTPException with 415 status
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file type")

    # Create document metadata with generated UUID, current timestamp, file information, and provided metadata
    document_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    metadata = {
        "document_id": document_id,
        "timestamp": timestamp,
        "file_name": file.filename,
        "mime_type": mime_type,
        "document_type": document_type,
        "related_entity_type": related_entity_type,
        "related_entity_id": related_entity_id,
        "created_by": current_user['id']
    }

    # Upload document using storage_service.upload_document
    try:
        upload_result = await storage_service.upload_document(file_content, file.filename, metadata)
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error uploading document")

    # Log document creation event
    logger.info(f"Document created: {document_id}")

    # Return document metadata response
    return {"message": "Document created successfully", "metadata": metadata}


@router.get('/{document_id}')
@require_auth
async def get_document(document_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """Get document metadata by ID"""
    # Validate document_id is a valid UUID, if not raise HTTPException with 400 status
    try:
        uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

    # Validate current user has permission to view the document
    if not check_permission(current_user, "documents:read"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Get document metadata using storage_service.get_document_metadata
    try:
        document_metadata = await storage_service.get_document_metadata(document_id)
    except storage_service.DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except Exception as e:
        logger.error(f"Error retrieving document metadata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving document metadata")

    # Check if user has access to the related entity referenced in the document
    # TODO: Implement access control logic based on related_entity_type and related_entity_id

    # Return document metadata
    return document_metadata


@router.get('/{document_id}/download')
@require_auth
async def download_document(document_id: str, current_user: dict = Depends(get_current_user)) -> Response:
    """Download a document by ID"""
    # Validate document_id is a valid UUID, if not raise HTTPException with 400 status
    try:
        uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

    # Validate current user has permission to download the document
    if not check_permission(current_user, "documents:read"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Get document metadata using storage_service.get_document_metadata
    try:
        document_metadata = await storage_service.get_document_metadata(document_id)
    except storage_service.DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except Exception as e:
        logger.error(f"Error retrieving document metadata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving document metadata")

    # Check if user has access to the related entity referenced in the document
    # TODO: Implement access control logic based on related_entity_type and related_entity_id

    # Log document download event
    logger.info(f"Document downloaded: {document_id}")

    # Download document content using storage_service.download_document
    try:
        file_content = await storage_service.download_document(document_id)
    except Exception as e:
        logger.error(f"Error downloading document content: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error downloading document content")

    # Create file-like object using io.BytesIO
    file_like_object = io.BytesIO(file_content)

    # Return document as a streaming response with appropriate content-type header and original filename
    return Response(
        file_like_object.read(),
        media_type=document_metadata['mime_type'],
        headers={"Content-Disposition": f"attachment;filename={document_metadata['file_name']}"}
    )


@router.get('/')
@require_auth
async def list_documents(
    document_type: Optional[str] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """List documents with pagination and filtering"""
    # Validate current user has permission to list documents
    if not check_permission(current_user, "documents:read"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Create filter dictionary from provided parameters
    filters = {
        "document_type": document_type,
        "related_entity_type": related_entity_type,
        "related_entity_id": related_entity_id
    }

    # Add organization filter based on user's organization
    filters["organization_id"] = current_user['organization_id']

    # Get list of documents using storage_service.list_documents with filtering and pagination
    try:
        documents, total_count = await storage_service.list_documents(filters, pagination.page, pagination.page_size)
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listing documents")

    # Return document list response with total count and results
    return {
        "total_count": total_count,
        "results": documents
    }


@router.put('/{document_id}')
@require_auth
async def update_document(
    document_id: str,
    document_data: dict,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Update document metadata"""
    # Validate document_id is a valid UUID, if not raise HTTPException with 400 status
    try:
        uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

    # Validate current user has permission to update the document
    if not check_permission(current_user, "documents:update"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Get document metadata using storage_service.get_document_metadata
    try:
        document_metadata = await storage_service.get_document_metadata(document_id)
    except storage_service.DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except Exception as e:
        logger.error(f"Error retrieving document metadata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving document metadata")

    # Check if user has access to the related entity referenced in the document
    # TODO: Implement access control logic based on related_entity_type and related_entity_id

    # Update document metadata using storage_service.update_document_metadata
    try:
        updated_metadata = await storage_service.update_document_metadata(document_id, document_data)
    except Exception as e:
        logger.error(f"Error updating document metadata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating document metadata")

    # Log document update event
    logger.info(f"Document updated: {document_id}")

    # Return updated document metadata
    return {"message": "Document updated successfully", "metadata": updated_metadata}


@router.delete('/{document_id}', status_code=status.HTTP_204_NO_CONTENT)
@require_auth
async def delete_document(document_id: str, current_user: dict = Depends(get_current_user)) -> None:
    """Delete a document by ID"""
    # Validate document_id is a valid UUID, if not raise HTTPException with 400 status
    try:
        uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

    # Validate current user has permission to delete the document
    if not check_permission(current_user, "documents:delete"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Get document metadata using storage_service.get_document_metadata
    try:
        document_metadata = await storage_service.get_document_metadata(document_id)
    except storage_service.DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except Exception as e:
        logger.error(f"Error retrieving document metadata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving document metadata")

    # Check if user has access to the related entity referenced in the document
    # TODO: Implement access control logic based on related_entity_type and related_entity_id

    # Delete document using storage_service.delete_document
    try:
        await storage_service.delete_document(document_id)
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting document")

    # Log document deletion event
    logger.info(f"Document deleted: {document_id}")

    # Return no content response


@router.post('/ocg/{ocg_id}/generate')
@require_auth
async def generate_ocg_pdf(ocg_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """Generate a PDF for Outside Counsel Guidelines"""
    # Validate ocg_id is a valid UUID, if not raise HTTPException with 400 status
    try:
        uuid.UUID(ocg_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OCG ID format")

    # Validate current user has permission to generate OCG documents
    if not check_permission(current_user, "ocg:generate"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Check if OCG exists, if not raise HTTPException with 404 status
    try:
        ocg_data = await storage_service.get_ocg(ocg_id)  # Assuming a get_ocg function exists in storage_service
    except storage_service.OCGNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OCG not found")
    except Exception as e:
        logger.error(f"Error retrieving OCG data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving OCG data")

    # Generate OCG document using ocg_generation.generate_ocg_document
    try:
        pdf_content = await ocg_generation.generate_ocg_document(ocg_id)
    except Exception as e:
        logger.error(f"Error generating OCG document: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error generating OCG document")

    # Create document metadata with appropriate type and relation to OCG
    document_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    metadata = {
        "document_id": document_id,
        "timestamp": timestamp,
        "file_name": f"{ocg_data['name']}.pdf",
        "mime_type": "application/pdf",
        "document_type": "OCG",
        "related_entity_type": "OCG",
        "related_entity_id": ocg_id,
        "created_by": current_user['id']
    }

    # Upload generated PDF to storage using storage_service.upload_document
    try:
        upload_result = await storage_service.upload_document(pdf_content, f"{ocg_data['name']}.pdf", metadata)
    except Exception as e:
        logger.error(f"Error uploading OCG document: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error uploading OCG document")

    # Log OCG document generation event
    logger.info(f"OCG document generated: {document_id}")

    # Return document metadata response
    return {"message": "OCG document generated successfully", "metadata": metadata}


@router.put('/{document_id}/content')
@require_auth
async def replace_document(
    document_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Replace an existing document with a new file while keeping the same ID and metadata"""
    # Validate document_id is a valid UUID, if not raise HTTPException with 400 status
    try:
        uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

    # Validate current user has permission to update the document
    if not check_permission(current_user, "documents:update"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Get document metadata using storage_service.get_document_metadata
    try:
        document_metadata = await storage_service.get_document_metadata(document_id)
    except storage_service.DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except Exception as e:
        logger.error(f"Error retrieving document metadata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving document metadata")

    # Check if user has access to the related entity referenced in the document
    # TODO: Implement access control logic based on related_entity_type and related_entity_id

    # Check if file is provided, if not raise HTTPException with 400 status
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    # Validate file size does not exceed MAX_FILE_SIZE, if exceeds raise HTTPException with 413 status
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File size exceeds maximum allowed size")

    # Detect MIME type of file using python-magic
    try:
        file_content = await file.read()
        mime_type = magic.from_buffer(file_content, mime=True)
    except Exception as e:
        logger.error(f"Error detecting MIME type: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error detecting MIME type")

    # Validate MIME type is in ALLOWED_MIME_TYPES, if not raise HTTPException with 415 status
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file type")

    # Delete old document file using storage_service.delete_document
    try:
        await storage_service.delete_document(document_id)
    except Exception as e:
        logger.error(f"Error deleting old document: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting old document")

    # Upload new document with same ID using storage_service.upload_document
    try:
        upload_result = await storage_service.upload_document(file_content, file.filename, document_metadata)
    except Exception as e:
        logger.error(f"Error uploading new document: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error uploading new document")

    # Update document metadata with new file information
    document_metadata['file_name'] = file.filename
    document_metadata['mime_type'] = mime_type

    # Log document replacement event
    logger.info(f"Document replaced: {document_id}")

    # Return updated document metadata
    return {"message": "Document replaced successfully", "metadata": document_metadata}


@router.get('/{document_id}/versions')
@require_auth
async def get_document_versions(document_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """Get list of document versions for a given document ID"""
    # Validate document_id is a valid UUID, if not raise HTTPException with 400 status
    try:
        uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

    # Validate current user has permission to view the document
    if not check_permission(current_user, "documents:read"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Get document metadata using storage_service.get_document_metadata
    try:
        document_metadata = await storage_service.get_document_metadata(document_id)
    except storage_service.DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except Exception as e:
        logger.error(f"Error retrieving document metadata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving document metadata")

    # Check if user has access to the related entity referenced in the document
    # TODO: Implement access control logic based on related_entity_type and related_entity_id

    # Get list of document versions using storage_service.list_documents with parent_document_id filter
    try:
        document_versions = await storage_service.list_documents(document_id)  # Assuming list_documents can filter by parent_document_id
    except Exception as e:
        logger.error(f"Error listing document versions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listing document versions")

    # Return document versions list
    return {"total_count": len(document_versions), "results": document_versions}