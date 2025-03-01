"""
Processes CSV files for import and export operations, handling parsing, validation, mapping, and transformation.
"""

import csv  # built-in
import io  # built-in
import typing  # built-in
import pandas  # package version: ^1.5.0

from .validators import validate_csv_structure, validate_csv_data  # internal
from ...utils.file_handling import read_file, save_file  # internal
from ..common.adapter import FileProcessor  # internal
from ...utils.logging import get_logger  # internal

# Initialize logger
logger = get_logger(__name__)


def detect_delimiter(file_content: str) -> str:
    """
    Detects the delimiter used in a CSV file by analyzing the first few lines.

    Args:
        file_content: The content of the CSV file as a string.

    Returns:
        The detected delimiter character (comma, semicolon, tab, etc.).
        Defaults to comma if no clear delimiter is detected.
    """
    # Analyze the first few lines of the file content
    lines = file_content.splitlines()
    sample_lines = lines[:5]  # Use the first 5 lines as a sample

    # Count occurrences of common delimiters (comma, semicolon, tab)
    delimiter_counts = {',': 0, ';': 0, '\t': 0}
    for line in sample_lines:
        for delimiter in delimiter_counts:
            delimiter_counts[delimiter] += line.count(delimiter)

    # Return the most frequently occurring delimiter
    most_likely_delimiter = max(delimiter_counts, key=delimiter_counts.get)

    # Default to comma if no clear delimiter is detected
    if delimiter_counts[most_likely_delimiter] == 0:
        return ','
    else:
        return most_likely_delimiter


def normalize_headers(headers: list) -> list:
    """
    Normalizes header names by removing special characters, converting to lowercase, and replacing spaces with underscores.

    Args:
        headers: A list of header names.

    Returns:
        A list of normalized header names.
    """
    normalized_headers = []
    for header in headers:
        # Convert each header to lowercase
        header = header.lower()
        # Replace spaces with underscores
        header = header.replace(' ', '_')
        # Remove special characters
        header = ''.join(char for char in header if char.isalnum() or char == '_')
        normalized_headers.append(header)
    return normalized_headers


def infer_column_types(data: list, headers: list) -> dict:
    """
    Analyzes the data to infer the data type of each column.

    Args:
        data: A list of data rows.
        headers: A list of column headers.

    Returns:
        A dictionary mapping column names to their inferred types (e.g., 'int', 'float', 'str', 'date').
    """
    column_types = {}
    for header in headers:
        # Initialize an empty list to store values for type inference
        values = []
        # Collect a sample of values from the data
        for row in data[:min(100, len(data))]:  # Analyze up to 100 rows
            value = row.get(header)
            if value:
                values.append(value)

        # If no values are found, default to string
        if not values:
            column_types[header] = 'str'
            continue

        # Attempt to parse values as different types (int, float, date, etc.)
        inferred_type = 'str'  # Default type
        try:
            # Check if all values can be converted to integers
            all(isinstance(int(float(v)), int) for v in values)
            inferred_type = 'int'
        except ValueError:
            try:
                # Check if all values can be converted to floats
                all(isinstance(float(v), float) for v in values)
                inferred_type = 'float'
            except ValueError:
                try:
                    # Check if all values can be converted to dates
                    all(pandas.to_datetime(v) for v in values)
                    inferred_type = 'date'
                except ValueError:
                    pass  # Keep default 'str' type

        column_types[header] = inferred_type
    return column_types


