"""
Initialization file for the rates service package that exports key functions and classes from rate service submodules.
This package handles all operations related to attorney rates, including validation, calculation, currency conversion, rules enforcement, history tracking, staff class management, and exports.
"""

from .currency import CurrencyService  # Service for handling currency conversions in rate data
from .validation import RateValidator, validate_rate, validate_rates  # Service for validating rate data against rules
from .calculation import RateCalculator, calculate_rate_impact  # Service for performing rate calculations
from .rules import RateRuleService  # Service for managing rate rules
from .history import RateHistoryService  # Service for tracking and querying rate history
from .staff_class import StaffClassService  # Service for managing staff classes
from .export import RateExportService  # Service for exporting rates to external systems

__all__ = [
    "CurrencyService",
    "RateValidator",
    "validate_rate",
    "validate_rates",
    "RateCalculator",
    "calculate_rate_impact",
    "RateRuleService",
    "RateHistoryService",
    "StaffClassService",
    "RateExportService",
]