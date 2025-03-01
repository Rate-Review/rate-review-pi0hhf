"""
Core validation utility module providing reusable validation functions for data input validation
across the Justice Bid Rate Negotiation System. These validators ensure data integrity,
enforce business rules, and provide consistent error handling for API requests,
file imports, and database operations.
"""

import re
import uuid
from typing import Any, Dict, List, Optional, Union, Callable
from decimal import Decimal
from datetime import date, datetime
from email_validator import validate_email as validate_email_rfc, EmailNotValidError

from .constants import (
    PASSWORD_MIN_LENGTH,
    SUPPORTED_FILE_FORMATS,
    MAX_FILE_SIZE_MB,
    RateStatus,
    RateType,
    NegotiationStatus
)
from .datetime_utils import is_valid_date_format, parse_date, is_date_between
from .currency import is_valid_currency, SUPPORTED_CURRENCIES
from ..api.core.errors import ValidationError

# Regular expression patterns for common validations
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
URL_REGEX = re.compile(r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)$')
PHONE_REGEX = re.compile(r'^\+?[0-9]{1,3}?[-.\s]?\(?[0-9]{1,3}\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}$')
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
UUID_REGEX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
PASSWORD_COMPLEXITY_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\W]{12,}$')


def validate_required(value: Any, field_name: str) -> bool:
    """
    Validates that a required value is not None or empty.
    
    Args:
        value: Value to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if value is None:
        raise ValidationError(f"{field_name} is required and cannot be None")
    
    # Check for empty strings, lists, or dicts
    if isinstance(value, (str, list, dict)) and len(value) == 0:
        raise ValidationError(f"{field_name} is required and cannot be empty")
    
    return True


def validate_string(value: str, field_name: str, min_length: Optional[int] = None, 
                   max_length: Optional[int] = None) -> bool:
    """
    Validates a string value against maximum and minimum length constraints.
    
    Args:
        value: String value to validate
        field_name: Name of the field being validated
        min_length: Optional minimum length
        max_length: Optional maximum length
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    if min_length is not None and len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters long")
    
    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"{field_name} cannot exceed {max_length} characters")
    
    return True


def validate_number(value: Union[int, float, Decimal], field_name: str, 
                   min_value: Optional[Union[int, float, Decimal]] = None, 
                   max_value: Optional[Union[int, float, Decimal]] = None, 
                   allow_zero: bool = True) -> bool:
    """
    Validates a numeric value against minimum and maximum constraints.
    
    Args:
        value: Numeric value to validate
        field_name: Name of the field being validated
        min_value: Optional minimum allowed value
        max_value: Optional maximum allowed value
        allow_zero: Whether to allow zero as a valid value
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, (int, float, Decimal)):
        raise ValidationError(f"{field_name} must be a number")
    
    if value == 0 and not allow_zero:
        raise ValidationError(f"{field_name} cannot be zero")
    
    if min_value is not None and value < min_value:
        raise ValidationError(f"{field_name} must be greater than or equal to {min_value}")
    
    if max_value is not None and value > max_value:
        raise ValidationError(f"{field_name} must be less than or equal to {max_value}")
    
    return True


def validate_integer(value: Any, field_name: str, 
                    min_value: Optional[int] = None, 
                    max_value: Optional[int] = None) -> bool:
    """
    Validates that a value is an integer within specified range.
    
    Args:
        value: Value to validate
        field_name: Name of the field being validated
        min_value: Optional minimum allowed value
        max_value: Optional maximum allowed value
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(f"{field_name} must be an integer")
    
    # Validate range using validate_number
    return validate_number(value, field_name, min_value, max_value, allow_zero=True)


