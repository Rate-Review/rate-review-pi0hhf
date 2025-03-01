"""
This module provides functionality for managing, validating, and applying rate rules in the rate negotiation process.
It handles rate freeze periods, notice periods, submission windows, maximum increase percentages, and other client-defined rate rules.
"""

from typing import Dict, Optional
from datetime import datetime, date

from sqlalchemy.exc import SQLAlchemyError

from src.backend.db.models.organization import Organization  # Import Organization model
from src.backend.db.models.rate import Rate  # Import Rate model
from src.backend.db.repositories import organization_repository  # Import organization repository
from src.backend.db.repositories import rate_repository  # Import rate repository
from src.backend.utils import datetime_utils  # Import datetime utilities
from src.backend.utils.validators import ValidationError  # Import ValidationError for raising validation errors
from src.backend.utils.logging import logger  # Import logger for logging


def get_organization_rate_rules(organization_id: str) -> Dict:
    """
    Retrieves the rate rules configured for a specific organization.

    Args:
        organization_id: UUID of the organization.

    Returns:
        Dictionary containing rate rule settings for the organization.
    """
    try:
        # Retrieve organization from database using organization_id
        organization = organization_repository.organization_repository.get_by_id(organization_id)

        if not organization:
            logger.warning(f"Organization not found with ID: {organization_id}")
            return get_default_rate_rules()

        # Extract rate rules from organization settings
        rate_rules = organization.get_rate_rules()

        # Return rate rules as a dictionary with default values for missing settings
        default_rules = get_default_rate_rules()
        return {**default_rules, **rate_rules}  # Merge with defaults

    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving rate rules for organization {organization_id}: {str(e)}")
        return get_default_rate_rules()  # Return default rules if organization not found


def is_within_rate_freeze_period(rate_rules: Dict, effective_date: datetime, last_change_date: datetime) -> bool:
    """
    Checks if a proposed rate change falls within a rate freeze period.

    Args:
        rate_rules: Dictionary containing rate rule settings.
        effective_date: Proposed effective date of the rate change.
        last_change_date: Date of the last rate change.

    Returns:
        True if within freeze period, False otherwise.
    """
    # Extract freeze period duration from rate_rules
    freeze_period = rate_rules.get('freeze_period', 12)  # Default to 12 months

    # Calculate the end date of the freeze period based on last_change_date
    freeze_end_date = datetime_utils.add_months(last_change_date, freeze_period)

    # Check if effective_date is before the end of the freeze period
    return effective_date <= freeze_end_date


def check_notice_period_compliance(rate_rules: Dict, submission_date: datetime, effective_date: datetime) -> bool:
    """
    Checks if a proposed rate change provides sufficient notice based on client rules.

    Args:
        rate_rules: Dictionary containing rate rule settings.
        submission_date: Date the rate change was submitted.
        effective_date: Proposed effective date of the rate change.

    Returns:
        True if notice period is compliant, False otherwise.
    """
    # Extract notice period duration from rate_rules
    notice_period = rate_rules.get('notice_required', 60)  # Default to 60 days

    # Calculate the minimum required notice period in days
    min_notice_date = datetime_utils.add_days(submission_date, notice_period)

    # Check if the effective_date is after the minimum required notice date
    return effective_date >= min_notice_date


def is_within_submission_window(rate_rules: Dict, submission_date: datetime) -> bool:
    """
    Checks if a rate submission is within the allowed submission window defined by client.

    Args:
        rate_rules: Dictionary containing rate rule settings.
        submission_date: Date the rate change was submitted.

    Returns:
        True if within submission window, False otherwise.
    """
    # Extract submission window settings from rate_rules
    submission_window = rate_rules.get('submission_window', {})

    # Get start and end dates for the submission window in the current year
    window = calculate_submission_window(rate_rules, submission_date.year)
    start_date = window['start_date']
    end_date = window['end_date']

    # Check if submission_date falls within the window
    return datetime_utils.is_date_within_range(submission_date, start_date, end_date)


def calculate_submission_window(rate_rules: Dict, year: Optional[int] = None) -> Dict:
    """
    Calculates the current submission window dates based on client rules.

    Args:
        rate_rules: Dictionary containing rate rule settings.
        year: Optional year for the submission window.

    Returns:
        Dictionary with start_date and end_date of submission window.
    """
    # Extract submission window settings from rate_rules
    submission_window = rate_rules.get('submission_window', {})

    # Use current year if no year provided
    current_year = year or datetime.now().year

    # Calculate start date based on start month and day
    start_month = submission_window.get('start_month', 10)  # Default to October
    start_day = submission_window.get('start_day', 1)  # Default to 1st
    start_date = date(current_year, start_month, start_day)

    # Calculate end date based on end month and day
    end_month = submission_window.get('end_month', 12)  # Default to December
    end_day = submission_window.get('end_day', 31)  # Default to 31st
    end_date = date(current_year, end_month, end_day)

    # Handle year boundary cases (if window spans across years)
    if start_date > end_date:
        end_date = date(current_year + 1, end_month, end_day)

    # Return dictionary with start_date and end_date
    return {'start_date': start_date, 'end_date': end_date}


