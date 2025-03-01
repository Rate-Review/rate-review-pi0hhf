"""
Utility module providing functions for handling file operations including reading, writing, validating, and processing files
of various formats (Excel, CSV, PDF) for the Justice Bid Rate Negotiation System.
"""

import os
import io
import tempfile
import csv
import mimetypes
import shutil
from typing import List, Dict, Union, Optional, Any, BinaryIO, Tuple

import openpyxl  # version 3.1.0
import pandas as pd  # version 2.0.0
import PyPDF2  # version 3.0.0

from ..utils.logging import get_logger
from ..utils.validators import validate_file_extension, validate_file_size
from ..utils.constants import SUPPORTED_FILE_FORMATS, MAX_FILE_SIZE_MB

# Set up logger
logger = get_logger(__name__)

# Global constants
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB in bytes

def get_file_extension(filename: str) -> str:
    """
    Extracts the file extension from a filename.
    
    Args:
        filename (str): The filename to extract the extension from
        
    Returns:
        str: Lowercase file extension without dot
    """
    # Convert to string in case it's a Path object
    filename = str(filename)
    
    try:
        # Split the filename and extension
        _, extension = os.path.splitext(filename)
        
        # Return the extension (excluding the dot) and convert to lowercase
        return extension[1:].lower() if extension else ""
    except Exception as e:
        logger.error(f"Error extracting file extension from {filename}: {str(e)}")
        return ""

