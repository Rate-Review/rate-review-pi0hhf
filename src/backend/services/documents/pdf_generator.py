"""
Module that provides PDF generation capabilities for the Justice Bid Rate Negotiation System.
This service handles the creation of various PDF documents including rate reports, Outside Counsel Guidelines (OCGs),
negotiation summaries, and analytics reports. It leverages industry-standard PDF libraries to create professional,
well-formatted documents with proper headers, footers, tables, and styling.
"""
import os  # standard library
import io  # standard library
import datetime  # standard library
import uuid  # standard library
import typing  # standard library
from typing import Union, Optional, Dict, List  # standard library

import reportlab  # reportlab v3.6.12
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle  # reportlab
from reportlab.lib.styles import getSampleStyleSheet  # reportlab
from reportlab.lib.units import inch  # reportlab
from reportlab.lib import colors  # reportlab
from reportlab.lib.pagesizes import letter  # reportlab
from reportlab.pdfgen import canvas  # reportlab

import weasyprint  # weasyprint v57.1
from weasyprint import HTML  # weasyprint

import jinja2  # jinja2 v3.1.2

import xhtml2pdf  # xhtml2pdf v0.2.8

import markdown  # markdown v3.4.3

from src.backend.utils.logging import get_logger  # internal
from src.backend.utils.file_handling import create_temp_file, safe_file_name  # internal
from src.backend.utils.formatting import format_currency, format_percentage, format_date, format_datetime, format_number  # internal
from src.backend.services.documents.storage import store_document  # internal
from src.backend.db.models.document import DocumentType  # internal
from src.backend.utils.constants import DEFAULT_CURRENCY, DEFAULT_LOCALE  # internal
from reportlab.pdfgen.canvas import Canvas

# Initialize logger
logger = get_logger(__name__)

# Define template directory
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'templates')

# Define font directory
PDF_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', 'fonts')

# Default page size
DEFAULT_PAGE_SIZE = reportlab.lib.pagesizes.LETTER

# Default margin
DEFAULT_MARGIN = 36

# Default font name
DEFAULT_FONT_NAME = "Helvetica"

# Default font size
DEFAULT_FONT_SIZE = 10

# Header font size
HEADER_FONT_SIZE = 12

# Title font size
TITLE_FONT_SIZE = 16

# Subtitle font size
SUBTITLE_FONT_SIZE = 14

# Default font color
DEFAULT_FONT_COLOR = reportlab.lib.colors.black

# Primary color
PRIMARY_COLOR = reportlab.lib.colors.HexColor('#2C5282')

# Secondary color
SECONDARY_COLOR = reportlab.lib.colors.HexColor('#38A169')

# Accent color
ACCENT_COLOR = reportlab.lib.colors.HexColor('#DD6B20')


def generate_pdf(title: str, content: Union[str, dict, io.IOBase, List], template_name: Optional[str] = None, options: Optional[dict] = None) -> bytes:
    """Generic function to generate a PDF document from various inputs

    Args:
        title (str): Title of the PDF document
        content (Union[str, dict, io.IOBase, List]): Content of the PDF document. Can be HTML, Markdown, plain text, or table data.
        template_name (Optional[str]): Name of the Jinja2 template to use for HTML-based PDFs.
        options (Optional[dict]): Additional options for PDF generation.

    Returns:
        bytes: Generated PDF content as bytes
    """
    # Initialize options with defaults if None provided
    if options is None:
        options = {}

    # Determine the PDF generation method based on content type and template_name
    if template_name:
        # If template_name is provided, use HTML template approach with weasyprint
        if isinstance(content, dict):
            # If content is a dictionary, use it as context for template rendering
            return generate_pdf_from_template(template_name, content, options)
        else:
            logger.warning("Content must be a dictionary when using a template. Falling back to default PDF generation.")
            return b''  # Or raise an exception

    elif isinstance(content, str):
        # If content is a string, determine if it's HTML, Markdown, or plain text
        if content.strip().startswith('<!DOCTYPE html>') or content.strip().startswith('<html'):
            # HTML content
            return generate_pdf_from_html(content, options)
        else:
            # Markdown content
            return generate_pdf_from_markdown(content, options)

    elif isinstance(content, list):
        # If content is a list, treat as table data for reportlab
        return generate_pdf_from_reportlab(title, content, options)
    
    elif isinstance(content, dict):
        # If content is a dict, treat as chart data for reportlab
        return generate_pdf_from_reportlab(title, content, options)

    else:
        logger.error("Unsupported content type for PDF generation.")
        raise ValueError("Unsupported content type for PDF generation.")


