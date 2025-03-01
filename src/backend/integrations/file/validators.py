"""
Specialized validation module for file imports and exports in the Justice Bid Rate Negotiation System.
Provides validators for various file formats (CSV, Excel), data structure validation, and 
domain-specific validation for rate, attorney, and billing data imports.
"""

import os
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from decimal import Decimal
import decimal
from datetime import date, datetime

from ...utils.logging import get_logger
from ...utils.file_handling import get_file_extension, validate_file_size
from ...utils.validators import validate_decimal, validate_string, validate_date, validate_currency_code
from ...api.core.errors import ValidationError
from ...utils.constants import DEFAULT_CURRENCY, RATE_DECIMALS

# Set up logger
logger = get_logger(__name__)

# Allowed file extensions
CSV_ALLOWED_EXTENSIONS = {'csv'}
EXCEL_ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
FILE_SIZE_LIMIT_MB = 50  # Maximum file size in MB

# Required fields for various import types
RATE_IMPORT_REQUIRED_FIELDS = ['Firm Name', 'Attorney Name', 'Rate Amount', 'Effective Date']
ATTORNEY_IMPORT_REQUIRED_FIELDS = ['Firm Name', 'Attorney Name', 'Bar Date', 'Office']
BILLING_IMPORT_REQUIRED_FIELDS = ['Firm Name', 'Attorney Name', 'Hours', 'Fees', 'Date']

# Optional fields for various import types
RATE_IMPORT_OPTIONAL_FIELDS = ['Currency', 'Expiration Date', 'Timekeeper ID', 'Office', 'Practice Area', 'Staff Class']
ATTORNEY_IMPORT_OPTIONAL_FIELDS = ['Graduation Date', 'Timekeeper ID', 'Practice Area', 'Staff Class']
BILLING_IMPORT_OPTIONAL_FIELDS = ['Matter ID', 'Practice Area', 'Office', 'Currency', 'AFA Flag']


def validate_file_basics(file_path: str, allowed_extensions: set, max_size_mb: int) -> bool:
    """
    Validates basic file properties like existence, extension, and size.
    
    Args:
        file_path: Path to the file
        allowed_extensions: Set of allowed file extensions
        max_size_mb: Maximum file size in megabytes
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    # Validate file extension
    extension = get_file_extension(file_path)
    if extension not in allowed_extensions:
        raise ValidationError(
            f"Invalid file format: .{extension}. Allowed formats: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size
    file_size_bytes = os.path.getsize(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    
    if file_size_bytes > max_size_bytes:
        raise ValidationError(
            f"File size ({file_size_bytes / (1024 * 1024):.2f} MB) exceeds maximum allowed size of {max_size_mb} MB"
        )
    
    return True


def validate_csv_file(file_path: str, options: Dict = None) -> bool:
    """
    Validates that a file is a properly formatted CSV file.
    
    Args:
        file_path: Path to the file
        options: Dictionary of validation options
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if options is None:
        options = {}
    
    # Validate basic file properties
    validate_file_basics(file_path, CSV_ALLOWED_EXTENSIONS, options.get('max_size_mb', FILE_SIZE_LIMIT_MB))
    
    # Try to read the CSV file with pandas
    try:
        df = pd.read_csv(
            file_path,
            encoding=options.get('encoding', 'utf-8'),
            sep=options.get('delimiter', ','),
            nrows=10  # Read just a few rows to validate format
        )
        
        # Check if file has content
        if df.empty:
            raise ValidationError("CSV file is empty")
        
        # Check if file has at least one column
        if len(df.columns) == 0:
            raise ValidationError("CSV file has no columns")
        
        return True
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        else:
            raise ValidationError(f"Invalid CSV file format: {str(e)}")


