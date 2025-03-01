"""
Module for rate calculations and financial impact analysis within the Justice Bid Rate Negotiation System.
Provides functions to calculate rate differences, increases, weighted averages, and projected financial impacts based on historical billing data.
"""

import decimal  # Precise decimal calculations for currency and rate values
from datetime import datetime  # Date handling for rate periods and calculations
from typing import Dict, List, Optional, Union  # Type annotations for improved code clarity

import pandas as pd  # v2.0.0 Data processing for rate calculations and analysis
import numpy as np  # v1.24.0 Numerical operations for rate calculations

from src.backend.db.models.billing import BillingHistory, MatterBillingSummary  # Access to billing history data for impact calculations
from src.backend.db.models.rate import Rate  # Access to rate data model for rate calculations
from src.backend.services.rates.currency import convert_rate, convert_rates_batch, format_rate_with_currency  # Currency conversion and formatting utilities
from src.backend.utils.currency import convert_currency, round_currency, DEFAULT_CURRENCY  # Core currency utilities for calculations
from src.backend.utils.logging import logger  # Logging for calculation operations

RATE_PRECISION = 4  # Decimal places for rate calculations
DEFAULT_REFERENCE_PERIOD = 1  # Default year period for historical data analysis


def calculate_rate_difference(current_rate: decimal.Decimal, proposed_rate: decimal.Decimal) -> dict:
    """
    Calculates the absolute and percentage difference between two rates.

    Args:
        current_rate (Decimal): The current rate.
        proposed_rate (Decimal): The proposed rate.

    Returns:
        dict: Dictionary containing absolute difference and percentage change.
    """
    # Validate that both rates are positive numbers
    if current_rate < 0 or proposed_rate < 0:
        raise ValueError("Rates must be non-negative.")

    # Calculate absolute difference (proposed_rate - current_rate)
    absolute_difference = proposed_rate - current_rate

    # Calculate percentage change ((proposed_rate - current_rate) / current_rate * 100)
    if current_rate != 0:
        percentage_change = (absolute_difference / current_rate) * 100
    else:
        percentage_change = 0  # Avoid division by zero

    # Round percentage to two decimal places
    percentage_change = round(percentage_change, 2)

    # Return dictionary with both values
    return {
        "absolute_difference": absolute_difference,
        "percentage_change": percentage_change,
    }


def calculate_weighted_average_rate(rate_data: list, currency: str) -> decimal.Decimal:
    """
    Calculates the weighted average rate based on hours billed.

    Args:
        rate_data (list): List of dictionaries, each containing 'rate' and 'hours' keys.
        currency (str): The target currency for the weighted average rate.

    Returns:
        Decimal: Weighted average rate in the specified currency.
    """
    # Convert all rates to the same currency if different currencies exist
    total_weighted_sum = 0
    total_hours = 0

    for entry in rate_data:
        rate = entry["rate"]
        hours = entry["hours"]
        from_currency = entry["currency"]

        # Convert rate to the specified currency
        if from_currency != currency:
            rate = convert_currency(rate, from_currency, currency)

        # Calculate weighted sum and total hours
        total_weighted_sum += rate * hours
        total_hours += hours

    # Calculate weighted average as total_weighted_sum / total_hours
    if total_hours > 0:
        weighted_average = total_weighted_sum / total_hours
    else:
        weighted_average = decimal.Decimal("0")

    # Round to appropriate precision for the currency
    weighted_average = round_currency(weighted_average, currency)

    # Return the weighted average rate
    return weighted_average


def calculate_effective_rates(billing_history: list, currency: str) -> dict:
    """
    Calculates effective rates based on historical billing data.

    Args:
        billing_history (list): List of BillingHistory objects.
        currency (str): The target currency for the effective rates.

    Returns:
        dict: Dictionary mapping attorney/staff class to their effective rates.
    """
    # Group billing history by attorney or staff class
    grouped_billing = {}
    for record in billing_history:
        key = record.attorney_id  # Group by attorney for now
        if key not in grouped_billing:
            grouped_billing[key] = []
        grouped_billing[key].append(record)

    effective_rates = {}
    # For each group, calculate total hours and total fees
    for key, records in grouped_billing.items():
        total_hours = sum(record.hours for record in records)
        total_fees = sum(record.fees for record in records)

        # Calculate effective rate as total_fees / total_hours for each group
        if total_hours > 0:
            effective_rate = total_fees / total_hours
        else:
            effective_rate = decimal.Decimal("0")

        # Convert all rates to specified currency
        if records[0].currency != currency:
            effective_rate = convert_currency(effective_rate, records[0].currency, currency)

        effective_rates[key] = effective_rate

    # Return dictionary with calculated effective rates
    return effective_rates


