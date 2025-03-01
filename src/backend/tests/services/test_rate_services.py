import pytest
from unittest.mock import MagicMock
from datetime import date, datetime
from decimal import Decimal

from src.backend.services.rates import validation
from src.backend.db.repositories.rate_repository import RateRepository
from src.backend.db.models.rate import Rate
from src.backend.services.rates.calculation import calculate_rate_impact
from src.backend.services.rates.history import track_rate_history
from src.backend.services.rates.rules import check_rate_rules
from src.backend.services.rates.currency import convert_currency
from src.backend.api.core.errors import ValidationError, FreezeError

# Define test functions for rate validation, calculation, and rule enforcement
def test_validate_rate_valid():
    """Tests that validate_rate function accepts valid rate proposals"""
    # Create a mock Rate object with valid attributes
    rate = MagicMock(spec=Rate)
    rate.amount = Decimal('100.00')
    rate.effective_date = date(2024, 1, 1)

    # Define client rate rules with appropriate limits
    client_rules = {'max_increase_percent': 10, 'freeze_period': 0}

    # Create a mock organization to represent the client
    client = MagicMock()
    client.rate_rules = client_rules

    # Call validate_rate with the rate and client
    try:
        validation.validate_rate(rate, client)
    except ValidationError:
        pytest.fail("validate_rate raised ValidationError unexpectedly")

    # Assert that no exceptions are raised
    assert True

    # Assert the rate is marked as valid
    assert rate.is_valid is not False


def test_validate_rate_exceeds_max_increase():
    """Tests that validate_rate function rejects rates exceeding maximum increase percentage"""
    # Create a mock Rate object with current rate of $100
    rate = MagicMock(spec=Rate)
    rate.amount = Decimal('120.00')  # Proposed rate with $120 (20% increase)
    rate.effective_date = date(2024, 1, 1)
    rate.current_rate = Decimal('100.00')

    # Define client rate rules with max increase of 5%
    client_rules = {'max_increase_percent': 5}

    # Create a mock organization to represent the client
    client = MagicMock()
    client.rate_rules = client_rules

    # Call validate_rate with the rate and client
    with pytest.raises(ValidationError) as excinfo:
        validation.validate_rate(rate, client)

    # Assert that ValidationError is raised with appropriate message
    assert "exceeds the maximum allowed increase" in str(excinfo.value)


def test_validate_rate_within_freeze_period():
    """Tests that validate_rate function rejects rates submitted within a rate freeze period"""
    # Create a mock Rate object with valid rate amount
    rate = MagicMock(spec=Rate)
    rate.amount = Decimal('110.00')
    rate.effective_date = date(2023, 12, 1)

    # Set the effective date within an active freeze period
    rate.last_change_date = date(2023, 6, 1)

    # Define client rate rules with active freeze period
    client_rules = {'freeze_period': 9}  # 9-month freeze period

    # Create a mock organization to represent the client
    client = MagicMock()
    client.rate_rules = client_rules

    # Call validate_rate with the rate and client
    with pytest.raises(FreezeError) as excinfo:
        validation.validate_rate(rate, client)

    # Assert that FreezeError is raised with appropriate message
    assert "within the rate freeze period" in str(excinfo.value)


def test_calculate_rate_impact():
    """Tests calculation of financial impact based on rate changes and historical hours"""
    # Create a set of current rates for various attorneys
    current_rates = [
        MagicMock(spec=Rate, attorney_id='attorney1', amount=Decimal('100.00')),
        MagicMock(spec=Rate, attorney_id='attorney2', amount=Decimal('150.00')),
        MagicMock(spec=Rate, attorney_id='attorney3', amount=Decimal('200.00'))
    ]

    # Create a set of proposed rates with increases
    proposed_rates = [
        MagicMock(spec=Rate, attorney_id='attorney1', amount=Decimal('110.00')),
        MagicMock(spec=Rate, attorney_id='attorney2', amount=Decimal('160.00')),
        MagicMock(spec=Rate, attorney_id='attorney3', amount=Decimal('210.00'))
    ]

    # Create historical billing data with hours for each attorney
    historical_billing = [
        MagicMock(spec=Rate, attorney_id='attorney1', hours=100),
        MagicMock(spec=Rate, attorney_id='attorney2', hours=50),
        MagicMock(spec=Rate, attorney_id='attorney3', hours=25)
    ]

    # Call calculate_rate_impact with current rates, proposed rates, and historical data
    impact = calculate_rate_impact(current_rates, proposed_rates, historical_billing)

    # Assert that the calculated impact matches expected value based on rate differences and hours
    expected_impact = Decimal('1950.00')  # (10*100) + (10*50) + (10*25)
    assert impact == expected_impact