def is_rate_increase_compliant(rate_rules: Dict, current_rate: float, proposed_rate: float) -> bool:
    """
    Checks if a proposed rate increase is within the maximum allowed percentage.

    Args:
        rate_rules: Dictionary containing rate rule settings.
        current_rate: Current rate amount.
        proposed_rate: Proposed rate amount.

    Returns:
        True if increase is compliant, False otherwise.
    """
    # Extract maximum increase percentage from rate_rules
    max_increase_percent = rate_rules.get('max_increase_percent', 5.0)  # Default to 5%

    # Calculate the percentage increase from current_rate to proposed_rate
    increase_percent = ((proposed_rate - current_rate) / current_rate) * 100

    # Check if calculated increase exceeds the maximum allowed
    return increase_percent <= max_increase_percent


def calculate_maximum_allowed_rate(rate_rules: Dict, current_rate: float) -> float:
    """
    Calculates the maximum allowed rate based on current rate and maximum increase percentage.

    Args:
        rate_rules: Dictionary containing rate rule settings.
        current_rate: Current rate amount.

    Returns:
        Maximum allowed rate after applying increase rule.
    """
    # Extract maximum increase percentage from rate_rules
    max_increase_percent = rate_rules.get('max_increase_percent', 5.0)  # Default to 5%

    # Calculate the maximum allowed increase amount
    max_increase_amount = current_rate * (max_increase_percent / 100)

    # Add the increase to the current rate
    maximum_allowed_rate = current_rate + max_increase_amount

    return maximum_allowed_rate


def validate_rate_rules(client_id: str, attorney_id: str, proposed_rate: float, effective_date: datetime,
                       submission_date: Optional[datetime] = None) -> Dict:
    """
    Validates a rate submission against all applicable rate rules.

    Args:
        client_id: UUID of the client organization.
        attorney_id: UUID of the attorney.
        proposed_rate: Proposed rate amount.
        effective_date: Proposed effective date of the rate change.
        submission_date: Optional date the rate change was submitted.

    Returns:
        Dictionary with validation results and explanations.
    """
    # Retrieve organization rate rules for the client
    rate_rules = get_organization_rate_rules(client_id)

    # Get current rate and last change date for the attorney and client
    current_rate_data = rate_repository.rate_repository.get_rates_by_attorney_and_client(attorney_id, client_id)
    current_rate = current_rate_data[0].amount if current_rate_data else 0.0
    last_change_date = current_rate_data[0].updated_at if current_rate_data else effective_date

    # Use current date as submission_date if not provided
    submission_date = submission_date or datetime.now()

    # Check freeze period compliance
    freeze_compliant = not is_within_rate_freeze_period(rate_rules, effective_date, last_change_date)
    freeze_explanation = "Rate change is within the rate freeze period." if not freeze_compliant else None

    # Check notice period compliance
    notice_compliant = check_notice_period_compliance(rate_rules, submission_date, effective_date)
    notice_explanation = "Insufficient notice period provided." if not notice_compliant else None

    # Check submission window compliance
    window_compliant = is_within_submission_window(rate_rules, submission_date)
    window_explanation = "Rate submission is outside the allowed submission window." if not window_compliant else None

    # Check rate increase compliance
    increase_compliant = is_rate_increase_compliant(rate_rules, current_rate, proposed_rate)
    increase_explanation = "Proposed rate increase exceeds the maximum allowed percentage." if not increase_compliant else None

    # Compile validation results including explanations for failures
    validation_results = {
        "freeze_compliant": freeze_compliant,
        "notice_compliant": notice_compliant,
        "window_compliant": window_compliant,
        "increase_compliant": increase_compliant,
        "freeze_explanation": freeze_explanation,
        "notice_explanation": notice_explanation,
        "window_explanation": window_explanation,
        "increase_explanation": increase_explanation
    }

    return validation_results


def get_request_frequency_compliance(rate_rules: Dict, client_id: str, firm_id: str, request_date: datetime) -> bool:
    """
    Checks if a rate request complies with the allowed frequency of requests.

    Args:
        rate_rules: Dictionary containing rate rule settings.
        client_id: UUID of the client organization.
        firm_id: UUID of the law firm organization.
        request_date: Date of the rate request.

    Returns:
        True if request frequency is compliant, False otherwise.
    """
    # Extract request frequency limitations from rate_rules
    request_frequency = rate_rules.get('request_frequency', 1)  # Default to once per year

    # Retrieve historical request data for the firm and client
    # TODO: Implement historical request data retrieval
    # For now, assume compliance
    return True


def get_default_rate_rules() -> Dict:
    """
    Returns a set of default rate rules when organization-specific rules are not available.

    Returns:
        Dictionary containing default rate rule settings.
    """
    # Define default freeze period (e.g., 12 months)
    default_freeze_period = 12

    # Define default notice period (e.g., 60 days)
    default_notice_period = 60

    # Define default submission window (e.g., Oct 1 - Dec 31)
    default_submission_window = {
        'start_month': 10,
        'start_day': 1,
        'end_month': 12,
        'end_day': 31
    }

    # Define default maximum increase percentage (e.g., 5%)
    default_max_increase_percent = 5.0

    # Define default request frequency (e.g., once per year)
    default_request_frequency = 1

    # Return dictionary with all default settings
    return {
        'freeze_period': default_freeze_period,
        'notice_required': default_notice_period,
        'submission_window': default_submission_window,
        'max_increase_percent': default_max_increase_percent,
        'request_frequency': default_request_frequency
    }