def is_allowed_file(filename: str, allowed_extensions: set = None) -> bool:
    """
    Checks if a file has an allowed extension.
    
    Args:
        filename (str): The filename to check
        allowed_extensions (set): Set of allowed extensions
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    
    extension = get_file_extension(filename)
    return extension in allowed_extensions

def validate_file_size(file_object: BinaryIO, max_size: int = None) -> bool:
    """
    Validates if a file's size is within the allowed limit.
    
    Args:
        file_object (file): File object to check
        max_size (int): Maximum allowed size in bytes
        
    Returns:
        bool: True if file size is valid, False otherwise
    """
    if max_size is None:
        max_size = MAX_FILE_SIZE
        
    try:
        # Get current position to restore it later
        current_position = file_object.tell()
        
        # Seek to the end to get the file size
        file_object.seek(0, os.SEEK_END)
        file_size = file_object.tell()
        
        # Restore original position
        file_object.seek(current_position)
        
        # Check if file size is within limits
        return file_size <= max_size
    except Exception as e:
        logger.error(f"Error validating file size: {str(e)}")
        return False

def get_mime_type(filename: str) -> str:
    """
    Determines the MIME type of a file.
    
    Args:
        filename (str): The filename to check
        
    Returns:
        str: MIME type of the file
    """
    mime_type, _ = mimetypes.guess_type(filename)
    
    # If mime_type couldn't be determined, default to application/octet-stream
    if mime_type is None:
        return "application/octet-stream"
    
    return mime_type

def read_csv_file(file_path: str, options: Dict = None) -> List[Dict]:
    """
    Reads data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        options (dict): Dictionary of CSV reader options
        
    Returns:
        list: List of dictionaries representing rows in the CSV
    """
    if options is None:
        options = {}
    
    # Default options
    delimiter = options.get("delimiter", ",")
    encoding = options.get("encoding", "utf-8")
    
    try:
        rows = []
        with open(file_path, 'r', encoding=encoding) as csv_file:
            # Create CSV reader
            csv_reader = csv.reader(csv_file, delimiter=delimiter)
            
            # Read the header row
            header = next(csv_reader)
            
            # Process each row
            for row in csv_reader:
                # Convert row to dictionary using header as keys
                row_dict = {header[i]: value for i, value in enumerate(row) if i < len(header)}
                rows.append(row_dict)
        
        logger.info(f"Successfully read {len(rows)} rows from CSV file: {file_path}")
        return rows
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {str(e)}")
        raise ValueError(f"Failed to read CSV file: {str(e)}")

def write_csv_file(file_path: str, data: List[Dict], fieldnames: List[str] = None, options: Dict = None) -> str:
    """
    Writes data to a CSV file.
    
    Args:
        file_path (str): Path to save the CSV file
        data (list): List of dictionaries to write
        fieldnames (list): List of field names for the CSV header
        options (dict): Dictionary of CSV writer options
        
    Returns:
        str: Path to the created CSV file
    """
    if options is None:
        options = {}
    
    # Default options
    delimiter = options.get("delimiter", ",")
    encoding = options.get("encoding", "utf-8")
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # If fieldnames not provided, use keys from first data item
        if fieldnames is None and data:
            fieldnames = list(data[0].keys())
        
        with open(file_path, 'w', encoding=encoding, newline='') as csv_file:
            # Create CSV writer
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=delimiter)
            
            # Write header
            csv_writer.writeheader()
            
            # Write data rows
            csv_writer.writerows(data)
        
        logger.info(f"Successfully wrote {len(data)} rows to CSV file: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error writing CSV file {file_path}: {str(e)}")
        raise ValueError(f"Failed to write CSV file: {str(e)}")

def read_excel_file(file_path: str, options: Dict = None) -> Dict[str, pd.DataFrame]:
    """
    Reads data from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        options (dict): Dictionary of Excel reader options
        
    Returns:
        dict: Dictionary of sheet names to data frames
    """
    if options is None:
        options = {}
    
    # Default options
    sheet_name = options.get("sheet_name", None)  # None means read all sheets
    
    try:
        # Use pandas to read Excel file
        excel_data = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # If sheet_name is None, excel_data will be a dict of sheet name -> DataFrame
        if isinstance(excel_data, dict):
            logger.info(f"Successfully read {len(excel_data)} sheets from Excel file: {file_path}")
            return excel_data
        
        # If a specific sheet was requested, wrap the single DataFrame in a dict
        sheet_name = sheet_name or "Sheet1"
        logger.info(f"Successfully read sheet '{sheet_name}' from Excel file: {file_path}")
        return {sheet_name: excel_data}
    except Exception as e:
        logger.error(f"Error reading Excel file {file_path}: {str(e)}")
        raise ValueError(f"Failed to read Excel file: {str(e)}")

def write_excel_file(file_path: str, data_frames: Dict[str, pd.DataFrame], options: Dict = None) -> str:
    """
    Writes data to an Excel file.
    
    Args:
        file_path (str): Path to save the Excel file
        data_frames (dict): Dictionary of sheet names to data frames
        options (dict): Dictionary of Excel writer options
        
    Returns:
        str: Path to the created Excel file
    """
    if options is None:
        options = {}
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Create ExcelWriter object
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Write each data frame to a separate sheet
            for sheet_name, df in data_frames.items():
                df.to_excel(writer, sheet_name=sheet_name, index=options.get("index", False))
                
                # Apply formatting if specified
                if "column_widths" in options and sheet_name in options["column_widths"]:
                    worksheet = writer.sheets[sheet_name]
                    for col, width in options["column_widths"][sheet_name].items():
                        worksheet.column_dimensions[col].width = width
        
        logger.info(f"Successfully wrote {len(data_frames)} sheets to Excel file: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error writing Excel file {file_path}: {str(e)}")
        raise ValueError(f"Failed to write Excel file: {str(e)}")

def create_temp_file(content: bytes, suffix: str = None) -> str:
    """
    Creates a temporary file with the given content.
    
    Args:
        content (bytes): Binary content to write to the file
        suffix (str): File suffix/extension
        
    Returns:
        str: Path to the temporary file
    """
    try:
        # Create a temporary file with the specified suffix
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        
        # Write content to the file
        with os.fdopen(fd, 'wb') as temp_file:
            temp_file.write(content)
        
        logger.debug(f"Created temporary file: {temp_path}")
        return temp_path
    except Exception as e:
        logger.error(f"Error creating temporary file: {str(e)}")
        raise IOError(f"Failed to create temporary file: {str(e)}")

def create_temp_directory() -> str:
    """
    Creates a temporary directory.
    
    Returns:
        str: Path to the temporary directory
    """
    try:
        temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {temp_dir}")
        return temp_dir
    except Exception as e:
        logger.error(f"Error creating temporary directory: {str(e)}")
        raise IOError(f"Failed to create temporary directory: {str(e)}")

def safe_file_name(filename: str) -> str:
    """
    Sanitizes a filename to ensure it's safe for the filesystem.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Ensure filename is not too long (max 255 chars)
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    
    return filename

def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensures a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            logger.debug(f"Created directory: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {str(e)}")
        return False

