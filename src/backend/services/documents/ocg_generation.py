"""
Service module responsible for generating Outside Counsel Guidelines (OCG) documents in the Justice Bid Rate Negotiation System.
This service provides functionality to create, structure, and format OCG documents with sections, subsections, negotiable alternatives, and point values.
It supports generation of OCG templates, conversion of OCG data models to formatted documents, and integration with document storage and PDF generation.
"""
import os  # standard library
import uuid  # standard library
import datetime  # standard library
import typing  # standard library
import json  # standard library
import io  # standard library

from typing import Union, Optional, Dict, List, Tuple, Any  # standard library

from src.backend.db.models.ocg import OCG, OCGSection, OCGAlternative, OCGStatus  # internal
from src.backend.db.repositories.ocg_repository import OCGRepository  # internal
from src.backend.services.documents.pdf_generator import generate_ocg_pdf, generate_pdf_from_template  # internal
from src.backend.services.documents.storage import store_ocg_document, store_document  # internal
from src.backend.utils.logging import get_logger  # internal
from src.backend.db.session import get_db  # internal
from src.backend.db.models.document import DocumentType  # internal
from src.backend.utils.formatting import format_document  # internal
from src.backend.utils.validators import validate_ocg_structure  # internal

# Initialize logger
logger = get_logger(__name__)

# Define template directory
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../templates')

# Define OCG template directory
OCG_TEMPLATE_DIR = os.path.join(TEMPLATES_DIR, 'ocg')

# Define industry-specific templates
INDUSTRY_TEMPLATES = {
    'legal': 'legal_standard.json',
    'financial': 'financial_standard.json',
    'healthcare': 'healthcare_standard.json',
    'technology': 'technology_standard.json',
    'generic': 'generic_standard.json'
}


