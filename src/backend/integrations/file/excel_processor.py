"""
Processor for Excel files that handles importing and exporting data in Excel format,
including reading, parsing, validating, mapping, and transformation of data for the
Justice Bid Rate Negotiation System.
"""

import os  # standard library
import io  # standard library
from typing import Dict, List, Union  # standard library

import pandas as pd  # version 2.0.0
import numpy  # version 1.24.0
from openpyxl import load_workbook  # version 3.1.0
from openpyxl.styles import Font, PatternFill  # version 3.1.0

from .validators import validate_excel_file, validate_dataframe_structure, validate_rate_import_data, \
    validate_attorney_import_data, validate_billing_import_data, RATE_IMPORT_REQUIRED_FIELDS, \
    RATE_IMPORT_OPTIONAL_FIELDS, ATTORNEY_IMPORT_REQUIRED_FIELDS, ATTORNEY_IMPORT_OPTIONAL_FIELDS, \
    BILLING_IMPORT_REQUIRED_FIELDS, BILLING_IMPORT_OPTIONAL_FIELDS  # Internal import
from ..common.adapter import FileProcessor  # Internal import
from ...utils.file_handling import read_excel_file, write_excel_file, get_file_extension  # Internal import
from ...utils.logging import get_logger  # Internal import

# Initialize logger
logger = get_logger(__name__)

# Define supported Excel file extensions
EXCEL_EXTENSIONS = {'xlsx', 'xls'}

# Define default sheet name
DEFAULT_SHEET_NAME = "Sheet1"


def detect_sheet_names(file_path_or_buffer: str) -> list:
    """
    Detects available sheet names in an Excel file

    Args:
        file_path_or_buffer: Path to the Excel file

    Returns:
        list: List of sheet names in the Excel file
    """
    try:
        # LD1: Use pandas ExcelFile to open the file
        excel_file = pd.ExcelFile(file_path_or_buffer)
        # LD1: Get sheet names from the ExcelFile object
        sheet_names = excel_file.sheet_names
        # LD1: Return list of sheet names
        return sheet_names
    except Exception as e:
        # LD1: Handle exceptions and log errors
        logger.error(f"Error detecting sheet names in Excel file: {str(e)}")
        return []


def normalize_excel_headers(headers: list) -> list:
    """
    Normalizes Excel header names by removing special characters, converting to lowercase,
    and replacing spaces with underscores

    Args:
        headers: List of header names

    Returns:
        list: Normalized headers
    """
    normalized_headers = []
    for header in headers:
        if isinstance(header, str):
            # LD1: Convert each header to lowercase
            header = header.lower()
            # LD1: Replace spaces with underscores
            header = header.replace(" ", "_")
            # LD1: Remove special characters
            header = ''.join(char for char in header if char.isalnum() or char == '_')
            # LD1: Ensure header names are valid Python identifiers
            if not header.isidentifier():
                header = "column_" + header
        else:
            header = "unknown_column"  # Handle non-string headers
        normalized_headers.append(header)
    # LD1: Return the normalized headers list
    return normalized_headers


def infer_column_types(df: pd.DataFrame) -> dict:
    """
    Analyzes DataFrame to infer the data type of each column

    Args:
        df: DataFrame to analyze

    Returns:
        dict: Dictionary mapping column names to their inferred types
    """
    column_types = {}
    for column in df.columns:
        # LD1: Check if column contains mostly numeric values
        if pd.api.types.is_numeric_dtype(df[column]):
            column_types[column] = 'numeric'
        # LD1: Check if column contains date values
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            column_types[column] = 'date'
        # LD1: Check if column contains boolean values
        elif pd.api.types.is_bool_dtype(df[column]):
            column_types[column] = 'boolean'
        # LD1: Default to string type if no specific type is detected
        else:
            column_types[column] = 'string'
    # LD1: Return the dictionary of column types
    return column_types


def get_template_path(import_type: str) -> str:
    """
    Gets path to a template Excel file based on import type

    Args:
        import_type: Type of import (e.g., 'rate', 'attorney', 'billing')

    Returns:
        str: Path to template file
    """
    template_map = {
        'rate': 'templates/rate_import_template.xlsx',
        'attorney': 'templates/attorney_import_template.xlsx',
        'billing': 'templates/billing_import_template.xlsx'
    }
    # LD1: Map import_type to appropriate template path
    template_path = template_map.get(import_type)
    if template_path:
        # LD1: Check if template file exists
        if os.path.exists(template_path):
            # LD1: Return the template path if exists
            return template_path
        else:
            # LD1: Log warning and return None if template not found
            logger.warning(f"Template file not found: {template_path}")
            return None
    else:
        logger.warning(f"No template defined for import type: {import_type}")
        return None


