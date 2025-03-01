"""
Unit tests for validator utility functions used throughout the Justice Bid Rate Negotiation System
to ensure data integrity for rate submissions, negotiations, and approvals.
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock

from utils.validators import (
    validate_rate,
    validate_email,
    validate_date_range,
    validate_currency_code,
    validate_file_extension,
    validate_negotiation_status,
    validate_unique_constraint,
    validate_rate_increase,
    validate_staff_class,
    ValidationError
)
from utils.constants import (
    NEGOTIATION_STATUSES,
    SUPPORTED_CURRENCIES,
    ALLOWED_FILE_EXTENSIONS
)


@pytest.mark.parametrize('rate, currency', [
    (100, 'USD'),
    (150.50, 'EUR'),
    (Decimal('200.75'), 'GBP'),
    (0, 'USD')
])
def test_validate_rate_valid(rate, currency):
    """Tests the validate_rate function with valid rate values"""
    # No exception should be raised for valid rates
    validate_rate(rate, currency)


@pytest.mark.parametrize('rate, currency, expected_message', [
    (-100, 'USD', 'Rate must be a non-negative number'),
    (100, 'INVALID', 'Currency code INVALID is not supported'),
    ('not-a-number', 'USD', 'Rate must be a numeric value')
])
def test_validate_rate_invalid(rate, currency, expected_message):
    """Tests the validate_rate function with invalid rate values"""
    with pytest.raises(ValidationError) as excinfo:
        validate_rate(rate, currency)
    assert expected_message in str(excinfo.value)


@pytest.mark.parametrize('email', [
    'user@example.com',
    'first.last@example.co.uk',
    'user+tag@domain.org'
])
def test_validate_email_valid(email):
    """Tests the validate_email function with valid email addresses"""
    # No exception should be raised for valid email addresses
    validate_email(email)


@pytest.mark.parametrize('email, expected_message', [
    ('user@', 'Invalid email format'),
    ('user@.com', 'Invalid email format'),
    ('@domain.com', 'Invalid email format'),
    ('', 'Email cannot be empty')
])
def test_validate_email_invalid(email, expected_message):
    """Tests the validate_email function with invalid email addresses"""
    with pytest.raises(ValidationError) as excinfo:
        validate_email(email)
    assert expected_message in str(excinfo.value)


def test_validate_date_range_valid():
    """Tests the validate_date_range function with valid date ranges"""
    start_date = date.today()
    end_date = start_date + timedelta(days=30)
    
    # No exception should be raised for valid date range
    validate_date_range(start_date, end_date)


def test_validate_date_range_invalid():
    """Tests the validate_date_range function with invalid date ranges"""
    start_date = date.today()
    end_date = start_date - timedelta(days=5)  # End date is before start date
    
    with pytest.raises(ValidationError) as excinfo:
        validate_date_range(start_date, end_date)
    assert "End date must be after start date" in str(excinfo.value)


def test_validate_date_range_equal_dates():
    """Tests the validate_date_range function with equal start and end dates"""
    same_date = date.today()
    
    # Should not raise an exception when allow_equal is True
    validate_date_range(same_date, same_date, allow_equal=True)
    
    # Should raise an exception when allow_equal is False
    with pytest.raises(ValidationError) as excinfo:
        validate_date_range(same_date, same_date, allow_equal=False)
    assert "End date must be after start date" in str(excinfo.value)


@pytest.mark.parametrize('currency', [
    'USD', 'EUR', 'GBP', 'JPY'
])
def test_validate_currency_code_valid(currency):
    """Tests the validate_currency_code function with valid currency codes"""
    # No exception should be raised for valid currency codes
    validate_currency_code(currency)


@pytest.mark.parametrize('currency, expected_message', [
    ('INVALID', 'Currency code INVALID is not supported'),
    ('', 'Currency code cannot be empty'),
    (None, 'Currency code cannot be None')
])
def test_validate_currency_code_invalid(currency, expected_message):
    """Tests the validate_currency_code function with invalid currency codes"""
    with pytest.raises(ValidationError) as excinfo:
        validate_currency_code(currency)
    assert expected_message in str(excinfo.value)


@pytest.mark.parametrize('filename', [
    'data.csv',
    'rates.xlsx',
    'document.pdf',
    'backup.zip'
])
def test_validate_file_extension_valid(filename):
    """Tests the validate_file_extension function with valid file extensions"""
    # No exception should be raised for valid file extensions
    validate_file_extension(filename)


@pytest.mark.parametrize('filename, expected_message', [
    ('script.exe', 'File extension .exe is not allowed'),
    ('data', 'File must have an extension'),
    ('', 'Filename cannot be empty')
])
def test_validate_file_extension_invalid(filename, expected_message):
    """Tests the validate_file_extension function with invalid file extensions"""
    with pytest.raises(ValidationError) as excinfo:
        validate_file_extension(filename)
    assert expected_message in str(excinfo.value)


@pytest.mark.parametrize('status', [
    'Requested', 'InProgress', 'Completed', 'Rejected'
])
def test_validate_negotiation_status_valid(status):
    """Tests the validate_negotiation_status function with valid statuses"""
    # No exception should be raised for valid negotiation statuses
    validate_negotiation_status(status)


@pytest.mark.parametrize('status, expected_message', [
    ('Invalid', 'Invalid negotiation status: Invalid'),
    ('', 'Negotiation status cannot be empty'),
    (None, 'Negotiation status cannot be None')
])
def test_validate_negotiation_status_invalid(status, expected_message):
    """Tests the validate_negotiation_status function with invalid statuses"""
    with pytest.raises(ValidationError) as excinfo:
        validate_negotiation_status(status)
    assert expected_message in str(excinfo.value)


def test_validate_unique_constraint_success():
    """Tests the validate_unique_constraint function with a unique value"""
    # Mock a query function that returns None (indicating uniqueness)
    mock_query = Mock(return_value=None)
    
    # No exception should be raised if the query returns None
    validate_unique_constraint(mock_query, "test_value")
    
    # Verify the mock was called with the test value
    mock_query.assert_called_once_with("test_value")


def test_validate_unique_constraint_violation():
    """Tests the validate_unique_constraint function with a non-unique value"""
    # Mock a query function that returns a result (indicating non-uniqueness)
    mock_query = Mock(return_value={"id": 1})
    
    with pytest.raises(ValidationError) as excinfo:
        validate_unique_constraint(mock_query, "test_value")
    assert "Value already exists" in str(excinfo.value)
    
    # Verify the mock was called with the test value
    mock_query.assert_called_once_with("test_value")


@pytest.mark.parametrize('current_rate, proposed_rate, max_percentage', [
    (100, 105, 5),
    (200, 210, 10),
    (500, 500, 5),
    (100, 104.99, 5)
])
def test_validate_rate_increase_valid(current_rate, proposed_rate, max_percentage):
    """Tests the validate_rate_increase function with valid rate increases"""
    # No exception should be raised for valid rate increases
    validate_rate_increase(current_rate, proposed_rate, max_percentage)


@pytest.mark.parametrize('current_rate, proposed_rate, max_percentage, expected_message', [
    (100, 106, 5, 'Rate increase exceeds maximum allowed percentage of 5%'),
    (200, 250, 10, 'Rate increase exceeds maximum allowed percentage of 10%'),
    (0, 100, 5, 'Current rate cannot be zero when calculating percentage increase'),
    (100, 90, 5, 'Proposed rate cannot be less than current rate')
])
def test_validate_rate_increase_invalid(current_rate, proposed_rate, max_percentage, expected_message):
    """Tests the validate_rate_increase function with invalid rate increases that exceed client rate rules"""
    with pytest.raises(ValidationError) as excinfo:
        validate_rate_increase(current_rate, proposed_rate, max_percentage)
    assert expected_message in str(excinfo.value)


@pytest.mark.parametrize('experience_type, experience_value, min_experience, max_experience', [
    ('GraduationYear', 2015, 2010, 2020),
    ('BarDate', 2018, 2015, 2020),
    ('YearsOfExperience', 7, 5, 10)
])
def test_validate_staff_class_valid(experience_type, experience_value, min_experience, max_experience):
    """Tests the validate_staff_class function with valid staff class parameters"""
    # No exception should be raised for valid staff class parameters
    validate_staff_class(experience_type, experience_value, min_experience, max_experience)


@pytest.mark.parametrize('experience_type, experience_value, min_experience, max_experience, expected_message', [
    ('InvalidType', 2015, 2010, 2020, 'Invalid experience type: InvalidType'),
    ('GraduationYear', 2005, 2010, 2020, 'Experience value is outside the allowed range'),
    ('BarDate', 2025, 2015, 2020, 'Experience value is outside the allowed range'),
    ('YearsOfExperience', 3, 5, 10, 'Experience value is outside the allowed range')
])
def test_validate_staff_class_invalid(experience_type, experience_value, min_experience, max_experience, expected_message):
    """Tests the validate_staff_class function with invalid staff class parameters"""
    with pytest.raises(ValidationError) as excinfo:
        validate_staff_class(experience_type, experience_value, min_experience, max_experience)
    assert expected_message in str(excinfo.value)