def validate_decimal(value: Any, field_name: str, 
                    min_value: Optional[Decimal] = None, 
                    max_value: Optional[Decimal] = None,
                    max_decimal_places: Optional[int] = None) -> bool:
    """
    Validates that a value is a decimal number within specified range and precision.
    
    Args:
        value: Value to validate
        field_name: Name of the field being validated
        min_value: Optional minimum allowed value
        max_value: Optional maximum allowed value
        max_decimal_places: Optional maximum decimal places
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    # Convert to Decimal if not already
    try:
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
    except (ValueError, TypeError, decimal.InvalidOperation):
        raise ValidationError(f"{field_name} must be a valid decimal number")
    
    # Check decimal places if specified
    if max_decimal_places is not None:
        decimal_tuple = value.as_tuple()
        if decimal_tuple.exponent < 0 and -decimal_tuple.exponent > max_decimal_places:
            raise ValidationError(f"{field_name} cannot have more than {max_decimal_places} decimal places")
    
    # Validate range using validate_number
    return validate_number(value, field_name, min_value, max_value, allow_zero=True)


def validate_boolean(value: Any, field_name: str) -> bool:
    """
    Validates that a value is a boolean.
    
    Args:
        value: Value to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, bool):
        raise ValidationError(f"{field_name} must be a boolean (true or false)")
    
    return True


def validate_list(value: Any, field_name: str, 
                 min_length: Optional[int] = None, 
                 max_length: Optional[int] = None,
                 item_validator: Optional[callable] = None) -> bool:
    """
    Validates that a value is a list with optional length constraints.
    
    Args:
        value: Value to validate
        field_name: Name of the field being validated
        min_length: Optional minimum list length
        max_length: Optional maximum list length
        item_validator: Optional function to validate each item in the list
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, list):
        raise ValidationError(f"{field_name} must be a list")
    
    if min_length is not None and len(value) < min_length:
        raise ValidationError(f"{field_name} must contain at least {min_length} items")
    
    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"{field_name} cannot contain more than {max_length} items")
    
    if item_validator and callable(item_validator):
        errors = []
        for i, item in enumerate(value):
            try:
                item_validator(item, f"{field_name}[{i}]")
            except ValidationError as e:
                errors.append(f"Item {i}: {str(e)}")
        
        if errors:
            raise ValidationError(f"Validation failed for items in {field_name}: {'; '.join(errors)}")
    
    return True


def validate_dict(value: Any, field_name: str, 
                 required_keys: Optional[List] = None, 
                 optional_keys: Optional[List] = None) -> bool:
    """
    Validates that a value is a dictionary with optional key validation.
    
    Args:
        value: Value to validate
        field_name: Name of the field being validated
        required_keys: List of keys that must be present
        optional_keys: List of keys that may be present
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, dict):
        raise ValidationError(f"{field_name} must be a dictionary")
    
    if required_keys:
        missing_keys = [key for key in required_keys if key not in value]
        if missing_keys:
            raise ValidationError(f"{field_name} is missing required keys: {', '.join(missing_keys)}")
    
    if required_keys or optional_keys:
        allowed_keys = set((required_keys or []) + (optional_keys or []))
        extra_keys = [key for key in value.keys() if key not in allowed_keys]
        if extra_keys:
            raise ValidationError(f"{field_name} contains unrecognized keys: {', '.join(extra_keys)}")
    
    return True


def validate_email(value: str, field_name: str) -> bool:
    """
    Validates that a value is a properly formatted email address.
    
    Args:
        value: Email address to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    try:
        # Use email_validator for RFC-compliant validation
        validate_email_rfc(value)
        return True
    except EmailNotValidError as e:
        raise ValidationError(f"{field_name} is not a valid email address: {str(e)}")


def validate_url(value: str, field_name: str) -> bool:
    """
    Validates that a value is a properly formatted URL.
    
    Args:
        value: URL to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    if not URL_REGEX.match(value):
        raise ValidationError(f"{field_name} is not a valid URL")
    
    return True


def validate_phone(value: str, field_name: str) -> bool:
    """
    Validates that a value is a properly formatted phone number.
    
    Args:
        value: Phone number to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    if not PHONE_REGEX.match(value):
        raise ValidationError(f"{field_name} is not a valid phone number")
    
    return True


def validate_uuid(value: str, field_name: str) -> bool:
    """
    Validates that a value is a properly formatted UUID.
    
    Args:
        value: UUID string to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        raise ValidationError(f"{field_name} is not a valid UUID")


