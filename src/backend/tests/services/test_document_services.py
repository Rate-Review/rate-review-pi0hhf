# src/backend/tests/services/test_document_services.py
"""Test module for document services in the Justice Bid Rate Negotiation System.
Contains comprehensive unit tests for document storage, retrieval, PDF generation, OCG document handling, and document versioning functionality.
Ensures that document services properly handle various document types, maintain correct metadata, perform proper error handling, and integrate correctly with storage backends.
"""
import io  # IO handling for document content testing
import os  # Operating system interfaces for file path manipulation
import unittest.mock  # Mocking functionality for unit tests
import uuid  # UUID generation for test document IDs
from datetime import datetime  # Date and time handling for document timestamps

import pytest  # Python testing framework
from unittest.mock import patch

from src.backend.db.models.document import Document, DocumentType  # Document data model for tests
from src.backend.db.models.ocg import OCG, OCGSection, OCGAlternative, OCGStatus  # OCG data models for tests
from src.backend.services.documents.ocg_generation import OCGGenerator, get_ocg_template, create_ocg_from_template, generate_ocg_document, OCGFormatException, OCGTemplateException, OCGNotFoundError  # OCG generation service functions to be tested
from src.backend.services.documents.pdf_generator import generate_pdf, generate_pdf_from_html, generate_pdf_from_template, generate_pdf_from_markdown, generate_ocg_pdf, store_pdf, PDFGenerator, ReportLabPDFGenerator, HTMLPDFGenerator  # PDF generation service functions to be tested
from src.backend.services.documents.storage import store_document, retrieve_document, get_document_url, delete_document, create_document_version, list_documents, DocumentStorageError, DocumentNotFoundError, DocumentAccessError  # Document storage service functions to be tested
from src.backend.services.documents.ocg_negotiation import OCGNegotiationService, PointBudgetExceededError  # OCG negotiation service class to be tested
from src.backend.tests.conftest import db_session, client, app, client_organization, law_firm_organization  # Test fixtures for database sessions and test client

@pytest.mark.parametrize('document_type, encrypt', [
    pytest.param(DocumentType.OCG, True),
    pytest.param(DocumentType.RATE_SHEET, False)
])
def test_store_document(db_session, document_type, encrypt):
    """Test storing a document in the storage backend"""
    file_data = io.BytesIO(b"Test file content")
    filename = "test_document.txt"
    organization_id = str(uuid.uuid4())
    name = "Test Document"
    metadata = {"key1": "value1", "key2": "value2"}

    with patch('src.backend.services.documents.storage.upload_file') as mock_upload_file:
        mock_upload_file.return_value = "s3://test_bucket/test_document.txt"

        document, storage_key = store_document(
            file_data=file_data,
            filename=filename,
            document_type=document_type,
            organization_id=organization_id,
            name=name,
            metadata=metadata,
            encrypt=encrypt
        )

        assert document.organization_id == organization_id
        assert document.document_type == document_type
        assert document.file_name == name
        assert document.content_type == "text/plain"
        assert document.status == "active"
        assert document.version == 1
        assert document.get_metadata() == metadata

        mock_upload_file.assert_called_once()
        args, kwargs = mock_upload_file.call_args
        assert args[0] == file_data
        assert kwargs['content_type'] == "text/plain"
        assert kwargs['metadata'] == metadata

        if encrypt:
            assert b"Test file content" not in args[0].getvalue()
        else:
            assert b"Test file content" in args[0].getvalue()