def calculate_rate_impact(current_rates: list, proposed_rates: list, historical_billing: list, currency: str) -> dict:
    """
    Calculates the financial impact of rate changes based on historical billing.

    Args:
        current_rates (list): List of current Rate objects.
        proposed_rates (list): List of proposed Rate objects.
        historical_billing (list): List of BillingHistory objects.
        currency (str): The target currency for the impact analysis.

    Returns:
        dict: Comprehensive impact analysis with total and breakdown by attorney/staff class.
    """
    # Group historical billing by attorney/timekeeper
    billing_by_attorney = {}
    for bill in historical_billing:
        attorney_id = str(bill.attorney_id)
        if attorney_id not in billing_by_attorney:
            billing_by_attorney[attorney_id] = []
        billing_by_attorney[attorney_id].append(bill)

    # Match current and proposed rates with historical billing data
    impact_data = []
    for attorney_id, billing_records in billing_by_attorney.items():
        # Find current and proposed rates for this attorney
        current_rate = next((r for r in current_rates if str(r.attorney_id) == attorney_id), None)
        proposed_rate = next((r for r in proposed_rates if str(r.attorney_id) == attorney_id), None)

        if not current_rate or not proposed_rate:
            logger.warning(f"Missing rate data for attorney {attorney_id}, skipping impact calculation")
            continue

        # Calculate current cost projection using current rates and historical hours
        current_cost = sum(bill.hours * current_rate.amount for bill in billing_records)

        # Calculate proposed cost projection using proposed rates and historical hours
        proposed_cost = sum(bill.hours * proposed_rate.amount for bill in billing_records)

        # Convert to target currency
        if current_rate.currency != currency:
            current_cost = convert_currency(current_cost, current_rate.currency, currency)
        if proposed_rate.currency != currency:
            proposed_cost = convert_currency(proposed_cost, proposed_rate.currency, currency)

        # Calculate absolute and percentage differences
        absolute_difference = proposed_cost - current_cost
        if current_cost != 0:
            percentage_difference = (absolute_difference / current_cost) * 100
        else:
            percentage_difference = 0

        impact_data.append({
            "attorney_id": attorney_id,
            "current_cost": current_cost,
            "proposed_cost": proposed_cost,
            "absolute_difference": absolute_difference,
            "percentage_difference": percentage_difference,
        })

    # Calculate total impact
    total_current_cost = sum(item["current_cost"] for item in impact_data)
    total_proposed_cost = sum(item["proposed_cost"] for item in impact_data)
    total_absolute_difference = total_proposed_cost - total_current_cost
    if total_current_cost != 0:
        total_percentage_difference = (total_absolute_difference / total_current_cost) * 100
    else:
        total_percentage_difference = 0

    # Calculate impact by staff class and other dimensions (not implemented in this version)

    # Return complete impact analysis with various breakdowns
    return {
        "total_current_cost": total_current_cost,
        "total_proposed_cost": total_proposed_cost,
        "total_absolute_difference": total_absolute_difference,
        "total_percentage_difference": total_percentage_difference,
        "impact_by_attorney": impact_data,
        # Add other breakdowns as needed
    }


def calculate_blended_rates(rate_data: list, billing_data: list, dimension: str, currency: str) -> dict:
    """
    Calculates blended rates across different dimensions (staff class, practice area, etc.).

    Args:
        rate_data (list): List of Rate objects.
        billing_data (list): List of BillingHistory objects.
        dimension (str): The dimension to blend rates across (e.g., 'staff_class', 'practice_area').
        currency (str): The target currency for the blended rates.

    Returns:
        dict: Dictionary of blended rates by the specified dimension.
    """
    # Validate dimension parameter (staff_class, practice_area, office, etc.)
    valid_dimensions = ["staff_class", "practice_area", "office"]
    if dimension not in valid_dimensions:
        raise ValueError(f"Invalid dimension: {dimension}. Must be one of {valid_dimensions}")

    # Group rate and billing data by the specified dimension
    grouped_data = {}
    for bill in billing_data:
        # Determine the key based on the dimension
        if dimension == "staff_class":
            key = bill.staff_class_id
        elif dimension == "practice_area":
            key = bill.practice_area
        elif dimension == "office":
            key = bill.office_id
        else:
            raise ValueError(f"Invalid dimension: {dimension}")

        if key not in grouped_data:
            grouped_data[key] = []
        grouped_data[key].append(bill)

    blended_rates = {}
    # For each group, calculate weighted average rate
    for key, records in grouped_data.items():
        # Prepare rate data for the weighted average calculation
        rate_info = []
        for record in records:
            rate = next((r.amount for r in rate_data if r.attorney_id == record.attorney_id), None)
            if rate:
                rate_info.append({"rate": rate, "hours": record.hours, "currency": record.currency})

        # Calculate weighted average rate
        if rate_info:
            blended_rate = calculate_weighted_average_rate(rate_info, currency)
            blended_rates[key] = blended_rate

    # Return dictionary with blended rates by dimension
    return blended_rates