def validate_date(value: Union[str, date, datetime], field_name: str, 
                 min_date: Optional[date] = None, 
                 max_date: Optional[date] = None,
                 date_formats: Optional[List] = None) -> bool:
    """
    Validates that a value is a properly formatted date string or date object.
    
    Args:
        value: Date to validate
        field_name: Name of the field being validated
        min_date: Optional minimum date
        max_date: Optional maximum date
        date_formats: Optional list of date formats to try
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    date_obj = None
    
    # Handle string dates
    if isinstance(value, str):
        try:
            date_obj = parse_date(value, date_formats[0] if date_formats else None)
        except ValueError as e:
            formats_str = ", ".join(date_formats) if date_formats else "standard date format"
            raise ValidationError(f"{field_name} is not a valid date. Expected format: {formats_str}")
    
    # Handle datetime objects
    elif isinstance(value, datetime):
        date_obj = value.date()
    
    # Handle date objects
    elif isinstance(value, date):
        date_obj = value
    
    else:
        raise ValidationError(f"{field_name} must be a date, datetime, or date string")
    
    # Validate min_date and max_date if provided
    if min_date is not None and date_obj < min_date:
        raise ValidationError(f"{field_name} must be on or after {min_date}")
    
    if max_date is not None and date_obj > max_date:
        raise ValidationError(f"{field_name} must be on or before {max_date}")
    
    return True


def validate_future_date(value: Union[str, date, datetime], field_name: str, 
                        allow_today: bool = True) -> bool:
    """
    Validates that a date is in the future.
    
    Args:
        value: Date to validate
        field_name: Name of the field being validated
        allow_today: Whether to allow today's date
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    today = date.today()
    
    # First validate it's a valid date
    validate_date(value, field_name)
    
    # Convert to date object if it's a string or datetime
    if isinstance(value, str):
        date_obj = parse_date(value)
    elif isinstance(value, datetime):
        date_obj = value.date()
    else:
        date_obj = value
    
    # Check if date is in the future
    if allow_today:
        if date_obj < today:
            raise ValidationError(f"{field_name} must be today or in the future")
    else:
        if date_obj <= today:
            raise ValidationError(f"{field_name} must be in the future")
    
    return True


def validate_past_date(value: Union[str, date, datetime], field_name: str, 
                      allow_today: bool = True) -> bool:
    """
    Validates that a date is in the past.
    
    Args:
        value: Date to validate
        field_name: Name of the field being validated
        allow_today: Whether to allow today's date
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    today = date.today()
    
    # First validate it's a valid date
    validate_date(value, field_name)
    
    # Convert to date object if it's a string or datetime
    if isinstance(value, str):
        date_obj = parse_date(value)
    elif isinstance(value, datetime):
        date_obj = value.date()
    else:
        date_obj = value
    
    # Check if date is in the past
    if allow_today:
        if date_obj > today:
            raise ValidationError(f"{field_name} must be today or in the past")
    else:
        if date_obj >= today:
            raise ValidationError(f"{field_name} must be in the past")
    
    return True


def validate_date_range(start_date: Union[str, date, datetime], 
                       end_date: Union[str, date, datetime],
                       start_field_name: str, 
                       end_field_name: str,
                       allow_equal: bool = True) -> bool:
    """
    Validates that an end date comes after a start date.
    
    Args:
        start_date: Start date
        end_date: End date
        start_field_name: Name of the start date field
        end_field_name: Name of the end date field
        allow_equal: Whether to allow start and end dates to be equal
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    # Validate both dates individually
    validate_date(start_date, start_field_name)
    validate_date(end_date, end_field_name)
    
    # Convert to date objects if they're strings or datetimes
    if isinstance(start_date, str):
        start_date_obj = parse_date(start_date)
    elif isinstance(start_date, datetime):
        start_date_obj = start_date.date()
    else:
        start_date_obj = start_date
    
    if isinstance(end_date, str):
        end_date_obj = parse_date(end_date)
    elif isinstance(end_date, datetime):
        end_date_obj = end_date.date()
    else:
        end_date_obj = end_date
    
    # Check if end date is after start date
    if allow_equal:
        if end_date_obj < start_date_obj:
            raise ValidationError(f"{end_field_name} must be on or after {start_field_name}")
    else:
        if end_date_obj <= start_date_obj:
            raise ValidationError(f"{end_field_name} must be after {start_field_name}")
    
    return True


