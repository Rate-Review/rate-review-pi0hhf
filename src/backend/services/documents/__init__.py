"""
Initialization file for the documents service package that exposes document-related functionality including storage, PDF generation, OCG generation, and OCG negotiation.
"""

from .storage import (
    store_document,
    retrieve_document,
    delete_document,
    get_document_url,
    store_ocg_document,
    store_rate_sheet,
    DocumentStorageManager,  # Provides document storage functionality
)
from .pdf_generator import (
    generate_ocg_pdf,
    generate_rate_sheet_pdf,
    generate_negotiation_summary_pdf,
    generate_analytics_pdf,
    store_generated_pdf,
    PDFGenerator,  # Provides PDF generation functionality
)
from .ocg_generation import (
    generate_ocg_document,
    generate_ocg_pdf_document,
    generate_ocg_html_document,
    compare_ocg_versions,
    OCGDocumentGenerator,  # Provides OCG document generation functionality
)
from .ocg_negotiation import (
    OCGNegotiationService,
    publish_ocg_for_negotiation,
    start_ocg_negotiation,
    generate_negotiation_document,  # Provides OCG negotiation functionality
)

__all__ = [
    "store_document",  # Stores a document in the system
    "retrieve_document",  # Retrieves a document from the system
    "delete_document",  # Deletes a document from the system
    "get_document_url",  # Gets a URL for accessing a document
    "store_ocg_document",  # Stores an OCG document
    "store_rate_sheet",  # Stores a rate sheet document
    "DocumentStorageManager",  # Context manager for document storage operations
    "generate_ocg_pdf",  # Generates a PDF from an OCG
    "generate_rate_sheet_pdf",  # Generates a PDF for rate submissions
    "generate_negotiation_summary_pdf",  # Generates a PDF summary of a negotiation
    "generate_analytics_pdf",  # Generates a PDF with analytics data
    "store_generated_pdf",  # Stores a generated PDF
    "PDFGenerator",  # Base class for PDF generation
    "generate_ocg_document",  # Generates an OCG document in various formats
    "generate_ocg_pdf_document",  # Generates an OCG document in PDF format
    "generate_ocg_html_document",  # Generates an OCG document in HTML format
    "compare_ocg_versions",  # Compares different versions of an OCG
    "OCGDocumentGenerator",  # Base class for OCG document generation
    "OCGNegotiationService",  # Service for managing OCG negotiations
    "publish_ocg_for_negotiation",  # Publishes an OCG for negotiation
    "start_ocg_negotiation",  # Starts the OCG negotiation process
    "generate_negotiation_document",  # Generates a document for OCG negotiation
]