def test_track_rate_history():
    """Tests that rate history is properly recorded when rates change"""
    # Create a mock Rate object with initial values
    rate = MagicMock(spec=Rate)
    rate.amount = Decimal('100.00')
    rate.status = 'active'
    rate.history = []

    # Mock the rate repository to test database interactions
    rate_repository = MagicMock(spec=RateRepository)

    # Call track_rate_history with the rate and change information
    track_rate_history(rate, 'user123', 'Rate increased')

    # Assert that repository was called with correct history data
    rate_repository.update.assert_called_with(rate.id, {'history': rate.history})

    # Verify the history contains expected timestamp, user, and old/new values
    assert len(rate.history) == 1
    history_entry = rate.history[0]
    assert 'timestamp' in history_entry
    assert history_entry['user'] == 'user123'
    assert history_entry['old_amount'] == Decimal('100.00')
    assert history_entry['new_amount'] == Decimal('100.00')  # Should remain the same
    assert history_entry['message'] == 'Rate increased'


def test_convert_currency():
    """Tests currency conversion for rates"""
    # Create a mock Rate object in USD currency
    rate = MagicMock(spec=Rate)
    rate.amount = Decimal('100.00')
    rate.currency = 'USD'

    # Mock the currency conversion service with known exchange rates
    def mock_convert_currency(amount, from_currency, to_currency):
        if from_currency == 'USD' and to_currency == 'EUR':
            return amount * Decimal('0.85')
        return amount

    # Call convert_currency to convert to EUR
    converted_rate = convert_currency(rate, 'EUR', mock_convert_currency)

    # Assert that the converted rate has the correct amount in EUR
    assert converted_rate.amount == Decimal('85.00')

    # Assert that the currency code is updated correctly
    assert converted_rate.currency == 'EUR'


def test_check_rate_rules_compliant():
    """Tests that compliant rate changes pass rule checks"""
    # Create a mock Rate object with current and proposed values within allowed limits
    rate = MagicMock(spec=Rate)
    rate.amount = Decimal('105.00')  # 5% increase from 100
    rate.effective_date = date(2024, 1, 1)

    # Define client rate rules with appropriate constraints
    client_rules = {'max_increase_percent': 10, 'freeze_period': 0}

    # Call check_rate_rules with the rate and client rules
    is_compliant, validation_errors = check_rate_rules(rate, client_rules)

    # Assert that the result indicates compliance
    assert is_compliant is True

    # Verify no validation errors are returned
    assert validation_errors == []


def test_check_rate_rules_multiple_violations():
    """Tests that multiple rule violations are detected and reported"""
    # Create a mock Rate object that violates multiple rules (increase, freeze period, etc.)
    rate = MagicMock(spec=Rate)
    rate.amount = Decimal('120.00')  # 20% increase
    rate.effective_date = date(2023, 12, 1)
    rate.last_change_date = date(2023, 6, 1)

    # Define client rate rules with multiple constraints
    client_rules = {'max_increase_percent': 5, 'freeze_period': 9}

    # Call check_rate_rules with the rate and client rules
    is_compliant, validation_errors = check_rate_rules(rate, client_rules)

    # Assert that the result indicates non-compliance
    assert is_compliant is False

    # Verify that all expected violations are included in the result
    assert len(validation_errors) == 2
    assert "exceeds the maximum allowed increase" in validation_errors[0]
    assert "within the rate freeze period" in validation_errors[1]