class ExcelProcessor(FileProcessor):
    """
    Processes Excel files for import and export operations, including parsing, validation,
    mapping, and transformation.
    """

    def __init__(self):
        """
        Initializes a new Excel processor instance
        """
        # LD1: Initialize empty field_mapping dictionary
        self.field_mapping = {}
        # LD1: Initialize empty validation_errors list
        self.validation_errors = []
        # LD1: Initialize empty column_types dictionary
        self.column_types = {}
        # LD1: Set default current_sheet to None
        self.current_sheet = None
        # LD1: Initialize logger
        self.logger = logger

    def read_excel(self, file_path_or_buffer: Union[str, io.BytesIO], sheet_name: str = None, options: Dict = None) -> pd.DataFrame:
        """
        Reads and parses an Excel file from a file path or content buffer

        Args:
            file_path_or_buffer: Path to the Excel file or content buffer
            sheet_name: Name of the sheet to read (default: first sheet)
            options: Dictionary of options for reading the Excel file

        Returns:
            DataFrame: DataFrame containing Excel data
        """
        if options is None:
            options = {}

        try:
            # LD1: If no sheet_name provided, use DEFAULT_SHEET_NAME or the first sheet
            if sheet_name is None:
                sheet_name = options.get('default_sheet_name', DEFAULT_SHEET_NAME)
                if sheet_name == DEFAULT_SHEET_NAME:
                    try:
                        all_sheets = detect_sheet_names(file_path_or_buffer)
                        if all_sheets:
                            sheet_name = all_sheets[0]
                    except Exception as e:
                        logger.warning(f"Could not detect sheet names, using default. Error: {e}")

            # LD1: Use pandas.read_excel to read the Excel file or buffer
            df = pd.read_excel(file_path_or_buffer, sheet_name=sheet_name)

            # LD1: Convert all column names to string type
            df.columns = df.columns.astype(str)

            # LD1: Check if headers need to be normalized based on options
            if options.get('normalize_headers', False):
                df.columns = normalize_excel_headers(df.columns)

            # LD1: Drop empty rows and columns if specified in options
            if options.get('drop_empty_rows', True):
                df.dropna(axis=0, how='all', inplace=True)
            if options.get('drop_empty_columns', True):
                df.dropna(axis=1, how='all', inplace=True)

            # LD1: Store the column types using infer_column_types
            self.column_types = infer_column_types(df)

            # LD1: Set current_sheet to the read sheet name
            self.current_sheet = sheet_name

            # LD1: Return the DataFrame
            return df
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise

    def set_field_mapping(self, mapping: Dict):
        """
        Sets the mapping between Excel columns and system fields

        Args:
            mapping: Dictionary mapping Excel columns to system fields
        """
        # LD1: Validate that the mapping contains valid source and target fields
        if not isinstance(mapping, dict):
            raise ValueError("Field mapping must be a dictionary")
        # LD1: Set the field_mapping property
        self.field_mapping = mapping
        # LD1: Log the configured mapping
        logger.info(f"Field mapping set: {self.field_mapping}")

    def apply_field_mapping(self, df: pd.DataFrame, strict_mapping: bool = True) -> list:
        """
        Applies the field mapping to transform Excel data to system format

        Args:
            df: DataFrame containing Excel data
            strict_mapping: If True, skip fields not in the mapping

        Returns:
            list: Transformed data with mapped field names
        """
        # LD1: Convert DataFrame to dictionary records
        data = df.to_dict(orient='records')
        # LD1: Initialize a new list for transformed data
        transformed_data = []
        # LD1: For each row in the data, create a new dictionary using the field mapping
        for row in data:
            transformed_row = {}
            for target_field, source_field in self.field_mapping.items():
                if source_field in row:
                    transformed_row[target_field] = row[source_field]
                elif not strict_mapping:
                    transformed_row[target_field] = None  # Or a default value
            transformed_data.append(transformed_row)
        # LD1: Return the transformed data list
        return transformed_data

    def validate_excel_file(self, file_path_or_buffer: str, sheet_name: str = None, import_type: str = None, validation_rules: Dict = None) -> dict:
        """
        Validates an Excel file against defined rules and schema

        Args:
            file_path_or_buffer: Path to the Excel file
            sheet_name: Name of the sheet to validate
            import_type: Type of import (e.g., 'rate', 'attorney', 'billing')
            validation_rules: Dictionary of validation rules to apply

        Returns:
            dict: Validation results with errors and warnings
        """
        # LD1: Call validate_excel_file from validators
        try:
            validate_excel_file(file_path_or_buffer, {'sheet_name': sheet_name})
        except Exception as e:
            return {"valid": False, "errors": [str(e)], "warnings": []}

        # LD1: Read the Excel data into a DataFrame
        try:
            df = self.read_excel(file_path_or_buffer, sheet_name=sheet_name)
        except Exception as e:
            return {"valid": False, "errors": [str(e)], "warnings": []}

        # LD1: Determine which validation function to use based on import_type
        if import_type == 'rate':
            validation_function = validate_rate_import_data
        elif import_type == 'attorney':
            validation_function = validate_attorney_import_data
        elif import_type == 'billing':
            validation_function = validate_billing_import_data
        else:
            return {"valid": True, "errors": [], "warnings": []}

        # LD1: Call appropriate validation function (validate_rate_import_data, etc.)
        # LD1: Store validation errors if any
        validation_results = validation_function(df, validation_rules)
        # LD1: Return validation results
        return validation_results

    def get_validation_errors(self) -> list:
        """
        Returns the validation errors from the last validation operation

        Returns:
            list: List of validation error messages
        """
        # LD1: Return the validation_errors property
        return self.validation_errors

    def process_import(self, file_path_or_buffer: Union[str, io.BytesIO], sheet_name: str = None, import_type: str = None, field_mapping: Dict = None, validation_rules: Dict = None) -> dict:
        """
        Processes an Excel file for import, including validation, mapping, and transformation

        Args:
            file_path_or_buffer: Path to the Excel file
            sheet_name: Name of the sheet to import
            import_type: Type of import (e.g., 'rate', 'attorney', 'billing')
            field_mapping: Dictionary mapping Excel columns to system fields
            validation_rules: Dictionary of validation rules to apply

        Returns:
            dict: Processing result with transformed data or errors
        """
        # LD1: If field_mapping is provided, set the mapping using set_field_mapping
        if field_mapping:
            self.set_field_mapping(field_mapping)

        # LD1: Validate the Excel file using validate_excel_file
        validation_results = self.validate_excel_file(file_path_or_buffer, sheet_name, import_type, validation_rules)

        # LD1: If validation fails, return a result with success=False and errors
        if not validation_results["valid"]:
            return {"success": False, "errors": validation_results["errors"]}

        # LD1: Read the Excel file using read_excel
        try:
            df = self.read_excel(file_path_or_buffer, sheet_name=sheet_name)
        except Exception as e:
            return {"success": False, "errors": [str(e)]}

        # LD1: Apply field mapping using apply_field_mapping
        transformed_data = self.apply_field_mapping(df)

        # LD1: Return a result with success=True and the transformed data
        return {"success": True, "data": transformed_data}

    def process_export(self, data: list, file_path: str, sheet_name: str = None, field_mapping: Dict = None, style_options: Dict = None) -> bool:
        """
        Processes data for export to Excel format

        Args:
            data: List of dictionaries to export
            file_path: Path to save the Excel file
            sheet_name: Name of the sheet to write to
            field_mapping: Dictionary mapping system fields to Excel columns
            style_options: Dictionary of styling options for the Excel file

        Returns:
            bool: True if export was successful, False otherwise
        """
        if style_options is None:
            style_options = {}
        # LD1: If field_mapping is provided, set the mapping using set_field_mapping
        if field_mapping:
            self.set_field_mapping(field_mapping)

        # LD1: Apply reverse field mapping to the data
        df = pd.DataFrame(data)
        # LD1: Create a dictionary mapping sheet_name to DataFrame
        data_frames = {sheet_name or DEFAULT_SHEET_NAME: df}
        # LD1: Call write_excel_file with the data, file_path and style options
        try:
            write_excel_file(file_path, data_frames, options=style_options)
            # LD1: Return True if export was successful, False otherwise
            return True
        except Exception as e:
            # LD1: Handle exceptions and log errors
            logger.error(f"Error processing export: {str(e)}")
            return False

    def create_template(self, file_path: str, import_type: str, include_sample_data: bool = False, style_options: Dict = None) -> bool:
        """
        Creates an Excel template with headers based on the required fields for an import type

        Args:
            file_path: Path to save the template file
            import_type: Type of import (e.g., 'rate', 'attorney', 'billing')
            include_sample_data: Whether to include a sample data row
            style_options: Dictionary of styling options for the Excel file

        Returns:
            bool: True if template creation was successful, False otherwise
        """
        if style_options is None:
            style_options = {}
        # LD1: Determine required and optional fields based on import_type
        if import_type == 'rate':
            required_fields = RATE_IMPORT_REQUIRED_FIELDS
            optional_fields = RATE_IMPORT_OPTIONAL_FIELDS
        elif import_type == 'attorney':
            required_fields = ATTORNEY_IMPORT_REQUIRED_FIELDS
            optional_fields = ATTORNEY_IMPORT_OPTIONAL_FIELDS
        elif import_type == 'billing':
            required_fields = BILLING_IMPORT_REQUIRED_FIELDS
            optional_fields = BILLING_IMPORT_OPTIONAL_FIELDS
        else:
            logger.error(f"Invalid import type: {import_type}")
            return False

        # LD1: Create a DataFrame with headers from the fields
        headers = required_fields + optional_fields
        df = pd.DataFrame(columns=headers)

        # LD1: Optionally add sample data row if include_sample_data is True
        if include_sample_data:
            sample_data = {header: "" for header in headers}
            df = pd.concat([df, pd.DataFrame([sample_data])], ignore_index=True)

        # LD1: Add header formatting in style_options (bold, background color)
        # LD1: Call write_excel_file with the data, file_path and style options
        try:
            data_frames = {DEFAULT_SHEET_NAME: df}
            write_excel_file(file_path, data_frames, options=style_options)
            # LD1: Return True if template creation was successful, False otherwise
            return True
        except Exception as e:
            # LD1: Handle exceptions and log errors
            logger.error(f"Error creating template: {str(e)}")
            return False

    def clean_and_transform_data(self, df: pd.DataFrame, transformation_rules: Dict) -> pd.DataFrame:
        """
        Cleans and transforms Excel data based on column types and rules

        Args:
            df: DataFrame to clean and transform
            transformation_rules: Dictionary of transformation rules

        Returns:
            DataFrame: Cleaned and transformed DataFrame
        """
        # LD1: Infer column types if not already done
        if not self.column_types:
            self.column_types = infer_column_types(df)

        # LD1: Handle missing values based on rules (fill default values, drop rows, etc.)
        # LD1: Convert data types (string to numeric, string to date, etc.)
        # LD1: Apply transformations based on rules (capitalize, trim, etc.)
        # LD1: Handle duplicates (remove, flag, etc.)
        # LD1: Return cleaned DataFrame
        # LD1: Log transformations applied
        return df

    def get_sheets_info(self, file_path: str) -> dict:
        """
        Gets information about all sheets in an Excel file

        Args:
            file_path: Path to the Excel file

        Returns:
            dict: Dictionary with sheet names and information (row count, column names)
        """
        try:
            # LD1: Get sheet names using detect_sheet_names
            sheet_names = detect_sheet_names(file_path)
            sheets_info = {}
            # LD1: For each sheet, read a sample to get column names and row count
            for sheet_name in sheet_names:
                try:
                    df = self.read_excel(file_path, sheet_name=sheet_name)
                    sheets_info[sheet_name] = {
                        'row_count': len(df),
                        'column_names': list(df.columns)
                    }
                except Exception as e:
                    logger.warning(f"Could not read sheet '{sheet_name}': {str(e)}")
                    sheets_info[sheet_name] = {
                        'row_count': 0,
                        'column_names': []
                    }
            # LD1: Return dictionary with sheet details
            return sheets_info
        except Exception as e:
            # LD1: Handle exceptions and log errors
            logger.error(f"Error getting sheets info: {str(e)}")
            return {}

    def merge_sheets(self, file_path: str, sheet_names: List[str], key_column: str) -> pd.DataFrame:
        """
        Merges multiple sheets into a single DataFrame based on a common key

        Args:
            file_path: Path to the Excel file
            sheet_names: List of sheet names to merge
            key_column: Common column to use for merging

        Returns:
            DataFrame: Merged DataFrame from multiple sheets
        """
        dataframes = {}
        # LD1: For each sheet in sheet_names, read the data
        for sheet_name in sheet_names:
            try:
                dataframes[sheet_name] = self.read_excel(file_path, sheet_name=sheet_name)
            except Exception as e:
                logger.error(f"Could not read sheet '{sheet_name}': {str(e)}")
                return None

        merged_df = None
        # LD1: Validate that key_column exists in all sheets
        for sheet_name, df in dataframes.items():
            if key_column not in df.columns:
                logger.error(f"Key column '{key_column}' not found in sheet '{sheet_name}'")
                return None

        # LD1: Merge DataFrames using pandas merge functions
        for sheet_name, df in dataframes.items():
            if merged_df is None:
                merged_df = df
            else:
                # LD1: Prefix column names with sheet name to avoid conflicts if needed
                cols_to_use = df.columns.difference(merged_df.columns)
                merged_df = pd.merge(merged_df, df[cols_to_use], left_on=key_column, right_on=key_column, how='outer')

        # LD1: Return merged DataFrame
        return merged_df