def project_rate_impact(current_rates: list, proposed_rates: list, historical_billing: list, years: int, growth_assumptions: dict, currency: str) -> dict:
    """
    Projects financial impact of rate changes over multiple years.

    Args:
        current_rates (list): List of current Rate objects.
        proposed_rates (list): List of proposed Rate objects.
        historical_billing (list): List of BillingHistory objects.
        years (int): Number of years to project.
        growth_assumptions (dict): Dictionary of growth assumptions (e.g., {'hours': 0.02, 'rate': 0.03}).
        currency (str): The target currency for the projections.

    Returns:
        dict: Year-by-year and cumulative projected impact.
    """
    # Calculate first year impact using calculate_rate_impact
    first_year_impact = calculate_rate_impact(current_rates, proposed_rates, historical_billing, currency)

    # Extract growth assumptions
    hours_growth = growth_assumptions.get("hours", 0)
    rate_growth = growth_assumptions.get("rate", 0)

    # Apply growth assumptions to hours for subsequent years
    projected_impact = {
        "year_by_year": [],
        "cumulative": {}
    }

    cumulative_impact = {
        "current_cost": first_year_impact["total_current_cost"],
        "proposed_cost": first_year_impact["total_proposed_cost"],
        "absolute_difference": first_year_impact["total_absolute_difference"],
        "percentage_difference": first_year_impact["total_percentage_difference"],
    }

    projected_impact["year_by_year"].append({
        "year": datetime.now().year,
        "current_cost": first_year_impact["total_current_cost"],
        "proposed_cost": first_year_impact["total_proposed_cost"],
        "absolute_difference": first_year_impact["total_absolute_difference"],
        "percentage_difference": first_year_impact["total_percentage_difference"],
    })

    # Calculate impact for each projected year
    for year in range(1, years):
        # Apply growth assumptions to historical billing data
        new_billing = []
        for bill in historical_billing:
            new_hours = bill.hours * (1 + hours_growth)
            new_billing.append(
                BillingHistory(
                    attorney_id=bill.attorney_id,
                    client_id=bill.client_id,
                    hours=new_hours,
                    fees=bill.fees,  # Fees will be recalculated based on new rates
                    billing_date=bill.billing_date,
                    currency=bill.currency,
                )
            )

        # Apply additional rate increases for subsequent years if specified
        new_proposed_rates = []
        for rate in proposed_rates:
            new_amount = rate.amount * (1 + rate_growth)
            new_rate = Rate(
                attorney_id=rate.attorney_id,
                client_id=rate.client_id,
                firm_id=rate.firm_id,
                office_id=rate.office_id,
                staff_class_id=rate.staff_class_id,
                amount=new_amount,
                currency=rate.currency,
                effective_date=rate.effective_date,
                expiration_date=rate.expiration_date,
                type=rate.type,
                status=rate.status,
            )
            new_proposed_rates.append(new_rate)

        # Calculate impact for the projected year
        year_impact = calculate_rate_impact(current_rates, new_proposed_rates, new_billing, currency)

        # Aggregate results into year-by-year and cumulative projections
        projected_impact["year_by_year"].append({
            "year": datetime.now().year + year,
            "current_cost": year_impact["total_current_cost"],
            "proposed_cost": year_impact["total_proposed_cost"],
            "absolute_difference": year_impact["total_absolute_difference"],
            "percentage_difference": year_impact["total_percentage_difference"],
        })

        cumulative_impact["current_cost"] += year_impact["total_current_cost"]
        cumulative_impact["proposed_cost"] += year_impact["total_proposed_cost"]
        cumulative_impact["absolute_difference"] += year_impact["total_absolute_difference"]
        # Cumulative percentage difference is not meaningful, so we don't calculate it

    projected_impact["cumulative"] = cumulative_impact

    # Return complete multi-year projection
    return projected_impact


def calculate_afa_impact(current_rates: list, proposed_rates: list, afa_data: list, currency: str) -> dict:
    """
    Calculates impact of rate changes on Alternative Fee Arrangements.

    Args:
        current_rates (list): List of current Rate objects.
        proposed_rates (list): List of proposed Rate objects.
        afa_data (list): List of AFA billing data (e.g., fixed fees, capped fees).
        currency (str): The target currency for the impact analysis.

    Returns:
        dict: Impact analysis for AFA matters.
    """
    # Identify AFA matters from billing data (not implemented in this version)

    # Calculate shadow billing impact (if rates were hourly)

    # Compare AFA fees to projected hourly costs

    # Calculate AFA efficiency metrics

    # Return AFA impact analysis
    return {}