def validate_excel_file(file_path: str, options: Dict = None) -> bool:
    """
    Validates that a file is a properly formatted Excel file.
    
    Args:
        file_path: Path to the file
        options: Dictionary of validation options
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if options is None:
        options = {}
    
    # Validate basic file properties
    validate_file_basics(file_path, EXCEL_ALLOWED_EXTENSIONS, options.get('max_size_mb', FILE_SIZE_LIMIT_MB))
    
    # Try to read the Excel file with pandas
    try:
        sheet_name = options.get('sheet_name', 0)  # Default to first sheet
        
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            nrows=10  # Read just a few rows to validate format
        )
        
        # Check if file has content
        if df.empty:
            raise ValidationError(f"Excel sheet '{sheet_name}' is empty")
        
        # Check if file has at least one column
        if len(df.columns) == 0:
            raise ValidationError(f"Excel sheet '{sheet_name}' has no columns")
        
        return True
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        else:
            raise ValidationError(f"Invalid Excel file format: {str(e)}")


def validate_dataframe_structure(df: pd.DataFrame, required_columns: List, optional_columns: List) -> bool:
    """
    Validates that a pandas DataFrame has the required structure and columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of columns that must be present
        optional_columns: List of columns that may be present
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    # Check if dataframe is empty
    if df.empty:
        raise ValidationError("Data is empty")
    
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValidationError(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Check for unknown columns (not in required or optional)
    allowed_columns = set(required_columns + optional_columns)
    unknown_columns = [col for col in df.columns if col not in allowed_columns]
    if unknown_columns:
        logger.warning(f"Found unknown columns that will be ignored: {', '.join(unknown_columns)}")
    
    # Check for missing values in required columns
    for col in required_columns:
        if df[col].isna().any():
            missing_rows = df[df[col].isna()].index.tolist()
            raise ValidationError(f"Column '{col}' has missing values in rows: {missing_rows}")
    
    return True


def validate_rate_import_data(df: pd.DataFrame, validation_rules: Dict = None) -> Dict:
    """
    Validates that rate import data meets business rules and data type requirements.
    
    Args:
        df: DataFrame containing rate data
        validation_rules: Dictionary of validation rules to apply
        
    Returns:
        Dictionary with validation results including warnings and errors
    """
    if validation_rules is None:
        validation_rules = {}
    
    validation_results = {"valid": True, "errors": [], "warnings": []}
    
    try:
        # Validate dataframe structure first
        validate_dataframe_structure(df, RATE_IMPORT_REQUIRED_FIELDS, RATE_IMPORT_OPTIONAL_FIELDS)
        
        # Validate data types and business rules
        errors = []
        warnings = []
        
        # Process each row
        for idx, row in df.iterrows():
            row_num = idx + 2  # +2 because idx is 0-based and we have a header row
            
            try:
                # Validate rate amount
                try:
                    rate_amount = Decimal(str(row['Rate Amount']))
                    max_decimals = validation_rules.get('max_decimals', RATE_DECIMALS)
                    min_rate = validation_rules.get('min_rate', Decimal('0'))
                    
                    # Check for negative rates
                    if rate_amount < 0:
                        errors.append(f"Row {row_num}: Rate amount cannot be negative")
                    
                    # Check minimum rate if specified
                    if rate_amount < min_rate:
                        errors.append(f"Row {row_num}: Rate amount must be at least {min_rate}")
                    
                    # Check decimal places
                    decimal_tuple = rate_amount.as_tuple()
                    if decimal_tuple.exponent < 0 and abs(decimal_tuple.exponent) > max_decimals:
                        errors.append(f"Row {row_num}: Rate amount has too many decimal places (max {max_decimals})")
                    
                except (ValueError, TypeError, decimal.InvalidOperation):
                    errors.append(f"Row {row_num}: Invalid rate amount format")
                
                # Validate currency if present
                if 'Currency' in row and not pd.isna(row['Currency']):
                    try:
                        currency = str(row['Currency']).strip().upper()
                        if not validate_currency_code(currency, f"Row {row_num}: Currency"):
                            errors.append(f"Row {row_num}: Invalid currency code: {currency}")
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                
                # Validate effective date
                try:
                    effective_date = pd.to_datetime(row['Effective Date']).date()
                except Exception:
                    errors.append(f"Row {row_num}: Invalid effective date format")
                
                # Validate expiration date if present
                if 'Expiration Date' in row and not pd.isna(row['Expiration Date']):
                    try:
                        expiration_date = pd.to_datetime(row['Expiration Date']).date()
                        
                        # Check that expiration date is after effective date
                        if 'Effective Date' in row and not pd.isna(row['Effective Date']):
                            effective_date = pd.to_datetime(row['Effective Date']).date()
                            if expiration_date <= effective_date:
                                errors.append(f"Row {row_num}: Expiration date must be after effective date")
                    except Exception:
                        errors.append(f"Row {row_num}: Invalid expiration date format")
                
                # Check rate increase against historical rate if provided in validation rules
                if validation_rules.get('historical_rates') and 'Attorney Name' in row:
                    attorney_name = str(row['Attorney Name']).strip()
                    historical_rates = validation_rules.get('historical_rates', {})
                    
                    if attorney_name in historical_rates:
                        old_rate = Decimal(str(historical_rates[attorney_name]))
                        new_rate = Decimal(str(row['Rate Amount']))
                        max_increase = validation_rules.get('max_increase_percent', Decimal('10'))
                        
                        increase_percent = ((new_rate - old_rate) / old_rate) * Decimal('100')
                        
                        if increase_percent > max_increase:
                            warnings.append(
                                f"Row {row_num}: Rate increase of {increase_percent:.2f}% for {attorney_name} "
                                f"exceeds recommended maximum of {max_increase}%"
                            )
            
            except Exception as e:
                errors.append(f"Row {row_num}: Validation error: {str(e)}")
        
        # Update validation results
        if errors:
            validation_results["valid"] = False
            validation_results["errors"] = errors
        
        validation_results["warnings"] = warnings
    
    except ValidationError as e:
        validation_results["valid"] = False
        validation_results["errors"] = [str(e)]
    
    return validation_results


def validate_attorney_import_data(df: pd.DataFrame, validation_rules: Dict = None) -> Dict:
    """
    Validates that attorney import data meets business rules and data type requirements.
    
    Args:
        df: DataFrame containing attorney data
        validation_rules: Dictionary of validation rules to apply
        
    Returns:
        Dictionary with validation results including warnings and errors
    """
    if validation_rules is None:
        validation_rules = {}
    
    validation_results = {"valid": True, "errors": [], "warnings": []}
    
    try:
        # Validate dataframe structure first
        validate_dataframe_structure(df, ATTORNEY_IMPORT_REQUIRED_FIELDS, ATTORNEY_IMPORT_OPTIONAL_FIELDS)
        
        # Validate data types and business rules
        errors = []
        warnings = []
        
        # Check for potential duplicate attorneys
        if 'Attorney Name' in df.columns and 'Firm Name' in df.columns:
            duplicate_check = df.duplicated(subset=['Firm Name', 'Attorney Name'], keep=False)
            if duplicate_check.any():
                duplicate_rows = df[duplicate_check].index.tolist()
                duplicate_rows = [r + 2 for r in duplicate_rows]  # +2 for 0-based index and header
                warnings.append(f"Potential duplicate attorneys found in rows: {duplicate_rows}")
        
        # Process each row
        for idx, row in df.iterrows():
            row_num = idx + 2  # +2 because idx is 0-based and we have a header row
            
            try:
                # Validate attorney name format
                if not pd.isna(row['Attorney Name']):
                    attorney_name = str(row['Attorney Name']).strip()
                    if not attorney_name or len(attorney_name) < 2:
                        errors.append(f"Row {row_num}: Invalid attorney name: too short")
                
                # Validate bar date
                try:
                    bar_date = pd.to_datetime(row['Bar Date']).date()
                    
                    # Check if bar date is in the future
                    if bar_date > date.today():
                        errors.append(f"Row {row_num}: Bar date cannot be in the future")
                    
                except Exception:
                    errors.append(f"Row {row_num}: Invalid bar date format")
                
                # Validate graduation date if present
                if 'Graduation Date' in row and not pd.isna(row['Graduation Date']):
                    try:
                        graduation_date = pd.to_datetime(row['Graduation Date']).date()
                        
                        # Check if graduation date is in the future
                        if graduation_date > date.today():
                            errors.append(f"Row {row_num}: Graduation date cannot be in the future")
                        
                        # Check that graduation date is before bar date
                        if 'Bar Date' in row and not pd.isna(row['Bar Date']):
                            bar_date = pd.to_datetime(row['Bar Date']).date()
                            if graduation_date > bar_date:
                                errors.append(f"Row {row_num}: Graduation date should be before bar date")
                    except Exception:
                        errors.append(f"Row {row_num}: Invalid graduation date format")
                
                # Validate office
                if pd.isna(row['Office']):
                    errors.append(f"Row {row_num}: Office is required")
            
            except Exception as e:
                errors.append(f"Row {row_num}: Validation error: {str(e)}")
        
        # Update validation results
        if errors:
            validation_results["valid"] = False
            validation_results["errors"] = errors
        
        validation_results["warnings"] = warnings
    
    except ValidationError as e:
        validation_results["valid"] = False
        validation_results["errors"] = [str(e)]
    
    return validation_results


def validate_billing_import_data(df: pd.DataFrame, validation_rules: Dict = None) -> Dict:
    """
    Validates that billing import data meets business rules and data type requirements.
    
    Args:
        df: DataFrame containing billing data
        validation_rules: Dictionary of validation rules to apply
        
    Returns:
        Dictionary with validation results including warnings and errors
    """
    if validation_rules is None:
        validation_rules = {}
    
    validation_results = {"valid": True, "errors": [], "warnings": []}
    
    try:
        # Validate dataframe structure first
        validate_dataframe_structure(df, BILLING_IMPORT_REQUIRED_FIELDS, BILLING_IMPORT_OPTIONAL_FIELDS)
        
        # Validate data types and business rules
        errors = []
        warnings = []
        
        # Process each row
        for idx, row in df.iterrows():
            row_num = idx + 2  # +2 because idx is 0-based and we have a header row
            
            try:
                # Validate hours
                try:
                    hours = Decimal(str(row['Hours']))
                    
                    # Check for negative hours
                    if hours < 0:
                        errors.append(f"Row {row_num}: Hours cannot be negative")
                    
                    # Check for unusually high hours
                    if hours > 24:
                        warnings.append(f"Row {row_num}: Hours value {hours} seems unusually high")
                
                except (ValueError, TypeError, decimal.InvalidOperation):
                    errors.append(f"Row {row_num}: Invalid hours format")
                
                # Validate fees
                try:
                    fees = Decimal(str(row['Fees']))
                    
                    # Check for negative fees
                    if fees < 0:
                        errors.append(f"Row {row_num}: Fees cannot be negative")
                
                except (ValueError, TypeError, decimal.InvalidOperation):
                    errors.append(f"Row {row_num}: Invalid fees format")
                
                # Validate date
                try:
                    billing_date = pd.to_datetime(row['Date']).date()
                    
                    # Check if date is in the future
                    if billing_date > date.today():
                        errors.append(f"Row {row_num}: Billing date cannot be in the future")
                    
                    # Check if date is too old (over 10 years)
                    if billing_date < (date.today() - pd.DateOffset(years=10)).date():
                        warnings.append(f"Row {row_num}: Billing date is more than 10 years old")
                
                except Exception:
                    errors.append(f"Row {row_num}: Invalid date format")
                
                # Validate AFA flag if present
                if 'AFA Flag' in row and not pd.isna(row['AFA Flag']):
                    afa_flag = row['AFA Flag']
                    
                    # Convert to boolean if possible
                    if isinstance(afa_flag, bool):
                        pass  # Already a boolean
                    elif isinstance(afa_flag, str):
                        if afa_flag.lower() not in ('true', 'false', 'yes', 'no', '1', '0', 'y', 'n'):
                            errors.append(f"Row {row_num}: Invalid AFA Flag value: {afa_flag}")
                    else:
                        try:
                            # Try to convert to int and then check if 0 or 1
                            afa_int = int(afa_flag)
                            if afa_int not in (0, 1):
                                errors.append(f"Row {row_num}: Invalid AFA Flag value: {afa_flag}")
                        except (ValueError, TypeError):
                            errors.append(f"Row {row_num}: Invalid AFA Flag value: {afa_flag}")
                
                # Validate currency if present
                if 'Currency' in row and not pd.isna(row['Currency']):
                    try:
                        currency = str(row['Currency']).strip().upper()
                        if not validate_currency_code(currency, f"Row {row_num}: Currency"):
                            errors.append(f"Row {row_num}: Invalid currency code: {currency}")
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
            
            except Exception as e:
                errors.append(f"Row {row_num}: Validation error: {str(e)}")
        
        # Update validation results
        if errors:
            validation_results["valid"] = False
            validation_results["errors"] = errors
        
        validation_results["warnings"] = warnings
    
    except ValidationError as e:
        validation_results["valid"] = False
        validation_results["errors"] = [str(e)]
    
    return validation_results


def create_validation_error_report(validation_results: Dict, file_path: str) -> Dict:
    """
    Creates a detailed error report from validation results.
    
    Args:
        validation_results: Validation results from a validator function
        file_path: Path to the file that was validated
        
    Returns:
        Formatted error report with details by row and column
    """
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_extension = get_file_extension(file_path)
    
    report = {
        "file_info": {
            "name": file_name,
            "size": file_size,
            "size_formatted": f"{file_size / (1024 * 1024):.2f} MB",
            "type": file_extension
        },
        "validation_summary": {
            "valid": validation_results.get("valid", False),
            "error_count": len(validation_results.get("errors", [])),
            "warning_count": len(validation_results.get("warnings", []))
        },
        "errors": {},
        "warnings": validation_results.get("warnings", [])
    }
    
    # Group errors by row number if possible
    errors_by_row = {}
    for error in validation_results.get("errors", []):
        # Try to extract row number from error message
        import re
        row_match = re.search(r"Row (\d+):", error)
        if row_match:
            row_num = int(row_match.group(1))
            if row_num not in errors_by_row:
                errors_by_row[row_num] = []
            errors_by_row[row_num].append(error)
        else:
            # For errors without a row number, use "general"
            if "general" not in errors_by_row:
                errors_by_row["general"] = []
            errors_by_row["general"].append(error)
    
    report["errors"] = errors_by_row
    
    # Add suggestion for correction if there are errors
    if report["validation_summary"]["error_count"] > 0:
        report["suggestion"] = "Please fix the errors and reupload the file."
    
    # Add warning suggestion if there are warnings but no errors
    elif report["validation_summary"]["warning_count"] > 0:
        report["suggestion"] = "The file has been accepted, but please review the warnings."
    
    return report


def validate_import_mapping(mapping: Dict, source_columns: List, required_target_fields: List) -> Tuple[bool, List]:
    """
    Validates that a field mapping configuration maps all required fields correctly.
    
    Args:
        mapping: Dictionary mapping source columns to target fields
        source_columns: List of available source columns
        required_target_fields: List of required target fields
        
    Returns:
        Tuple containing success flag and list of validation issues
    """
    issues = []
    success = True
    
    # Check if all required target fields are mapped
    mapped_target_fields = set(mapping.values())
    missing_required_fields = [field for field in required_target_fields if field not in mapped_target_fields]
    
    if missing_required_fields:
        issues.append(f"Missing mappings for required fields: {', '.join(missing_required_fields)}")
        success = False
    
    # Check if all source columns in the mapping exist in the source
    for source_col in mapping.keys():
        if source_col not in source_columns:
            issues.append(f"Source column '{source_col}' in mapping does not exist in the source file")
            success = False
    
    # Check for duplicate target fields
    target_field_counts = {}
    for target_field in mapping.values():
        if target_field not in target_field_counts:
            target_field_counts[target_field] = 0
        target_field_counts[target_field] += 1
    
    duplicate_fields = [field for field, count in target_field_counts.items() if count > 1]
    if duplicate_fields:
        issues.append(f"Target fields mapped multiple times: {', '.join(duplicate_fields)}")
        success = False
    
    return success, issues


def identify_potential_fields(df: pd.DataFrame, target_fields: List) -> Dict:
    """
    Identifies potential field mappings based on column names and data analysis.
    
    Args:
        df: DataFrame with the source data
        target_fields: List of target fields to map to
        
    Returns:
        Dictionary of suggested mappings with confidence scores
    """
    suggestions = {}
    
    # Create lowercase versions for case-insensitive matching
    lowercase_columns = {col.lower(): col for col in df.columns}
    lowercase_targets = [field.lower() for field in target_fields]
    
    # First check for exact matches (case-insensitive)
    for target_field in target_fields:
        target_lower = target_field.lower()
        if target_lower in lowercase_columns:
            suggestions[target_field] = {
                "suggested_column": lowercase_columns[target_lower],
                "confidence": 1.0,
                "rationale": "Exact match"
            }
    
    # Check for partial matches for fields not yet matched
    remaining_targets = [field for field in target_fields if field not in suggestions]
    
    for target_field in remaining_targets:
        target_lower = target_field.lower()
        best_match = None
        best_confidence = 0.0
        
        # Split target field into words
        target_words = set(target_lower.split())
        
        for column in df.columns:
            # Skip already mapped columns
            if any(suggestion["suggested_column"] == column for suggestion in suggestions.values()):
                continue
            
            column_lower = column.lower()
            
            # Check for target field as a substring of column
            if target_lower in column_lower:
                confidence = 0.8
                rationale = "Target is substring of column"
            # Check for column as a substring of target field
            elif column_lower in target_lower:
                confidence = 0.7
                rationale = "Column is substring of target"
            # Check for word overlap
            else:
                column_words = set(column_lower.split())
                overlap = target_words.intersection(column_words)
                
                if overlap:
                    # Calculate confidence based on overlap ratio
                    overlap_ratio = len(overlap) / max(len(target_words), len(column_words))
                    confidence = 0.5 + (0.3 * overlap_ratio)
                    rationale = f"Word overlap: {', '.join(overlap)}"
                else:
                    confidence = 0.0
                    rationale = "No match"
            
            # Update best match if we found a better one
            if confidence > best_confidence:
                best_match = column
                best_confidence = confidence
                best_rationale = rationale
        
        # Add suggestion if confidence is above threshold
        if best_match and best_confidence > 0.3:
            suggestions[target_field] = {
                "suggested_column": best_match,
                "confidence": best_confidence,
                "rationale": best_rationale
            }
    
    # Try data type analysis for fields that still have no match
    remaining_targets = [field for field in target_fields if field not in suggestions]
    
    data_type_mappings = {
        "Date": {"date", "time", "period"},
        "Amount": {"amount", "fee", "rate", "value", "cost"},
        "Currency": {"currency", "code"},
        "Name": {"name", "attorney", "firm", "client", "person"},
        "ID": {"id", "identifier", "code", "number"}
    }
    
    for target_field in remaining_targets:
        target_lower = target_field.lower()
        target_type = None
        
        # Determine target field type
        for type_name, keywords in data_type_mappings.items():
            if any(keyword in target_lower for keyword in keywords):
                target_type = type_name
                break
        
        if not target_type:
            continue
        
        # Find columns of similar type
        candidates = []
        
        for column in df.columns:
            # Skip already mapped columns
            if any(suggestion["suggested_column"] == column for suggestion in suggestions.values()):
                continue
            
            # Check for type compatibility
            if target_type == "Date" and pd.api.types.is_datetime64_any_dtype(df[column]):
                confidence = 0.6
                rationale = "Date type match"
                candidates.append((column, confidence, rationale))
            elif target_type == "Amount" and pd.api.types.is_numeric_dtype(df[column]):
                confidence = 0.5
                rationale = "Numeric type match"
                candidates.append((column, confidence, rationale))
            elif target_type == "Name" and pd.api.types.is_string_dtype(df[column]):
                # Check for name-like data (capitalized words)
                if df[column].astype(str).str.match(r'^[A-Z][a-z]*(\s+[A-Z][a-z]*)*$').mean() > 0.7:
                    confidence = 0.5
                    rationale = "Name pattern match"
                    candidates.append((column, confidence, rationale))
        
        # Add best candidate as suggestion
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_candidate = candidates[0]
            
            suggestions[target_field] = {
                "suggested_column": best_candidate[0],
                "confidence": best_candidate[1],
                "rationale": best_candidate[2]
            }
    
    return suggestions


def validate_date_columns(df: pd.DataFrame, date_columns: List, date_formats: List = None) -> Dict:
    """
    Validates that dataframe columns containing dates have proper format.
    
    Args:
        df: DataFrame to validate
        date_columns: List of column names containing dates
        date_formats: List of date formats to try
        
    Returns:
        Dictionary with validation results with error details by column and row
    """
    if date_formats is None:
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']
    
    results = {
        "valid": True,
        "errors": {},
        "parsed_dates": {}
    }
    
    for column in date_columns:
        if column not in df.columns:
            continue
        
        column_errors = []
        parsed_dates = []
        
        for idx, value in enumerate(df[column]):
            if pd.isna(value):
                parsed_dates.append(None)
                continue
            
            row_num = idx + 2  # +2 for 0-based index and header row
            success = False
            
            # Try parsing with pandas first
            try:
                parsed_date = pd.to_datetime(value)
                parsed_dates.append(parsed_date.date())
                success = True
            except:
                # Try each format manually
                for date_format in date_formats:
                    try:
                        if isinstance(value, str):
                            parsed_date = datetime.strptime(value, date_format).date()
                            parsed_dates.append(parsed_date)
                            success = True
                            break
                    except:
                        continue
            
            if not success:
                column_errors.append((row_num, value))
                parsed_dates.append(None)
        
        if column_errors:
            results["valid"] = False
            results["errors"][column] = column_errors
        
        results["parsed_dates"][column] = parsed_dates
    
    return results


def validate_numeric_columns(df: pd.DataFrame, numeric_columns: List, constraints: Dict = None) -> Dict:
    """
    Validates that dataframe columns containing numeric values have proper format.
    
    Args:
        df: DataFrame to validate
        numeric_columns: List of column names containing numeric values
        constraints: Dictionary of constraints for each column
        
    Returns:
        Dictionary with validation results with error details by column and row
    """
    if constraints is None:
        constraints = {}
    
    results = {
        "valid": True,
        "errors": {},
        "parsed_values": {}
    }
    
    for column in numeric_columns:
        if column not in df.columns:
            continue
        
        column_errors = []
        parsed_values = []
        
        column_constraints = constraints.get(column, {})
        min_value = column_constraints.get('min_value')
        max_value = column_constraints.get('max_value')
        decimals = column_constraints.get('decimals')
        allow_negative = column_constraints.get('allow_negative', False)
        
        for idx, value in enumerate(df[column]):
            if pd.isna(value):
                parsed_values.append(None)
                continue
            
            row_num = idx + 2  # +2 for 0-based index and header row
            
            try:
                numeric_value = Decimal(str(value))
                
                # Check constraints
                if min_value is not None and numeric_value < min_value:
                    column_errors.append((row_num, value, f"Value below minimum ({min_value})"))
                
                if max_value is not None and numeric_value > max_value:
                    column_errors.append((row_num, value, f"Value above maximum ({max_value})"))
                
                if decimals is not None:
                    decimal_tuple = numeric_value.as_tuple()
                    if decimal_tuple.exponent < 0 and abs(decimal_tuple.exponent) > decimals:
                        column_errors.append((row_num, value, f"Too many decimal places (max {decimals})"))
                
                if not allow_negative and numeric_value < 0:
                    column_errors.append((row_num, value, "Negative values not allowed"))
                
                parsed_values.append(numeric_value)
            
            except (ValueError, TypeError, decimal.InvalidOperation):
                column_errors.append((row_num, value, "Invalid numeric format"))
                parsed_values.append(None)
        
        if column_errors:
            results["valid"] = False
            results["errors"][column] = column_errors
        
        results["parsed_values"][column] = parsed_values
    
    return results


class FileValidator:
    """
    Main class for validating file imports with comprehensive validation options.
    """
    
    def __init__(self):
        """
        Initialize the FileValidator with default validators and validation rules.
        """
        # Initialize validators dictionary
        self._validators = {
            'csv': {},
            'excel': {},
        }
        
        # Initialize validation rules for different import types
        self._validation_rules = {
            'rate': {},
            'attorney': {},
            'billing': {}
        }
        
        # Register default validators
        self.register_validator('csv', 'rate', validate_rate_import_data)
        self.register_validator('csv', 'attorney', validate_attorney_import_data)
        self.register_validator('csv', 'billing', validate_billing_import_data)
        self.register_validator('excel', 'rate', validate_rate_import_data)
        self.register_validator('excel', 'attorney', validate_attorney_import_data)
        self.register_validator('excel', 'billing', validate_billing_import_data)
        
        logger.info("FileValidator initialized with default validators")
    
    def register_validator(self, file_type: str, import_type: str, validator_function: callable):
        """
        Registers a validator function for a specific file type and import type.
        
        Args:
            file_type: The file type ('csv', 'excel')
            import_type: The import type ('rate', 'attorney', 'billing')
            validator_function: The validator function to register
        """
        if file_type not in self._validators:
            self._validators[file_type] = {}
        
        self._validators[file_type][import_type] = validator_function
        logger.debug(f"Registered validator for {file_type}/{import_type}")
    
    def set_validation_rule(self, import_type: str, rule_name: str, rule_value: Any):
        """
        Sets a validation rule for a specific import type.
        
        Args:
            import_type: The import type ('rate', 'attorney', 'billing')
            rule_name: The name of the rule to set
            rule_value: The value for the rule
        """
        if import_type not in self._validation_rules:
            self._validation_rules[import_type] = {}
        
        self._validation_rules[import_type][rule_name] = rule_value
        logger.debug(f"Set validation rule {rule_name} for {import_type}")
    
    def validate_file(self, file_path: str, file_type: str = None, import_type: str = None, options: Dict = None) -> Dict:
        """
        Validates a file against registered validators for its type and import type.
        
        Args:
            file_path: Path to the file to validate
            file_type: Type of file ('csv', 'excel')
            import_type: Type of import ('rate', 'attorney', 'billing')
            options: Dictionary of validation options
            
        Returns:
            Dictionary with validation results
        """
        if options is None:
            options = {}
        
        # Determine file type from extension if not provided
        if file_type is None:
            extension = get_file_extension(file_path)
            if extension in CSV_ALLOWED_EXTENSIONS:
                file_type = 'csv'
            elif extension in EXCEL_ALLOWED_EXTENSIONS:
                file_type = 'excel'
            else:
                raise ValidationError(f"Unsupported file type: {extension}")
        
        # Check if we have a validator for this file type and import type
        if file_type not in self._validators:
            raise ValidationError(f"No validators registered for file type: {file_type}")
        
        if import_type and import_type not in self._validators[file_type]:
            raise ValidationError(f"No validators registered for import type: {import_type}")
        
        try:
            # First validate the file format
            if file_type == 'csv':
                validate_csv_file(file_path, options)
                df = pd.read_csv(file_path)
            elif file_type == 'excel':
                validate_excel_file(file_path, options)
                sheet_name = options.get('sheet_name', 0)
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                raise ValidationError(f"Unsupported file type: {file_type}")
            
            # Now apply the appropriate validator for the import type
            if import_type:
                validator_func = self._validators[file_type][import_type]
                validation_rules = self._validation_rules.get(import_type, {})
                validation_results = validator_func(df, validation_rules)
            else:
                # If no import type specified, just return success for format validation
                validation_results = {"valid": True, "errors": [], "warnings": []}
            
            # Create detailed error report if needed
            if not validation_results["valid"] or validation_results.get("warnings"):
                validation_results["report"] = create_validation_error_report(validation_results, file_path)
            
            return validation_results
            
        except ValidationError as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "report": create_validation_error_report(
                    {"valid": False, "errors": [str(e)], "warnings": []},
                    file_path
                )
            }
    
    def validate_dataframe(self, df: pd.DataFrame, import_type: str, options: Dict = None) -> Dict:
        """
        Validates a DataFrame directly without file I/O.
        
        Args:
            df: DataFrame to validate
            import_type: Type of import ('rate', 'attorney', 'billing')
            options: Dictionary of validation options
            
        Returns:
            Dictionary with validation results
        """
        if options is None:
            options = {}
        
        if import_type not in self._validation_rules:
            raise ValidationError(f"Unknown import type: {import_type}")
        
        try:
            if import_type == 'rate':
                validation_results = validate_rate_import_data(df, self._validation_rules.get('rate', {}))
            elif import_type == 'attorney':
                validation_results = validate_attorney_import_data(df, self._validation_rules.get('attorney', {}))
            elif import_type == 'billing':
                validation_results = validate_billing_import_data(df, self._validation_rules.get('billing', {}))
            else:
                raise ValidationError(f"Unsupported import type: {import_type}")
            
            return validation_results
            
        except ValidationError as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    def get_validation_rules(self, import_type: str) -> Dict:
        """
        Gets the current validation rules for an import type.
        
        Args:
            import_type: The import type ('rate', 'attorney', 'billing')
            
        Returns:
            Dictionary of current validation rules
        """
        if import_type in self._validation_rules:
            return dict(self._validation_rules[import_type])
        return {}
    
    def reset_validation_rules(self, import_type: str):
        """
        Resets validation rules to defaults for an import type.
        
        Args:
            import_type: The import type ('rate', 'attorney', 'billing')
        """
        if import_type in self._validation_rules:
            self._validation_rules[import_type] = {}
            logger.debug(f"Reset validation rules for {import_type}")