def delete_file(file_path: str) -> bool:
    """
    Safely deletes a file if it exists.
    
    Args:
        file_path (str): Path to the file to delete
        
    Returns:
        bool: True if file was deleted or doesn't exist, False if deletion failed
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Deleted file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False

def move_file(source_path: str, destination_path: str, overwrite: bool = False) -> bool:
    """
    Moves a file from source to destination.
    
    Args:
        source_path (str): Source file path
        destination_path (str): Destination file path
        overwrite (bool): Whether to overwrite existing files
        
    Returns:
        bool: True if file was moved successfully, False otherwise
    """
    try:
        # Check if source file exists
        if not os.path.exists(source_path):
            logger.error(f"Source file does not exist: {source_path}")
            return False
        
        # Check if destination exists and handle based on overwrite flag
        if os.path.exists(destination_path):
            if not overwrite:
                logger.error(f"Destination file already exists and overwrite is False: {destination_path}")
                return False
            delete_file(destination_path)
        
        # Ensure destination directory exists
        dest_dir = os.path.dirname(destination_path)
        ensure_directory_exists(dest_dir)
        
        # Move the file
        shutil.move(source_path, destination_path)
        logger.debug(f"Moved file from {source_path} to {destination_path}")
        return True
    except Exception as e:
        logger.error(f"Error moving file from {source_path} to {destination_path}: {str(e)}")
        return False

def copy_file(source_path: str, destination_path: str, overwrite: bool = False) -> bool:
    """
    Copies a file from source to destination.
    
    Args:
        source_path (str): Source file path
        destination_path (str): Destination file path
        overwrite (bool): Whether to overwrite existing files
        
    Returns:
        bool: True if file was copied successfully, False otherwise
    """
    try:
        # Check if source file exists
        if not os.path.exists(source_path):
            logger.error(f"Source file does not exist: {source_path}")
            return False
        
        # Check if destination exists and handle based on overwrite flag
        if os.path.exists(destination_path):
            if not overwrite:
                logger.error(f"Destination file already exists and overwrite is False: {destination_path}")
                return False
            delete_file(destination_path)
        
        # Ensure destination directory exists
        dest_dir = os.path.dirname(destination_path)
        ensure_directory_exists(dest_dir)
        
        # Copy the file
        shutil.copy2(source_path, destination_path)
        logger.debug(f"Copied file from {source_path} to {destination_path}")
        return True
    except Exception as e:
        logger.error(f"Error copying file from {source_path} to {destination_path}: {str(e)}")
        return False

def get_file_info(file_path: str) -> Dict:
    """
    Gets information about a file (size, modification time, etc.).
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict: Dictionary containing file information
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return {}
        
        # Get file stats
        stats = os.stat(file_path)
        
        # Extract relevant information
        info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'extension': get_file_extension(file_path),
            'size': stats.st_size,
            'size_human_readable': f"{stats.st_size / (1024 * 1024):.2f} MB",
            'created_time': stats.st_ctime,
            'modified_time': stats.st_mtime,
            'accessed_time': stats.st_atime,
            'mime_type': get_mime_type(file_path)
        }
        
        return info
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {str(e)}")
        return {}

def validate_file_content(file_path: str, file_type: str = None, schema: Dict = None) -> Tuple[bool, List[str]]:
    """
    Validates the content of a file based on expected format and schema.
    
    Args:
        file_path (str): Path to the file
        file_type (str): Type of file
        schema (dict): Schema to validate against
        
    Returns:
        tuple: Tuple containing validation result (bool) and error messages (list)
    """
    # Determine file type if not provided
    if file_type is None:
        file_type = get_file_extension(file_path)
    
    errors = []
    
    try:
        # Validate based on file type
        if file_type in ['csv']:
            # Read the file
            try:
                data = read_csv_file(file_path)
                
                # Basic CSV validation
                if not data:
                    errors.append("CSV file is empty")
                
                # Schema validation if provided
                if schema:
                    # Validate against schema
                    # Example implementation - would need to be tailored to specific schema format
                    if 'required_fields' in schema:
                        for row_idx, row in enumerate(data):
                            for field in schema['required_fields']:
                                if field not in row or not row[field]:
                                    errors.append(f"Row {row_idx+1}: Missing required field '{field}'")
                
            except Exception as e:
                errors.append(f"Invalid CSV file: {str(e)}")
                
        elif file_type in ['xlsx', 'xls']:
            # Read the file
            try:
                data = read_excel_file(file_path)
                
                # Basic Excel validation
                if not data or all(df.empty for df in data.values()):
                    errors.append("Excel file is empty")
                
                # Schema validation if provided
                if schema:
                    # Validate against schema
                    # Example implementation - would need to be tailored to specific schema format
                    if 'required_sheets' in schema:
                        for sheet in schema['required_sheets']:
                            if sheet not in data:
                                errors.append(f"Missing required sheet '{sheet}'")
                
            except Exception as e:
                errors.append(f"Invalid Excel file: {str(e)}")
                
        elif file_type == 'pdf':
            # Read the file
            try:
                with open(file_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    
                    # Basic PDF validation
                    if len(reader.pages) == 0:
                        errors.append("PDF file has no pages")
                
                # No schema validation for PDF files
                
            except Exception as e:
                errors.append(f"Invalid PDF file: {str(e)}")
                
        else:
            errors.append(f"Unsupported file type: {file_type}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    except Exception as e:
        logger.error(f"Error validating file content for {file_path}: {str(e)}")
        return False, [f"Validation error: {str(e)}"]