def get_ocg_template(template_type: str, custom_template_path: Optional[str] = None) -> dict:
    """
    Loads an OCG template from the template directory.

    Args:
        template_type (str): Type of template to load (legal, financial, healthcare, technology, generic, or custom)
        custom_template_path (Optional[str]): Path to a custom template file (required if template_type is 'custom')

    Returns:
        dict: Template structure with sections and default content
    """
    # Validate template_type is one of the supported industry templates or 'custom'
    if template_type not in INDUSTRY_TEMPLATES and template_type != 'custom':
        raise ValueError(f"Invalid template type: {template_type}. Must be one of: {', '.join(INDUSTRY_TEMPLATES.keys())} or 'custom'")

    # If template_type is 'custom', use custom_template_path
    if template_type == 'custom':
        if not custom_template_path:
            raise ValueError("custom_template_path is required when template_type is 'custom'")
        template_file_path = custom_template_path
    else:
        # Otherwise, get the template file path from INDUSTRY_TEMPLATES
        template_file_path = os.path.join(OCG_TEMPLATE_DIR, INDUSTRY_TEMPLATES[template_type])

    # Open and read the template file
    try:
        with open(template_file_path, 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found: {template_file_path}")
    except Exception as e:
        raise Exception(f"Error reading template file: {template_file_path}. {str(e)}")

    # Parse JSON content into a dictionary
    try:
        template_structure = json.loads(template_content)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Error parsing JSON in template file: {template_file_path}. {str(e)}", e.doc, e.pos)

    # Return the template structure
    return template_structure


def create_ocg_from_template(client_id: str, name: str, template_type: str, total_points: Optional[int] = None,
                             default_firm_point_budget: Optional[int] = None, custom_template_path: Optional[str] = None) -> OCG:
    """
    Creates a new OCG based on a template.

    Args:
        client_id (str): ID of the client organization
        name (str): Name of the OCG
        template_type (str): Type of template to use (legal, financial, healthcare, technology, generic, or custom)
        total_points (Optional[int]): Total points available for negotiation
        default_firm_point_budget (Optional[int]): Default point budget for law firms
        custom_template_path (Optional[str]): Path to a custom template file (required if template_type is 'custom')

    Returns:
        OCG: Newly created OCG populated with template content
    """
    # Get template structure using get_ocg_template
    template = get_ocg_template(template_type, custom_template_path)

    # Create database session
    db = get_db()

    # Create OCG repository instance
    repository = OCGRepository(db)

    # Create new OCG using repository.create
    ocg = repository.create(
        client_id=uuid.UUID(client_id),
        name=name,
        total_points=total_points,
        default_firm_point_budget=default_firm_point_budget
    )

    # Process template sections and add them to the OCG
    generator = OCGGenerator(repository)
    generator._process_template_sections(ocg, template)

    # Commit the changes to the database
    db.commit()

    # Return the created OCG
    return ocg


def generate_ocg_document(ocg_id: str, format_type: str, firm_id: Optional[str] = None, options: Optional[dict] = None) -> bytes:
    """
    Generates a formatted document from an OCG.

    Args:
        ocg_id (str): ID of the OCG to generate the document from
        format_type (str): Format of the document to generate (pdf, html, docx, json)
        firm_id (Optional[str]): ID of the law firm to include selections for
        options (Optional[dict]): Additional options for document generation

    Returns:
        bytes: Document content in the requested format
    """
    # Create database session
    db = get_db()

    # Create OCG repository instance
    repository = OCGRepository(db)

    # Get OCG by ID from repository
    ocg = repository.get_by_id(uuid.UUID(ocg_id))

    # If OCG not found, raise OCGNotFoundError
    if not ocg:
        raise OCGNotFoundError(ocg_id)

    # If format_type is 'pdf', use generate_ocg_pdf to create PDF
    if format_type == 'pdf':
        document_content = generate_ocg_pdf(ocg, options=options)
    elif format_type == 'html':
        document_content = format_document(ocg, format_type)
    elif format_type == 'docx':
        document_content = format_document(ocg, format_type)
    elif format_type == 'json':
        document_content = json.dumps(ocg.to_dict())
    else:
        raise ValueError(f"Unsupported format type: {format_type}")

    # If firm_id is provided, include firm selections in the document
    if firm_id:
        firm_selections = repository.get_selections_by_firm(ocg.id, uuid.UUID(firm_id))
    else:
        firm_selections = None

    # Store generated document using store_ocg_document
    store_ocg_document(
        file_data=document_content,
        filename=f"{ocg.name}.{format_type}",
        organization_id=str(ocg.client_id),
        ocg_id=str(ocg.id),
        ocg_name=ocg.name,
        mime_type=f"application/{format_type}" if format_type != 'html' else "text/html",
        version=ocg.version,
        metadata={'firm_id': firm_id} if firm_id else {}
    )

    # Return the document content
    return document_content


def save_ocg_template(ocg_id: str, template_name: str, description: Optional[str] = None, metadata: Optional[dict] = None) -> str:
    """
    Saves an OCG as a reusable template.

    Args:
        ocg_id (str): ID of the OCG to save as a template
        template_name (str): Name of the template file
        description (Optional[str]): Description of the template
        metadata (Optional[dict]): Additional metadata for the template

    Returns:
        str: Template file path
    """
    # Create database session
    db = get_db()

    # Create OCG repository instance
    repository = OCGRepository(db)

    # Get OCG by ID from repository
    ocg = repository.get_by_id(uuid.UUID(ocg_id))

    # If OCG not found, raise OCGNotFoundError
    if not ocg:
        raise OCGNotFoundError(ocg_id)

    # Convert OCG to template format (simplify and remove specific identifiers)
    template_data = {
        'name': ocg.name,
        'description': description,
        'sections': []
    }
    for section in ocg.sections:
        section_data = {
            'title': section.title,
            'content': section.content,
            'is_negotiable': section.is_negotiable,
            'alternatives': []
        }
        for alternative in section.alternatives:
            alternative_data = {
                'title': alternative.title,
                'content': alternative.content,
                'points': alternative.points
            }
            section_data['alternatives'].append(alternative_data)
        template_data['sections'].append(section_data)

    # Add metadata including description, creation date, and source OCG
    if metadata is None:
        metadata = {}
    metadata.update({
        'description': description,
        'creation_date': datetime.datetime.now().isoformat(),
        'source_ocg_id': str(ocg.id),
        'source_ocg_name': ocg.name
    })

    # Ensure template_name has .json extension
    if not template_name.lower().endswith('.json'):
        template_name += '.json'

    # Save template to custom templates directory
    template_file_path = os.path.join(OCG_TEMPLATE_DIR, template_name)
    with open(template_file_path, 'w') as f:
        json.dump(template_data, f, indent=4)

    # Return the path to the saved template file
    return template_file_path


def export_ocg_with_selections(ocg_id: str, firm_id: str, format_type: str, options: Optional[dict] = None) -> bytes:
    """
    Exports an OCG with firm selections as a document.

    Args:
        ocg_id (str): ID of the OCG to export
        firm_id (str): ID of the law firm to include selections for
        format_type (str): Format of the document to generate (pdf, html, docx, json)
        options (Optional[dict]): Additional options for document generation

    Returns:
        bytes: Document content with firm selections
    """
    # Create database session
    db = get_db()

    # Create OCG repository instance
    repository = OCGRepository(db)

    # Get OCG by ID from repository
    ocg = repository.get_by_id(uuid.UUID(ocg_id))

    # Get firm selections from repository
    firm_selections = repository.get_selections_by_firm(ocg.id, uuid.UUID(firm_id))

    # Generate document with selections using generate_ocg_document
    document_content = generate_ocg_document(ocg_id, format_type, firm_id, options)

    # Return the document content
    return document_content


def validate_ocg(ocg_id: str) -> Tuple[bool, List]:
    """
    Validates the structure and content of an OCG document.

    Args:
        ocg_id (str): ID of the OCG to validate

    Returns:
        tuple: (bool, list) - Validation result and list of issues
    """
    # Create database session
    db = get_db()

    # Create OCG repository instance
    repository = OCGRepository(db)

    # Get OCG by ID from repository
    ocg = repository.get_by_id(uuid.UUID(ocg_id))

    # If OCG not found, raise OCGNotFoundError
    if not ocg:
        raise OCGNotFoundError(ocg_id)

    # Validate OCG has required metadata (name, client_id, etc.)
    # Validate OCG has at least one section
    # Validate negotiable sections have at least one alternative
    # Validate alternatives have appropriate point values
    is_valid, issues = validate_ocg_structure(ocg)

    # Return tuple of validation result and list of any issues found
    return is_valid, issues


class OCGGenerator:
    """
    Class responsible for generating and managing OCG documents.
    """

    def __init__(self, repository: Optional[OCGRepository] = None):
        """
        Initialize the OCG Generator with a repository.

        Args:
            repository (Optional[OCGRepository]): OCG repository instance. If not provided, a new repository will be created.
        """
        # If repository is provided, store it as _repository
        if repository:
            self._repository = repository
        else:
            # Otherwise, create a new repository with get_db()
            self._repository = OCGRepository(get_db())

        # Initialize empty templates cache dictionary
        self._templates_cache: Dict = {}

        # Log initialization of OCGGenerator
        logger.info("OCGGenerator initialized")

    def create_ocg(self, client_id: str, name: str, total_points: Optional[int] = None,
                   default_firm_point_budget: Optional[int] = None) -> OCG:
        """
        Creates a new OCG document.

        Args:
            client_id (str): ID of the client organization
            name (str): Name of the OCG
            total_points (Optional[int]): Total points available for negotiation
            default_firm_point_budget (Optional[int]): Default point budget for law firms

        Returns:
            OCG: Newly created OCG
        """
        # Validate input parameters
        if not client_id:
            raise ValueError("client_id is required")
        if not name:
            raise ValueError("name is required")

        # Create new OCG using repository
        ocg = self._repository.create(
            client_id=uuid.UUID(client_id),
            name=name,
            total_points=total_points,
            default_firm_point_budget=default_firm_point_budget
        )

        # Log creation of new OCG
        logger.info(f"Created new OCG: {ocg.name} (ID: {ocg.id})")

        # Return the created OCG
        return ocg

    def create_from_template(self, client_id: str, name: str, template_type: str, total_points: Optional[int] = None,
                             default_firm_point_budget: Optional[int] = None, custom_template_path: Optional[str] = None) -> OCG:
        """
        Creates a new OCG from a template.

        Args:
            client_id (str): ID of the client organization
            name (str): Name of the OCG
            template_type (str): Type of template to use (legal, financial, healthcare, technology, generic, or custom)
            total_points (Optional[int]): Total points available for negotiation
            default_firm_point_budget (Optional[int]): Default point budget for law firms
            custom_template_path (Optional[str]): Path to a custom template file (required if template_type is 'custom')

        Returns:
            OCG: OCG created from template
        """
        # Get template using get_ocg_template or from cache
        template = self.load_template(template_type, custom_template_path)

        # Create new OCG using repository
        ocg = self._repository.create(
            client_id=uuid.UUID(client_id),
            name=name,
            total_points=total_points,
            default_firm_point_budget=default_firm_point_budget
        )

        # Process template sections and add them to the OCG
        self._process_template_sections(ocg, template)

        # Log creation of OCG from template
        logger.info(f"Created OCG from template: {ocg.name} (ID: {ocg.id})")

        # Return the created OCG
        return ocg

    def add_section(self, ocg_id: str, title: str, content: str, is_negotiable: bool, parent_id: Optional[str] = None) -> OCGSection:
        """
        Adds a section to an OCG.

        Args:
            ocg_id (str): ID of the OCG to add the section to
            title (str): Title of the section
            content (str): Content of the section
            is_negotiable (bool): Whether the section is negotiable
            parent_id (Optional[str]): ID of the parent section (if this is a subsection)

        Returns:
            OCGSection: Newly created section
        """
        # Validate OCG exists and is in draft status
        ocg = self._repository.get_by_id(uuid.UUID(ocg_id))
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        if ocg.status != OCGStatus.DRAFT:
            raise ValueError("Cannot add section to OCG that is not in draft status")

        # Create new section using repository
        section = self._repository.add_section(
            ocg_id=uuid.UUID(ocg_id),
            title=title,
            content=content,
            is_negotiable=is_negotiable,
            parent_id=uuid.UUID(parent_id) if parent_id else None
        )

        # Log creation of new section
        logger.info(f"Added section '{title}' to OCG {ocg_id}")

        # Return the created section
        return section

    def add_alternative(self, section_id: str, title: str, content: str, points: int, is_default: Optional[bool] = None) -> OCGAlternative:
        """
        Adds an alternative to a negotiable section.

        Args:
            section_id (str): ID of the section to add the alternative to
            title (str): Title of the alternative
            content (str): Content of the alternative
            points (int): Point value of the alternative
            is_default (Optional[bool]): Whether this alternative is the default

        Returns:
            OCGAlternative: Newly created alternative
        """
        # Validate section exists and is negotiable
        section = self._repository.get_section(uuid.UUID(section_id))
        if not section:
            raise ValueError(f"Section with ID {section_id} not found")
        if not section.is_negotiable:
            raise ValueError(f"Section with ID {section_id} is not negotiable")

        # Create new alternative using repository
        alternative = self._repository.add_alternative(
            section_id=uuid.UUID(section_id),
            title=title,
            content=content,
            points=points,
            is_default=is_default
        )

        # Log creation of new alternative
        logger.info(f"Added alternative '{title}' to section {section_id}")

        # Return the created alternative
        return alternative

    def generate_document(self, ocg_id: str, format_type: str, firm_id: Optional[str] = None, options: Optional[dict] = None) -> bytes:
        """
        Generates a document from an OCG.

        Args:
            ocg_id (str): ID of the OCG to generate the document from
            format_type (str): Format of the document to generate (pdf, html, docx, json)
            firm_id (Optional[str]): ID of the law firm to include selections for
            options (Optional[dict]): Additional options for document generation

        Returns:
            bytes: Generated document content
        """
        # Validate OCG exists
        ocg = self._repository.get_by_id(uuid.UUID(ocg_id))
        if not ocg:
            raise OCGNotFoundError(ocg_id)

        # Prepare OCG data structure for document generation
        # If format_type is 'pdf', use PDF generator
        # If format_type is 'html', use HTML formatter
        # If format_type is 'docx', use DOCX formatter
        # If format_type is 'json', use JSON serializer
        # If firm_id provided, include firm selections
        # Store the generated document
        # Return document content
        return generate_ocg_document(ocg_id, format_type, firm_id, options)

    def publish_ocg(self, ocg_id: str) -> OCG:
        """
        Publishes an OCG, making it available for negotiation.

        Args:
            ocg_id (str): ID of the OCG to publish

        Returns:
            OCG: Updated OCG with published status
        """
        # Validate OCG exists and is in draft status
        ocg = self._repository.get_by_id(uuid.UUID(ocg_id))
        if not ocg:
            raise OCGNotFoundError(ocg_id)
        if ocg.status != OCGStatus.DRAFT:
            raise ValueError("Cannot publish OCG that is not in draft status")

        # Validate OCG structure using validate_ocg
        is_valid, issues = validate_ocg_structure(ocg)
        if not is_valid:
            raise ValueError(f"OCG is not valid: {issues}")

        # Update OCG status to PUBLISHED
        ocg = self._repository.update_ocg_status(uuid.UUID(ocg_id), OCGStatus.PUBLISHED)

        # Generate and store final OCG document
        self.generate_document(ocg_id, 'pdf')

        # Log publication of OCG
        logger.info(f"Published OCG: {ocg.name} (ID: {ocg.id})")

        # Return the updated OCG
        return ocg

    def create_new_version(self, ocg_id: str) -> OCG:
        """
        Creates a new version of an OCG.

        Args:
            ocg_id (str): ID of the OCG to create a new version of

        Returns:
            OCG: New OCG version
        """
        # Validate OCG exists
        ocg = self._repository.get_by_id(uuid.UUID(ocg_id))
        if not ocg:
            raise OCGNotFoundError(ocg_id)

        # Create new version using repository
        new_ocg = self._repository.create_new_version(uuid.UUID(ocg_id))

        # Log creation of new OCG version
        logger.info(f"Created new version of OCG: {new_ocg.name} (ID: {new_ocg.id}, Version: {new_ocg.version})")

        # Return the new OCG version
        return new_ocg

    def save_as_template(self, ocg_id: str, template_name: str, description: Optional[str] = None, metadata: Optional[dict] = None) -> str:
        """
        Saves an OCG as a reusable template.

        Args:
            ocg_id (str): ID of the OCG to save as a template
            template_name (str): Name of the template file
            description (Optional[str]): Description of the template
            metadata (Optional[dict]): Additional metadata for the template

        Returns:
            str: Template file path
        """
        # Validate OCG exists
        ocg = self._repository.get_by_id(uuid.UUID(ocg_id))
        if not ocg:
            raise OCGNotFoundError(ocg_id)

        # Convert OCG to template format
        # Add metadata to template
        # Save template to file
        template_file_path = save_ocg_template(ocg_id, template_name, description, metadata)

        # Log saving of template
        logger.info(f"Saved OCG {ocg.name} (ID: {ocg.id}) as template: {template_file_path}")

        # Return template file path
        return template_file_path

    def load_template(self, template_type: str, custom_template_path: Optional[str] = None, force_reload: Optional[bool] = False) -> dict:
        """
        Loads an OCG template from file or cache.

        Args:
            template_type (str): Type of template to load (legal, financial, healthcare, technology, generic, or custom)
            custom_template_path (Optional[str]): Path to a custom template file (required if template_type is 'custom')
            force_reload (Optional[bool]): Whether to force reload the template from file

        Returns:
            dict: Template data structure
        """
        # If template in cache and not force_reload, return cached template
        if template_type in self._templates_cache and not force_reload:
            logger.debug(f"Loaded template '{template_type}' from cache")
            return self._templates_cache[template_type]

        # Otherwise, load template using get_ocg_template
        template = get_ocg_template(template_type, custom_template_path)

        # Cache the loaded template
        self._templates_cache[template_type] = template
        logger.debug(f"Loaded template '{template_type}' from file and cached")

        # Return the template data
        return template

    def get_ocg(self, ocg_id: str) -> Optional[OCG]:
        """
        Retrieves an OCG by ID.

        Args:
            ocg_id (str): ID of the OCG to retrieve

        Returns:
            Optional[OCG]: OCG if found, None otherwise
        """
        # Get OCG from repository by ID
        ocg = self._repository.get_by_id(uuid.UUID(ocg_id))

        # Return the OCG or None if not found
        return ocg

    def _process_template_sections(self, ocg: OCG, template: dict):
        """
        Processes template sections and adds them to an OCG.

        Args:
            ocg (OCG): OCG to add sections to
            template (dict): Template data structure
        """
        # Extract sections from template
        sections = template.get('sections', [])

        # For each section in template:
        for section_data in sections:
            # Create section in OCG
            title = section_data.get('title')
            content = section_data.get('content')
            is_negotiable = section_data.get('is_negotiable', False)
            section = self._repository.add_section(
                ocg_id=ocg.id,
                title=title,
                content=content,
                is_negotiable=is_negotiable
            )

            # If section is negotiable, process alternatives
            if is_negotiable:
                alternatives = section_data.get('alternatives', [])
                for alt_data in alternatives:
                    self._repository.add_alternative(
                        section_id=section.id,
                        title=alt_data.get('title'),
                        content=alt_data.get('content'),
                        points=alt_data.get('points')
                    )

            # If section has subsections, process them recursively
            subsections = section_data.get('subsections', [])
            for subsection_data in subsections:
                self.add_section(
                    ocg_id=str(ocg.id),
                    title=subsection_data.get('title'),
                    content=subsection_data.get('content'),
                    is_negotiable=subsection_data.get('is_negotiable', False),
                    parent_id=str(section.id)
                )


class OCGFormatException(Exception):
    """
    Exception raised for OCG formatting errors.
    """

    def __init__(self, message: str):
        """
        Initialize the exception with a message.

        Args:
            message (str): Error message
        """
        super().__init__(message)


class OCGTemplateException(Exception):
    """
    Exception raised for OCG template errors.
    """

    def __init__(self, message: str):
        """
        Initialize the exception with a message.

        Args:
            message (str): Error message
        """
        super().__init__(message)


class OCGNotFoundError(Exception):
    """
    Exception raised when an OCG is not found.
    """

    def __init__(self, ocg_id: str):
        """
        Initialize the exception with an OCG ID.

        Args:
            ocg_id (str): ID of the OCG that was not found
        """
        message = f"OCG with ID '{ocg_id}' not found"
        super().__init__(message)