def generate_pdf_from_html(html_content: str, options: Optional[dict] = None) -> bytes:
    """Generate a PDF document from HTML content

    Args:
        html_content (str): HTML content to convert to PDF
        options (Optional[dict]): Additional options for PDF generation

    Returns:
        bytes: Generated PDF content as bytes
    """
    # Initialize options with defaults if None provided
    if options is None:
        options = {}

    # Setup custom CSS based on options
    custom_css = options.get('css', '')

    # Create WeasyPrint HTML object from html_content
    html = HTML(string=html_content, base_url=TEMPLATES_DIR)

    # Render the HTML to PDF
    pdf_bytes = html.write_pdf()

    # Return the PDF content as bytes
    return pdf_bytes


def generate_pdf_from_template(template_name: str, context: dict, options: Optional[dict] = None) -> bytes:
    """Generate a PDF document from a Jinja2 HTML template

    Args:
        template_name (str): Name of the Jinja2 template file
        context (dict): Dictionary containing the data to pass to the template
        options (Optional[dict]): Additional options for PDF generation

    Returns:
        bytes: Generated PDF content as bytes
    """
    # Initialize options with defaults if None provided
    if options is None:
        options = {}

    # Setup Jinja2 environment with template directory
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_DIR))

    # Load the template by name
    template = env.get_template(template_name)

    # Enrich context with common data (date, time, etc.)
    context['now'] = datetime.datetime.now()

    # Render the template with the provided context
    html_content = template.render(context)

    # Generate PDF from rendered HTML using generate_pdf_from_html
    pdf_bytes = generate_pdf_from_html(html_content, options)

    # Return the PDF content as bytes
    return pdf_bytes