def validate_enum_value(value: Any, enum_class, field_name: str) -> bool:
    """
    Validates that a value is a member of an enumeration.
    
    Args:
        value: Value to validate
        enum_class: Enumeration class to validate against
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    try:
        enum_class(value)
        return True
    except ValueError:
        valid_values = ", ".join([e.value for e in enum_class])
        raise ValidationError(f"{field_name} must be one of: {valid_values}")


def validate_rate_status(value: str, field_name: str) -> bool:
    """
    Validates that a value is a valid rate status.
    
    Args:
        value: Rate status to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    return validate_enum_value(value, RateStatus, field_name)


def validate_rate_type(value: str, field_name: str) -> bool:
    """
    Validates that a value is a valid rate type.
    
    Args:
        value: Rate type to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    return validate_enum_value(value, RateType, field_name)


def validate_negotiation_status(value: str, field_name: str) -> bool:
    """
    Validates that a value is a valid negotiation status.
    
    Args:
        value: Negotiation status to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    return validate_enum_value(value, NegotiationStatus, field_name)


def validate_password(value: str, field_name: str) -> bool:
    """
    Validates that a password meets complexity requirements.
    
    Args:
        value: Password to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    if len(value) < PASSWORD_MIN_LENGTH:
        raise ValidationError(f"{field_name} must be at least {PASSWORD_MIN_LENGTH} characters long")
    
    if not PASSWORD_COMPLEXITY_REGEX.match(value):
        raise ValidationError(
            f"{field_name} must contain at least one uppercase letter, "
            f"one lowercase letter, and one number"
        )
    
    return True


def validate_currency_code(value: str, field_name: str) -> bool:
    """
    Validates that a value is a supported currency code.
    
    Args:
        value: Currency code to validate
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    if not is_valid_currency(value):
        supported = ", ".join(SUPPORTED_CURRENCIES)
        raise ValidationError(f"{field_name} must be a supported currency code. Supported currencies: {supported}")
    
    return True


def validate_rate_value(value: Union[str, float, Decimal], field_name: str, 
                       currency_code: str, 
                       min_value: Optional[Decimal] = None, 
                       max_value: Optional[Decimal] = None) -> bool:
    """
    Validates a rate value based on currency-specific rules.
    
    Args:
        value: Rate value to validate
        field_name: Name of the field being validated
        currency_code: Currency code for the rate
        min_value: Optional minimum value
        max_value: Optional maximum value
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    # Validate currency code first
    validate_currency_code(currency_code, f"{field_name}_currency")
    
    # Convert value to Decimal if it's not already
    try:
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
    except (ValueError, TypeError, decimal.InvalidOperation):
        raise ValidationError(f"{field_name} must be a valid numeric value")
    
    # Get currency-specific min/max values if not provided
    if min_value is None:
        # Most currencies should not allow negative rates
        min_value = Decimal('0')
    
    # Get currency-specific precision
    currency_decimal_places = 0 if currency_code.upper() == 'JPY' else 2
    
    # Validate using validate_decimal with currency-specific decimal places
    return validate_decimal(
        value, 
        field_name, 
        min_value=min_value, 
        max_value=max_value, 
        max_decimal_places=currency_decimal_places
    )


def validate_rate_increase(old_rate: Decimal, new_rate: Decimal, 
                          max_increase_percent: Decimal, field_name: str) -> bool:
    """
    Validates that a rate increase percentage is within allowed limits.
    
    Args:
        old_rate: Previous rate value
        new_rate: New rate value
        max_increase_percent: Maximum allowed percentage increase
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if old_rate <= 0:
        raise ValidationError("Previous rate must be greater than zero")
    
    # Calculate percentage increase
    increase_percent = ((new_rate - old_rate) / old_rate) * Decimal('100')
    
    # Check if increase is within limits
    if increase_percent > max_increase_percent:
        raise ValidationError(
            f"{field_name} increase of {increase_percent:.2f}% exceeds maximum allowed increase of {max_increase_percent}%"
        )
    
    return True