class RateCalculator:
    """
    Class for performing complex rate calculations with state.
    """

    def __init__(self, default_currency: str = DEFAULT_CURRENCY, include_afa: bool = False):
        """
        Initializes a new RateCalculator instance.

        Args:
            default_currency (str): The default currency for calculations.
            include_afa (bool): Whether to include AFA data in calculations.
        """
        # Set default currency (default to DEFAULT_CURRENCY if not provided)
        self.default_currency = default_currency

        # Set include_afa flag for AFA calculations
        self.include_afa = include_afa

        # Initialize currency converter instance
        self._currency_converter = None  # Placeholder for currency converter

    def calculate_impact(self, current_rates: list, proposed_rates: list, historical_billing: list, options: dict) -> dict:
        """
        Calculates comprehensive rate impact with configurable options.

        Args:
            current_rates (list): List of current Rate objects.
            proposed_rates (list): List of proposed Rate objects.
            historical_billing (list): List of BillingHistory objects.
            options (dict): Dictionary of configuration options.

        Returns:
            dict: Complete impact analysis based on configuration options.
        """
        # Process and normalize input data
        # Apply filters from options if specified
        # Determine analysis type from options
        analysis_type = options.get("analysis_type", "standard")

        # Call appropriate calculation method based on analysis type
        if analysis_type == "standard":
            impact = calculate_rate_impact(current_rates, proposed_rates, historical_billing, self.default_currency)
        elif analysis_type == "afa":
            impact = calculate_afa_impact(current_rates, proposed_rates, historical_billing, self.default_currency)
        else:
            raise ValueError(f"Invalid analysis type: {analysis_type}")

        # Apply result formatting based on options
        # Return complete analysis results
        return impact

    def calculate_weighted_rates(self, rate_data: list, billing_data: list, dimensions: list) -> dict:
        """
        Calculates weighted rates across different dimensions.

        Args:
            rate_data (list): List of Rate objects.
            billing_data (list): List of BillingHistory objects.
            dimensions (list): List of dimensions to calculate weighted rates across.

        Returns:
            dict: Weighted rates across specified dimensions.
        """
        weighted_rates = {}
        # For each dimension, call calculate_blended_rates
        for dimension in dimensions:
            blended_rates = calculate_blended_rates(rate_data, billing_data, dimension, self.default_currency)
            weighted_rates[dimension] = blended_rates

        # Return complete weighted rate analysis
        return weighted_rates

    def forecast_impact(self, current_rates: list, proposed_rates: list, historical_billing: list, forecast_options: dict) -> dict:
        """
        Forecasts future impact of rate changes with growth modeling.

        Args:
            current_rates (list): List of current Rate objects.
            proposed_rates (list): List of proposed Rate objects.
            historical_billing (list): List of BillingHistory objects.
            forecast_options (dict): Dictionary of forecasting options.

        Returns:
            dict: Forecasted impact over time period.
        """
        # Extract forecast period and growth assumptions from options
        forecast_years = forecast_options.get("years", 3)
        growth_assumptions = forecast_options.get("growth", {"hours": 0, "rate": 0})

        # Call project_rate_impact with appropriate parameters
        projected_impact = project_rate_impact(current_rates, proposed_rates, historical_billing, forecast_years, growth_assumptions, self.default_currency)

        # Return formatted forecast results
        return projected_impact

    def compare_scenarios(self, current_rates: list, scenario_rates: list, historical_billing: list) -> dict:
        """
        Compares multiple rate scenarios against each other.

        Args:
            current_rates (list): List of current Rate objects.
            scenario_rates (list): List of Rate objects for the scenario.
            historical_billing (list): List of BillingHistory objects.

        Returns:
            dict: Comparative analysis of different rate scenarios.
        """
        # Calculate impact for each scenario
        current_impact = calculate_rate_impact(current_rates, current_rates, historical_billing, self.default_currency)
        scenario_impact = calculate_rate_impact(current_rates, scenario_rates, historical_billing, self.default_currency)

        # Create comparative metrics between scenarios
        comparison = {
            "current": current_impact,
            "scenario": scenario_impact,
            "difference": {
                "total_cost": scenario_impact["total_proposed_cost"] - current_impact["total_proposed_cost"],
                "percentage_change": scenario_impact["total_percentage_difference"] - current_impact["total_percentage_difference"],
            }
        }

        # Return structured comparison of all scenarios
        return comparison