"""
Service component responsible for analyzing historical rate trends over time in the Justice Bid Rate Negotiation System,
supporting the rate analytics dashboard and historical trends visualization.
"""

import typing
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
import numpy  # version: ^1.24.0
import pandas  # version: ^2.0.0
from decimal import Decimal

from src.backend.db.models.rate import Rate
from src.backend.db.repositories.rate_repository import RateRepository
from src.backend.db.repositories.billing_repository import BillingRepository
from src.backend.utils.currency import convert_currency
from src.backend.utils.datetime_utils import get_current_date, add_years, get_fiscal_year_start, get_fiscal_year_end, date_diff_years, get_month_range
from src.backend.utils.logging import logger

DEFAULT_TREND_YEARS = 5
DEFAULT_CURRENCY = "USD"
CPI_DATA = {2018: 2.4, 2019: 1.8, 2020: 1.2, 2021: 4.7, 2022: 8.0, 2023: 3.4}


class RateTrendsAnalyzer:
    """
    Service class for analyzing historical rate trends over time, providing insights on rate changes, CAGR calculations, and comparison against inflation.
    """

    def __init__(self, rate_repository: RateRepository, billing_repository: BillingRepository):
        """
        Initializes the RateTrendsAnalyzer with required repositories
        
        Args:
            rate_repository: RateRepository instance for rate data access
            billing_repository: BillingRepository instance for correlation with billing data
        """
        self.rate_repository = rate_repository
        self.billing_repository = billing_repository
        # Initialize any required instance variables
        logger.debug("RateTrendsAnalyzer initialized")

    def get_rate_trends_by_attorney(self, attorney_id: str, client_id: Optional[str] = None,
                                    start_date: Optional[date] = None, end_date: Optional[date] = None,
                                    currency: Optional[str] = None, years: Optional[int] = None) -> dict:
        """
        Analyzes rate trends for a specific attorney over time
        
        Args:
            attorney_id: UUID of the attorney
            client_id: Optional UUID of the client to filter by
            start_date: Optional start date for the analysis period
            end_date: Optional end date for the analysis period
            currency: Optional currency to convert all amounts to
            years: Optional number of years to analyze (default: DEFAULT_TREND_YEARS)
        
        Returns:
            Attorney rate trend analysis including historical rates, CAGR, and inflation comparison
        """
        # Set default values for optional parameters if not provided
        if currency is None:
            currency = DEFAULT_CURRENCY
        if years is None:
            years = DEFAULT_TREND_YEARS

        # Retrieve rate history data for the attorney from rate_repository
        rate_history = self.rate_repository.get_rate_history(attorney_id, client_id, start_date, end_date)

        # Convert all rates to the specified currency for consistent analysis
        converted_rates = []
        for rate in rate_history:
            converted_rate = convert_currency(rate.amount, rate.currency, currency)
            converted_rates.append({"effective_date": rate.effective_date, "amount": converted_rate})

        # Calculate year-over-year rate changes
        rate_changes = []
        for i in range(1, len(converted_rates)):
            rate_changes.append({
                "year": converted_rates[i]["effective_date"].year,
                "change": (converted_rates[i]["amount"] - converted_rates[i - 1]["amount"]) / converted_rates[i - 1]["amount"] if converted_rates[i - 1]["amount"] else 0
            })

        # Calculate Compound Annual Growth Rate (CAGR) over the specified period
        start_value = converted_rates[0]["amount"] if converted_rates else 0
        end_value = converted_rates[-1]["amount"] if converted_rates else 0
        cagr = self.calculate_cagr(start_value, end_value, years)

        # Compare rate increases against inflation (CPI) for the same period
        start_year = get_current_date().year - years
        end_year = get_current_date().year
        inflation_data = self.get_inflation_for_period(start_year, end_year)

        # Format and return the analysis results
        analysis_results = {
            "attorney_id": attorney_id,
            "client_id": client_id,
            "currency": currency,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "historical_rates": [{"year": r["effective_date"].year, "amount": float(r["amount"])} for r in converted_rates],
            "rate_changes": rate_changes,
            "cagr": cagr,
            "inflation": inflation_data
        }
        logger.info(f"Analyzed rate trends for attorney {attorney_id}")
        return analysis_results

    def get_rate_trends_by_client(self, client_id: str, firm_id: Optional[str] = None,
                                  start_date: Optional[date] = None, end_date: Optional[date] = None,
                                  currency: Optional[str] = None, years: Optional[int] = None) -> dict:
        """
        Analyzes rate trends for a specific client's attorneys over time
        
        Args:
            client_id: UUID of the client
            firm_id: Optional UUID of the law firm to filter by
            start_date: Optional start date for the analysis period
            end_date: Optional end date for the analysis period
            currency: Optional currency to convert all amounts to
            years: Optional number of years to analyze (default: DEFAULT_TREND_YEARS)
        
        Returns:
            Client rate trend analysis with aggregate statistics and breakdowns
        """
        # Set default values for optional parameters if not provided
        if currency is None:
            currency = DEFAULT_CURRENCY
        if years is None:
            years = DEFAULT_TREND_YEARS

        # Retrieve rate data for all attorneys associated with the client
        rates = self.rate_repository.get_by_client(client_id, firm_id, start_date, end_date)

        # Optionally filter by firm_id if provided
        if firm_id:
            rates = [rate for rate in rates if str(rate.firm_id) == firm_id]

        # Convert all rates to the specified currency for consistent analysis
        converted_rates = []
        for rate in rates:
            converted_rate = convert_currency(rate.amount, rate.currency, currency)
            converted_rates.append({"effective_date": rate.effective_date, "amount": converted_rate, "staff_class_id": rate.staff_class_id, "practice_area": rate.practice_area})

        # Calculate aggregate rate trends across all attorneys
        total_rate_changes = []
        for i in range(1, len(converted_rates)):
            total_rate_changes.append((converted_rates[i]["amount"] - converted_rates[i - 1]["amount"]) / converted_rates[i - 1]["amount"] if converted_rates[i - 1]["amount"] else 0)

        # Calculate trends by staff class for the client
        staff_class_trends = {}
        for rate in converted_rates:
            staff_class_id = str(rate["staff_class_id"])
            if staff_class_id not in staff_class_trends:
                staff_class_trends[staff_class_id] = []
            staff_class_trends[staff_class_id].append(rate["amount"])

        # Calculate trends by practice area for the client
        practice_area_trends = {}
        for rate in converted_rates:
            practice_area = rate["practice_area"]
            if practice_area not in practice_area_trends:
                practice_area_trends[practice_area] = []
            practice_area_trends[practice_area].append(rate["amount"])

        # Calculate CAGR and compare against inflation
        start_value = converted_rates[0]["amount"] if converted_rates else 0
        end_value = converted_rates[-1]["amount"] if converted_rates else 0
        cagr = self.calculate_cagr(start_value, end_value, years)

        start_year = get_current_date().year - years
        end_year = get_current_date().year
        inflation_data = self.get_inflation_for_period(start_year, end_year)

        # Format and return the analysis results
        analysis_results = {
            "client_id": client_id,
            "firm_id": firm_id,
            "currency": currency,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "total_rates": len(converted_rates),
            "average_rate_change": numpy.mean(total_rate_changes) if total_rate_changes else 0,
            "staff_class_trends": staff_class_trends,
            "practice_area_trends": practice_area_trends,
            "cagr": cagr,
            "inflation": inflation_data
        }
        logger.info(f"Analyzed rate trends for client {client_id}")
        return analysis_results

    def get_rate_trends_by_firm(self, firm_id: str, client_id: Optional[str] = None,
                                start_date: Optional[date] = None, end_date: Optional[date] = None,
                                currency: Optional[str] = None, years: Optional[int] = None) -> dict:
        """
        Analyzes rate trends for a specific law firm's attorneys over time
        
        Args:
            firm_id: UUID of the law firm
            client_id: Optional UUID of the client to filter by
            start_date: Optional start date for the analysis period
            end_date: Optional end date for the analysis period
            currency: Optional currency to convert all amounts to
            years: Optional number of years to analyze (default: DEFAULT_TREND_YEARS)
        
        Returns:
            Firm rate trend analysis with aggregate statistics and breakdowns
        """
        # Set default values for optional parameters if not provided
        if currency is None:
            currency = DEFAULT_CURRENCY
        if years is None:
            years = DEFAULT_TREND_YEARS

        # Retrieve rate data for all attorneys associated with the firm
        rates = self.rate_repository.get_by_firm(firm_id, client_id, start_date, end_date)

        # Optionally filter by client_id if provided
        if client_id:
            rates = [rate for rate in rates if str(rate.client_id) == client_id]

        # Convert all rates to the specified currency for consistent analysis
        converted_rates = []
        for rate in rates:
            converted_rate = convert_currency(rate.amount, rate.currency, currency)
            converted_rates.append({"effective_date": rate.effective_date, "amount": converted_rate, "staff_class_id": rate.staff_class_id, "office_id": rate.office_id})

        # Calculate aggregate rate trends across all attorneys
        total_rate_changes = []
        for i in range(1, len(converted_rates)):
            total_rate_changes.append((converted_rates[i]["amount"] - converted_rates[i - 1]["amount"]) / converted_rates[i - 1]["amount"] if converted_rates[i - 1]["amount"] else 0)

        # Calculate trends by staff class for the firm
        staff_class_trends = {}
        for rate in converted_rates:
            staff_class_id = str(rate["staff_class_id"])
            if staff_class_id not in staff_class_trends:
                staff_class_trends[staff_class_id] = []
            staff_class_trends[staff_class_id].append(rate["amount"])

        # Calculate trends by office location for the firm
        office_trends = {}
        for rate in converted_rates:
            office_id = str(rate["office_id"])
            if office_id not in office_trends:
                office_trends[office_id] = []
            office_trends[office_id].append(rate["amount"])

        # Calculate CAGR and compare against inflation
        start_value = converted_rates[0]["amount"] if converted_rates else 0
        end_value = converted_rates[-1]["amount"] if converted_rates else 0
        cagr = self.calculate_cagr(start_value, end_value, years)

        start_year = get_current_date().year - years
        end_year = get_current_date().year
        inflation_data = self.get_inflation_for_period(start_year, end_year)

        # Format and return the analysis results
        analysis_results = {
            "firm_id": firm_id,
            "client_id": client_id,
            "currency": currency,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "total_rates": len(converted_rates),
            "average_rate_change": numpy.mean(total_rate_changes) if total_rate_changes else 0,
            "staff_class_trends": staff_class_trends,
            "office_trends": office_trends,
            "cagr": cagr,
            "inflation": inflation_data
        }
        logger.info(f"Analyzed rate trends for firm {firm_id}")
        return analysis_results

    def calculate_cagr(self, start_value: float, end_value: float, years: int) -> float:
        """
        Calculates the Compound Annual Growth Rate for rates over a specified period
        
        Args:
            start_value: Initial rate value
            end_value: Final rate value
            years: Number of years in the period
        
        Returns:
            CAGR as a percentage
        """
        # Validate input parameters are positive and years > 0
        if start_value <= 0 or end_value <= 0 or years <= 0:
            return 0.0

        # Apply CAGR formula: ((end_value / start_value) ^ (1 / years) - 1) * 100
        cagr = ((end_value / start_value) ** (1 / years) - 1) * 100

        # Round the result to two decimal places
        return round(cagr, 2)

    def get_inflation_for_period(self, start_year: int, end_year: int) -> dict:
        """
        Retrieves inflation (CPI) data for a specified time period
        
        Args:
            start_year: Start year for the period
            end_year: End year for the period
        
        Returns:
            Inflation data including average, cumulative, and yearly breakdown
        """
        # Validate start_year and end_year are valid years in CPI_DATA
        if start_year not in CPI_DATA or end_year not in CPI_DATA:
            return {}

        # Calculate average annual inflation over the period
        total_inflation = sum(CPI_DATA[year] for year in range(start_year, end_year + 1))
        average_inflation = total_inflation / (end_year - start_year + 1)

        # Calculate cumulative inflation over the period
        cumulative_inflation = 1.0
        for year in range(start_year, end_year + 1):
            cumulative_inflation *= (1 + CPI_DATA[year] / 100)
        cumulative_inflation = (cumulative_inflation - 1) * 100

        # Extract yearly inflation data for each year in the period
        yearly_data = {year: CPI_DATA[year] for year in range(start_year, end_year + 1)}

        # Return a dictionary with the inflation statistics
        return {
            "average": round(average_inflation, 2),
            "cumulative": round(cumulative_inflation, 2),
            "yearly": yearly_data
        }
    
    def get_time_series_data(self, entity_type: str, entity_id: str, related_id: Optional[str] = None,
                                group_by: Optional[str] = None, start_date: Optional[date] = None,
                                end_date: Optional[date] = None, currency: Optional[str] = None) -> dict:
        """
        Generates time series data for visualizing rate trends over time
        
        Args:
            entity_type: Type of entity ('attorney', 'client', 'firm')
            entity_id: UUID of the entity
            related_id: Optional UUID of a related entity (e.g., client for attorney trends)
            group_by: Optional field to group data by (e.g., 'staff_class', 'office')
            start_date: Optional start date for the time series
            end_date: Optional end date for the time series
            currency: Optional currency to convert all amounts to
        
        Returns:
            Time series data structured for visualization in charts
        """
        # Set default values for optional parameters if not provided
        if currency is None:
            currency = DEFAULT_CURRENCY
        
        # Validate entity_type is one of 'attorney', 'client', 'firm'
        if entity_type not in ['attorney', 'client', 'firm']:
            raise ValueError("Invalid entity_type. Must be 'attorney', 'client', or 'firm'")
        
        # Retrieve appropriate rate data based on entity_type and entity_id
        if entity_type == 'attorney':
            rates = self.rate_repository.get_by_attorney(entity_id, related_id, start_date, end_date)
        elif entity_type == 'client':
            rates = self.rate_repository.get_by_client(entity_id, related_id, start_date, end_date)
        elif entity_type == 'firm':
            rates = self.rate_repository.get_by_firm(entity_id, related_id, start_date, end_date)
        
        # Apply filtering by related_id if provided
        if related_id:
            rates = [rate for rate in rates if str(getattr(rate, entity_type + '_id')) == related_id]
        
        # Convert all rates to the specified currency
        converted_rates = []
        for rate in rates:
            converted_rate = convert_currency(rate.amount, rate.currency, currency)
            converted_rates.append({"effective_date": rate.effective_date, "amount": converted_rate})
        
        # Group data according to group_by parameter if provided (e.g., by staff_class, office, etc.)
        if group_by:
            grouped_rates = {}
            for rate in converted_rates:
                group_value = getattr(rate, group_by, 'Unknown')
                if group_value not in grouped_rates:
                    grouped_rates[group_value] = []
                grouped_rates[group_value].append(rate)
        else:
            grouped_rates = {'All': converted_rates}
        
        # Organize data into time series format suitable for visualization
        time_series_data = {}
        for group, rates in grouped_rates.items():
            time_series_data[group] = []
            for rate in rates:
                time_series_data[group].append({
                    "date": rate["effective_date"].isoformat(),
                    "value": float(rate["amount"])
                })
        
        # Include inflation/CPI data for comparison
        start_year = get_current_date().year - 5
        end_year = get_current_date().year
        inflation_data = self.get_inflation_for_period(start_year, end_year)
        
        # Return the formatted time series data
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "related_id": related_id,
            "group_by": group_by,
            "currency": currency,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "time_series_data": time_series_data,
            "inflation": inflation_data
        }

    def analyze_seasonal_patterns(self, entity_type: str, entity_id: str, years: Optional[int] = 5) -> dict:
        """
        Analyzes seasonal patterns in rate changes (e.g., timing of increases)
        
        Args:
            entity_type: Type of entity ('attorney', 'client', 'firm')
            entity_id: UUID of the entity
            years: Number of years to analyze
        
        Returns:
            Analysis of seasonal patterns in rate changes
        """
        # Retrieve historical rate data for the specified entity
        # Determine the timing of rate changes (month, quarter) over multiple years
        # Identify patterns in when rate changes typically occur
        # Calculate frequency statistics for rate change timing
        # Return the seasonal pattern analysis
        return {}

    def calculate_rate_distribution(self, rate_changes: List[float]) -> dict:
        """
        Calculates the distribution of rate increases across different percentile ranges
        
        Args:
            rate_changes: List of rate changes
        
        Returns:
            Rate change distribution statistics
        """
        # Calculate percentiles (10th, 25th, 50th, 75th, 90th) of rate changes
        # Determine the mean and median rate changes
        # Calculate standard deviation to measure variability
        # Create histogram data for visualization
        # Return the distribution statistics
        return {}

    def predict_future_rates(self, entity_type: str, entity_id: str, related_id: Optional[str] = None,
                                years_ahead: Optional[int] = 1, model_type: Optional[str] = 'linear') -> dict:
        """
        Predicts future rates based on historical trends using simple forecasting
        
        Args:
            entity_type: Type of entity ('attorney', 'client', 'firm')
            entity_id: UUID of the entity
            related_id: Optional UUID of a related entity (e.g., client for attorney trends)
            years_ahead: Number of years to forecast
            model_type: Type of forecasting model ('linear', 'exponential', etc.)
        
        Returns:
            Predicted future rates and confidence intervals
        """
        # Retrieve historical rate data for the entity
        # Apply the specified forecasting model (linear, exponential, etc.)
        # Calculate predicted rates for each year in the forecast period
        # Calculate confidence intervals for the predictions
        # Return the forecast data
        return {}

    def compare_with_market_indicators(self, rate_changes: List[float], years: List[int],
                                        indicators: Optional[List[str]] = None) -> dict:
        """
        Compares rate trends with relevant market indicators beyond CPI
        
        Args:
            rate_changes: List of rate changes
            years: List of years for the analysis
            indicators: List of market indicators to compare against (e.g., CPI, PPI_Legal)
        
        Returns:
            Comparison of rate trends with market indicators
        """
        # Retrieve data for each requested market indicator for the specified years
        # Calculate correlation between rate changes and each indicator
        # Create visualization data showing rates vs. indicators over time
        # Return the comparative analysis
        return {}