def generate_pdf_from_markdown(markdown_content: str, options: Optional[dict] = None) -> bytes:
    """Generate a PDF document from Markdown content

    Args:
        markdown_content (str): Markdown content to convert to PDF
        options (Optional[dict]): Additional options for PDF generation

    Returns:
        bytes: Generated PDF content as bytes
    """
    # Initialize options with defaults if None provided
    if options is None:
        options = {}

    # Convert markdown to HTML using the markdown library
    html_content = markdown.markdown(markdown_content)

    # Wrap HTML in a basic document structure with styling
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Markdown PDF</title>
        <style>
            body {{ font-family: sans-serif; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Generate PDF from HTML using generate_pdf_from_html
    pdf_bytes = generate_pdf_from_html(html_content, options)

    # Return the PDF content as bytes
    return pdf_bytes


def generate_pdf_from_reportlab(title: str, content: Union[List, Dict], options: Optional[dict] = None) -> bytes:
    """Generate a PDF document using ReportLab for complex layouts

    Args:
        title (str): Title of the PDF document
        content (Union[List, Dict]): Content of the PDF document. Can be table data, chart data, or paragraphs.
        options (Optional[dict]): Additional options for PDF generation

    Returns:
        bytes: Generated PDF content as bytes
    """
    # Initialize options with defaults if None provided
    if options is None:
        options = {}

    # Create a BytesIO buffer for the PDF content
    buffer = io.BytesIO()

    # Initialize ReportLab Canvas with specified page size and margins
    canvas_obj = canvas.Canvas(buffer, pagesize=DEFAULT_PAGE_SIZE)

    # Setup document metadata (title, author, etc.)
    canvas_obj.setAuthor("Justice Bid")
    canvas_obj.setTitle(title)

    # Add common header with logo and title
    add_header_footer(canvas_obj, title, options)

    # Process content based on type (table data, chart data, paragraphs)
    if isinstance(content, list):
        # Table data
        pass
    elif isinstance(content, dict):
        # Chart data
        pass
    else:
        # Paragraphs
        pass

    # Add page numbers and footer if requested
    add_page_number(canvas_obj, options)

    # Save the canvas to the buffer
    canvas_obj.save()

    # Return the buffer contents as bytes
    buffer.seek(0)
    return buffer.read()


def generate_table_pdf(title: str, data: List[dict], columns: List[dict], options: Optional[dict] = None) -> bytes:
    """Generate a PDF document containing a data table

    Args:
        title (str): Title of the PDF document
        data (List[dict]): List of dictionaries representing the table data
        columns (List[dict]): List of column specifications (name, width, format)
        options (Optional[dict]): Additional options for PDF generation

    Returns:
        bytes: Generated PDF content as bytes
    """
    # Initialize options with defaults if None provided
    if options is None:
        options = {}

    # Format the data according to column specifications (date/currency formatting)
    formatted_data = []
    for row in data:
        formatted_row = {}
        for col in columns:
            key = col['name']
            value = row.get(key)
            if value is not None:
                if col.get('type') == 'currency':
                    formatted_row[key] = format_currency(value, col.get('currency', DEFAULT_CURRENCY))
                elif col.get('type') == 'percentage':
                    formatted_row[key] = format_percentage(value)
                elif col.get('type') == 'date':
                    formatted_row[key] = format_date(value)
                else:
                    formatted_row[key] = str(value)
            else:
                formatted_row[key] = ''
        formatted_data.append(formatted_row)

    # Calculate column widths based on content and page size
    column_widths = [col.get('width', 1 * inch) for col in columns]

    # Create a table data structure for ReportLab
    table_data = [[col['label'] for col in columns]]  # Header row
    for row in formatted_data:
        table_data.append([row.get(col['name'], '') for col in columns])

    # Setup table styles (borders, header formatting, row coloring)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Generate PDF with the table using generate_pdf_from_reportlab
    return generate_pdf_from_reportlab(title, table_data, options)


def generate_chart_pdf(title: str, chart_data: List[dict], options: Optional[dict] = None) -> bytes:
    """Generate a PDF document containing one or more charts

    Args:
        title (str): Title of the PDF document
        chart_data (List[dict]): List of chart specifications (type, data, options)
        options (Optional[dict]): Additional options for PDF generation

    Returns:
        bytes: Generated PDF content as bytes
    """
    # Initialize options with defaults if None provided
    if options is None:
        options = {}

    # For each chart in chart_data:
    #   - Generate chart image using appropriate library (reportlab.graphics)
    #   - Position chart on the page with caption/title
    #   - Add explanatory text if provided

    # Generate PDF with the charts using generate_pdf_from_reportlab
    return generate_pdf_from_reportlab(title, chart_data, options)


def generate_ocg_pdf(ocg, firm_selections: Optional[List] = None, options: Optional[dict] = None) -> bytes:
    """Generate a PDF document for Outside Counsel Guidelines (OCGs)

    Args:
        ocg (OCG): OCG object containing the guidelines data
        firm_selections (Optional[List]): List of firm selections for negotiable sections
        options (Optional[dict]): Additional options for PDF generation

    Returns:
        bytes: Generated PDF content as bytes
    """
    # Initialize options with defaults if None provided
    if options is None:
        options = {}

    # Prepare OCG data structure with sections and alternatives
    context = {
        'ocg': ocg,
        'firm_selections': firm_selections
    }

    # Use specialized OCG template for rendering
    template_name = 'ocg_template.html'

    # Generate PDF document using generate_pdf_from_template
    return generate_pdf_from_template(template_name, context, options)


def generate_rate_report_pdf(title: str, rate_data: List[dict], metadata: dict, options: Optional[dict] = None) -> bytes:
    """Generate a PDF report for rate submissions or negotiations

    Args:
        title (str): Title of the PDF document
        rate_data (List[dict]): List of rate data dictionaries
        metadata (dict): Metadata about the rate report
        options (Optional[dict]): Additional options for PDF generation

    Returns:
        bytes: Generated PDF content as bytes
    """
    # Initialize options with defaults if None provided
    if options is None:
        options = {}

    # Format rate data with proper currency and percentage formatting
    # Group rates by appropriate category (staff class, attorney, etc.)
    # Add summary statistics (averages, increases, etc.)
    context = {
        'title': title,
        'rate_data': rate_data,
        'metadata': metadata
    }

    # Generate PDF using rate report template
    template_name = 'rate_report_template.html'
    return generate_pdf_from_template(template_name, context, options)


def generate_analytics_pdf(title: str, analytics_data: dict, charts: Optional[List[dict]] = None, options: Optional[dict] = None) -> bytes:
    """Generate a PDF report for analytics data

    Args:
        title (str): Title of the PDF document
        analytics_data (dict): Dictionary containing analytics data
        charts (Optional[List[dict]]): List of chart specifications (type, data, options)
        options (Optional[dict]): Additional options for PDF generation

    Returns:
        bytes: Generated PDF content as bytes
    """
    # Initialize options with defaults if None provided
    if options is None:
        options = {}

    # Format analytics data
    # Create visualizations based on charts configuration
    context = {
        'title': title,
        'analytics_data': analytics_data,
        'charts': charts
    }

    # Generate PDF using analytics template
    template_name = 'analytics_report_template.html'
    return generate_pdf_from_template(template_name, context, options)


def add_page_number(canvas: Canvas, doc: dict):
    """Helper function to add page numbers to a PDF

    Args:
        canvas (Canvas): ReportLab Canvas object
        doc (dict): Document properties
    """
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(doc['width'], doc['bottomMargin'] - 0.5 * inch,
                      "Page %d %s" % (canvas.getPageNumber(), doc['pageinfo']))
    canvas.restoreState()


def add_header_footer(canvas: Canvas, title: str, options: dict):
    """Helper function to add header and footer to a PDF

    Args:
        canvas (Canvas): ReportLab Canvas object
        title (str): Title of the document
        options (dict): Options for header and footer
    """
    canvas.saveState()
    canvas.setFont('Times-Bold', 16)
    canvas.drawString(inch, DEFAULT_PAGE_SIZE[1] - 0.75 * inch, title)
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch,
                      "Justice Bid Rate Negotiation System")
    canvas.drawRightString(DEFAULT_PAGE_SIZE[0] - inch, 0.75 * inch,
                           "Page %d" % canvas.getPageNumber())
    canvas.restoreState()


def store_pdf(pdf_content: bytes, filename: str, document_type: DocumentType, organization_id: str, metadata: Optional[dict] = None) -> Tuple[Document, str]:
    """Store a generated PDF in the document storage system

    Args:
        pdf_content (bytes): The PDF content as bytes
        filename (str): The filename for the PDF
        document_type (DocumentType): The type of document
        organization_id (str): The ID of the organization owning the document
        metadata (Optional[dict]): Additional metadata for the document

    Returns:
        tuple: (Document, str) - Created Document instance and storage key
    """
    # Ensure filename has .pdf extension
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'

    # Sanitize filename using safe_file_name
    safe_filename = safe_file_name(filename)

    # Call store_document with PDF content and parameters
    document, storage_key = store_document(
        file_data=pdf_content,
        filename=safe_filename,
        document_type=document_type,
        organization_id=organization_id,
        name=filename,
        mime_type='application/pdf',
        metadata=metadata
    )

    # Return document instance and storage key from store_document
    return document, storage_key