def validate_file_extension(filename: str, allowed_extensions: Optional[list] = None) -> bool:
    """
    Validates that a file has an allowed extension.
    
    Args:
        filename: Name of the file to validate
        allowed_extensions: List of allowed file extensions
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = SUPPORTED_FILE_FORMATS
    
    # Get file extension
    try:
        extension = filename.rsplit('.', 1)[1].lower()
    except IndexError:
        raise ValidationError(f"File '{filename}' has no extension")
    
    if extension not in allowed_extensions:
        raise ValidationError(f"File extension '{extension}' is not supported. Allowed extensions: {', '.join(allowed_extensions)}")
    
    return True


def validate_file_size(file_size_bytes: int, max_size_mb: Optional[int] = None) -> bool:
    """
    Validates that a file size is within allowed limits.
    
    Args:
        file_size_bytes: Size of the file in bytes
        max_size_mb: Maximum allowed size in megabytes
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    if max_size_mb is None:
        max_size_mb = MAX_FILE_SIZE_MB
    
    # Convert MB to bytes
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size_bytes > max_size_bytes:
        raise ValidationError(f"File size ({file_size_bytes / (1024 * 1024):.2f} MB) exceeds maximum allowed size of {max_size_mb} MB")
    
    return True


def validate_json_schema(data: dict, schema: dict, field_name: str) -> bool:
    """
    Validates a JSON object against a JSON schema.
    
    Args:
        data: JSON data to validate
        schema: JSON schema to validate against
        field_name: Name of the field being validated
        
    Returns:
        True if validation passes, raises ValidationError otherwise
    """
    try:
        import jsonschema
        jsonschema.validate(data, schema)
        return True
    except ImportError:
        raise ValidationError("JSON schema validation requires the jsonschema package")
    except jsonschema.ValidationError as e:
        raise ValidationError(f"JSON schema validation failed for {field_name}: {e.message}")


def validate_all(value: Any, field_name: str, validators: list) -> bool:
    """
    Runs multiple validators on a value and aggregates errors.
    
    Args:
        value: Value to validate
        field_name: Name of the field being validated
        validators: List of validator functions to apply
        
    Returns:
        True if all validations pass, raises ValidationError with aggregated errors otherwise
    """
    errors = []
    
    for validator in validators:
        try:
            validator(value, field_name)
        except ValidationError as e:
            errors.append(str(e))
    
    if errors:
        raise ValidationError(f"Validation failed for {field_name}: {'; '.join(errors)}")
    
    return True


class ValidationResult:
    """
    Class representing the result of a validation operation.
    
    This class helps track and manage multiple validation errors and can be
    used for comprehensive validation across multiple fields.
    """
    
    def __init__(self, is_valid: bool = True, errors: Optional[list] = None):
        """
        Initialize a new ValidationResult.
        
        Args:
            is_valid: Whether the validation passed
            errors: List of error messages
        """
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, message: str) -> None:
        """
        Add an error message to the result.
        
        Args:
            message: Error message to add
        """
        self.errors.append(message)
        self.is_valid = False
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """
        Merge another ValidationResult into this one.
        
        Args:
            other: Another ValidationResult to merge
            
        Returns:
            Self after merging
        """
        if not other.is_valid:
            self.is_valid = False
            self.errors.extend(other.errors)
        return self
    
    def raise_if_invalid(self) -> bool:
        """
        Raise ValidationError if the result is invalid.
        
        Returns:
            True if valid, raises ValidationError otherwise
        """
        if not self.is_valid:
            raise ValidationError("; ".join(self.errors))
        return True