class CSVProcessor(FileProcessor):
    """
    Processes CSV files for import and export operations, handling parsing, validation, mapping, and transformation.
    """

    def __init__(self):
        """
        Initializes a new CSV processor instance.
        """
        # Initialize empty field_mapping dictionary
        self.field_mapping = {}
        # Initialize empty validation_errors list
        self.validation_errors = []
        # Initialize empty column_types dictionary
        self.column_types = {}
        # Set default delimiter to comma
        self.delimiter = ','

    def read_csv(self, file_path_or_content: str, is_content: bool = False, has_headers: bool = True) -> tuple:
        """
        Reads and parses a CSV file from a file path or content string.

        Args:
            file_path_or_content: The path to the CSV file or the CSV content itself.
            is_content: A boolean indicating whether the input is a file path or content.
            has_headers: A boolean indicating whether the CSV file has a header row.

        Returns:
            A tuple containing the headers (list) and data (list of dictionaries).
        """
        try:
            if not is_content:
                # If is_content is False, read the file from the file path
                file_content = read_file(file_path_or_content)
            else:
                # Use the provided content directly
                file_content = file_path_or_content

            # Detect the delimiter if not specified
            self.delimiter = detect_delimiter(file_content)

            # Use csv.reader or pandas to parse the CSV content
            data = []
            headers = []
            csvfile = io.StringIO(file_content)
            reader = csv.DictReader(csvfile, delimiter=self.delimiter)

            if has_headers:
                # Extract headers if has_headers is True
                headers = reader.fieldnames
                # Read the data rows
                for row in reader:
                    data.append(row)
            else:
                # If no headers, create a list of dictionaries with numbered keys
                reader = csv.reader(io.StringIO(file_content), delimiter=self.delimiter)
                all_rows = list(reader)
                headers = [f'column_{i+1}' for i in range(len(all_rows[0]))]
                for row in all_rows:
                    data.append({headers[i]: row[i] for i in range(len(row))})

            # Return the headers and data as a tuple
            return headers, data
        except Exception as e:
            logger.error(f"Error reading CSV file/content: {str(e)}")
            raise

    def set_field_mapping(self, mapping: dict) -> None:
        """
        Sets the mapping between CSV columns and system fields.

        Args:
            mapping: A dictionary where keys are CSV column names and values are system field names.
        """
        # Validate that the mapping contains valid source and target fields
        if not isinstance(mapping, dict):
            raise ValueError("Field mapping must be a dictionary")

        # Set the field_mapping property
        self.field_mapping = mapping
        # Log the configured mapping
        logger.info(f"Configured field mapping: {self.field_mapping}")

    def apply_field_mapping(self, headers: list, data: list) -> list:
        """
        Applies the field mapping to transform CSV data to system format.

        Args:
            headers: A list of CSV column headers.
            data: A list of dictionaries representing CSV data rows.

        Returns:
            A list of dictionaries representing the transformed data with mapped field names.
        """
        # Create a mapping between header indexes and target field names
        header_index_mapping = {i: self.field_mapping.get(header) for i, header in enumerate(headers)}

        # Initialize a new list for transformed data
        transformed_data = []

        # For each row in the data, create a new dictionary using the field mapping
        for row in data:
            transformed_row = {}
            for i, header in enumerate(headers):
                target_field = header_index_mapping.get(i)
                if target_field:
                    transformed_row[target_field] = row.get(header)
            transformed_data.append(transformed_row)

        # Return the transformed data list
        return transformed_data

    def validate_csv_file(self, file_path_or_content: str, is_content: bool, validation_schema: dict) -> bool:
        """
        Validates a CSV file against defined rules and schema.

        Args:
            file_path_or_content: The path to the CSV file or the CSV content itself.
            is_content: A boolean indicating whether the input is a file path or content.
            validation_schema: A dictionary defining the validation rules and schema.

        Returns:
            True if validation passes, False otherwise.
        """
        try:
            # Read the CSV file/content using read_csv method
            headers, data = self.read_csv(file_path_or_content, is_content)
            # Validate the structure using validate_csv_structure from validators
            validate_csv_structure(headers, validation_schema)
            # Validate the data using validate_csv_data from validators
            validate_csv_data(data, validation_schema)
            # Store any validation errors in the validation_errors property
            self.validation_errors = []  # Reset errors if validation passes
            # Return True if no validation errors, False otherwise
            return True
        except Exception as e:
            self.validation_errors = [str(e)]
            return False

    def get_validation_errors(self) -> list:
        """
        Returns the validation errors from the last validation operation.

        Returns:
            A list of validation error messages.
        """
        # Return the validation_errors property
        return self.validation_errors

    def process_import(self, file_path_or_content: str, is_content: bool, validation_schema: dict, field_mapping: dict) -> dict:
        """
        Processes a CSV file for import, including validation, mapping, and transformation.

        Args:
            file_path_or_content: The path to the CSV file or the CSV content itself.
            is_content: A boolean indicating whether the input is a file path or content.
            validation_schema: A dictionary defining the validation rules and schema.
            field_mapping: A dictionary defining the mapping between CSV columns and system fields.

        Returns:
            A dictionary containing the processing result with transformed data or errors.
        """
        try:
            # If field_mapping is provided, set the mapping using set_field_mapping
            self.set_field_mapping(field_mapping)
            # Validate the CSV file using validate_csv_file
            if not self.validate_csv_file(file_path_or_content, is_content, validation_schema):
                # If validation fails, return a result with success=False and errors
                return {"success": False, "errors": self.get_validation_errors()}
            # Read the CSV file using read_csv
            headers, data = self.read_csv(file_path_or_content, is_content)
            # Apply field mapping using apply_field_mapping
            transformed_data = self.apply_field_mapping(headers, data)
            # Return a result with success=True and the transformed data
            return {"success": True, "data": transformed_data}
        except Exception as e:
            return {"success": False, "errors": [str(e)]}

    def process_export(self, data: list, field_mapping: dict, delimiter: str = ',') -> str:
        """
        Processes data for export to CSV format.

        Args:
            data: A list of dictionaries representing the data to export.
            field_mapping: A dictionary defining the mapping between system fields and CSV columns.
            delimiter: The delimiter to use in the CSV file (default: comma).

        Returns:
            A string containing the CSV data.
        """
        try:
            # If field_mapping is provided, set the mapping using set_field_mapping
            self.set_field_mapping(field_mapping)

            # Initialize an empty string buffer for the CSV data
            csvfile = io.StringIO()
            # Create a csv.writer with the specified delimiter
            writer = csv.DictWriter(csvfile, fieldnames=field_mapping.keys(), delimiter=delimiter)
            # Write the headers based on the field mapping
            writer.writeheader()

            # Transform and write each data row
            for row in data:
                transformed_row = {}
                for target_field, source_field in field_mapping.items():
                    transformed_row[target_field] = row.get(source_field)
                writer.writerow(transformed_row)

            # Return the CSV string from the buffer
            return csvfile.getvalue()
        except Exception as e:
            logger.error(f"Error processing CSV export: {str(e)}")
            raise

    def create_template(self, required_fields: list, optional_fields: list, delimiter: str = ',') -> str:
        """
        Creates a CSV template with headers based on the required fields.

        Args:
            required_fields: A list of required field names.
            optional_fields: A list of optional field names.
            delimiter: The delimiter to use in the CSV file (default: comma).

        Returns:
            A string containing the CSV template with headers.
        """
        try:
            # Initialize an empty string buffer for the CSV template
            csvfile = io.StringIO()
            # Create a csv.writer with the specified delimiter
            writer = csv.writer(csvfile, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)

            # Combine required and optional fields, marking optional fields with a '*' suffix
            header_row = required_fields + [f"{field}*" for field in optional_fields]
            # Write the header row
            writer.writerow(header_row)

            # Return the CSV template string from the buffer
            return csvfile.getvalue()
        except Exception as e:
            logger.error(f"Error creating CSV template: {str(e)}")
            raise

    def infer_and_clean_data(self, headers: list, data: list) -> list:
        """
        Infers column types and cleans/transforms data accordingly.

        Args:
            headers: A list of column headers.
            data: A list of data rows.

        Returns:
            A list of cleaned and transformed data.
        """
        try:
            # Infer column types using infer_column_types function
            column_types = infer_column_types(data, headers)

            # Initialize a new list for cleaned data
            cleaned_data = []

            # For each row in the data, attempt to convert values to their inferred types
            for row in data:
                cleaned_row = {}
                for header in headers:
                    value = row.get(header)
                    inferred_type = column_types.get(header)

                    try:
                        if inferred_type == 'int':
                            cleaned_value = int(float(value)) if value else None
                        elif inferred_type == 'float':
                            cleaned_value = float(value) if value else None
                        elif inferred_type == 'date':
                            cleaned_value = pandas.to_datetime(value).date() if value else None
                        else:
                            cleaned_value = str(value) if value else None
                    except ValueError:
                        cleaned_value = None  # Handle conversion errors gracefully

                    cleaned_row[header] = cleaned_value
                cleaned_data.append(cleaned_row)

            # Return the cleaned data list
            return cleaned_data
        except Exception as e:
            logger.error(f"Error inferring and cleaning data: {str(e)}")
            raise