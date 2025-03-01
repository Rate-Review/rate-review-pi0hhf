"""
Service for analyzing and retrieving attorney performance metrics from billing data, external UniCourt data, and user ratings.
"""

import typing
from typing import List, Dict, Any, Tuple, Optional
import uuid
from datetime import datetime, date

import logging  # Version: standard library
import pandas  # Version: 2.0+
import numpy  # Version: 1.24+

from src.backend.db.repositories import attorney_repository  # Purpose: Data access for attorney records
from src.backend.db.repositories import billing_repository  # Purpose: Data access for billing history and performance data
from src.backend.db.repositories import rate_repository  # Purpose: Data access for attorney rate information
from src.backend.integrations.unicourt import client as unicourt_client  # Purpose: Access to UniCourt API for attorney performance data
from src.backend.integrations.unicourt import mapper as unicourt_mapper  # Purpose: Mapping between Justice Bid and UniCourt data structures
from src.backend.utils import datetime_utils  # Purpose: Date handling utilities for performance period calculations
from src.backend.utils import cache  # Purpose: Caching performance metrics for improved performance
from src.backend.utils import validators  # Purpose: Input validation for performance analysis parameters

# Initialize logger
logger = logging.getLogger(__name__)


class AttorneyPerformanceService:
    """
    Service class for analyzing and retrieving attorney performance metrics.
    """

    def __init__(self, attorney_repository: attorney_repository.AttorneyRepository,
                 billing_repository: billing_repository.BillingRepository,
                 rate_repository: rate_repository.RateRepository,
                 unicourt_client: unicourt_client.UniCourtClient,
                 unicourt_mapper: unicourt_mapper.UniCourtMapper):
        """
        Initializes the AttorneyPerformanceService with required repositories and clients.

        Args:
            attorney_repository: Repository for attorney data.
            billing_repository: Repository for billing data.
            rate_repository: Repository for rate data.
            unicourt_client: Client for UniCourt API.
            unicourt_mapper: Mapper for UniCourt data.
        """
        self._attorney_repository = attorney_repository
        self._billing_repository = billing_repository
        self._rate_repository = rate_repository
        self._unicourt_client = unicourt_client
        self._unicourt_mapper = unicourt_mapper
        self._logger = logger

    @cache.cache_result(ttl=3600)
    def get_billing_performance(self, attorney_id: str, client_id: Optional[str] = None,
                                start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """
        Retrieves and analyzes attorney performance metrics based on billing data.

        Args:
            attorney_id: UUID of the attorney.
            client_id: Optional UUID of the client.
            start_date: Optional start date for the performance period.
            end_date: Optional end date for the performance period.

        Returns:
            Dictionary containing billing performance metrics.
        """
        try:
            # Validate input parameters
            validators.validate_uuid(attorney_id, "attorney_id")
            if client_id:
                validators.validate_uuid(client_id, "client_id")
            if start_date and end_date:
                validators.validate_date_range(start_date, end_date, "start_date", "end_date")

            # Retrieve billing data for the attorney from the BillingRepository
            billing_data = self._billing_repository.get_by_attorney(
                attorney_id=uuid.UUID(attorney_id),
                start_date=start_date,
                end_date=end_date,
                client_id=uuid.UUID(client_id) if client_id else None
            )

            # Calculate performance metrics
            total_hours = sum(record.hours for record in billing_data) if billing_data else 0
            total_fees = sum(record.fees for record in billing_data) if billing_data else 0
            matter_count = len(set(record.matter_id for record in billing_data if record.matter_id)) if billing_data else 0

            # Calculate utilization rate (example: assuming 8 hours/day, 5 days/week)
            if start_date and end_date:
                working_days = numpy.busday_count(start_date, end_date)
                available_hours = working_days * 8
                utilization_rate = (total_hours / available_hours) * 100 if available_hours > 0 else 0
            else:
                utilization_rate = 0

            # Calculate average hourly rate
            average_hourly_rate = total_fees / total_hours if total_hours > 0 else 0

            # Calculate efficiency metric (hours per matter)
            efficiency = total_hours / matter_count if matter_count > 0 else 0

            # Calculate realization rate (example: assuming a target rate)
            target_rate = 700  # Example target rate
            realization_rate = (average_hourly_rate / target_rate) * 100 if target_rate > 0 else 0

            # Compile metrics dictionary
            metrics = {
                "total_hours": float(total_hours),
                "total_fees": float(total_fees),
                "matter_count": matter_count,
                "utilization_rate": float(utilization_rate),
                "average_hourly_rate": float(average_hourly_rate),
                "efficiency": float(efficiency),
                "realization_rate": float(realization_rate)
            }

            return metrics

        except Exception as e:
            self._logger.error(f"Error retrieving billing performance: {str(e)}")
            raise

    @cache.cache_result(ttl=86400)
    def get_unicourt_performance(self, attorney_id: str) -> Dict:
        """
        Retrieves attorney performance data from UniCourt API.

        Args:
            attorney_id: UUID of the attorney.

        Returns:
            Dictionary containing UniCourt performance metrics.
        """
        try:
            # Validate attorney_id
            validators.validate_uuid(attorney_id, "attorney_id")

            # Retrieve attorney record to get UniCourt ID mapping
            attorney = self._attorney_repository.get_by_id(attorney_id)
            if not attorney:
                self._logger.warning(f"Attorney with ID {attorney_id} not found")
                return {}

            unicourt_id = attorney.unicourt_id
            if not unicourt_id:
                self._logger.warning(f"No UniCourt ID found for attorney {attorney_id}")
                return {}

            # Call UniCourtClient to fetch performance data
            raw_performance_data = self._unicourt_client.get_attorney_performance(str(unicourt_id))

            # Process and transform raw UniCourt data using UniCourtMapper
            performance_metrics = self._unicourt_mapper.transform_performance_metrics(raw_performance_data)

            # Calculate performance metrics (win rate, case complexity, etc.)
            # (Implementation depends on the structure of UniCourt data)

            # Compile metrics dictionary
            metrics = {
                "win_rate": performance_metrics.get("metrics", {}).get("win_rate", 0.0),
                "case_complexity": performance_metrics.get("metrics", {}).get("case_complexity", 0),
                # Add other metrics as needed
            }

            return metrics

        except Exception as e:
            self._logger.error(f"Error retrieving UniCourt performance: {str(e)}")
            return {}

    @cache.cache_result(ttl=3600)
    def get_client_ratings(self, attorney_id: str, client_id: Optional[str] = None) -> Dict:
        """
        Retrieves client ratings and feedback for an attorney.

        Args:
            attorney_id: UUID of the attorney.
            client_id: Optional UUID of the client.

        Returns:
            Dictionary containing rating metrics and feedback.
        """
        try:
            # Validate input parameters
            validators.validate_uuid(attorney_id, "attorney_id")
            if client_id:
                validators.validate_uuid(client_id, "client_id")

            # Retrieve attorney ratings from AttorneyRepository
            attorney, rates = self._attorney_repository.get_with_rates(attorney_id, client_id)

            # Calculate average rating and rating distribution
            total_rating = 0
            rating_count = 0
            for rate in rates:
                if rate.history and isinstance(rate.history, list):
                    for entry in rate.history:
                        if 'rating' in entry:
                            try:
                                total_rating += float(entry['rating'])
                                rating_count += 1
                            except ValueError:
                                self._logger.warning(f"Invalid rating value: {entry['rating']}")

            average_rating = total_rating / rating_count if rating_count > 0 else 0

            # Compile feedback comments (if requested and available)
            feedback_comments = []
            for rate in rates:
                if rate.history and isinstance(rate.history, list):
                    for entry in rate.history:
                        if 'feedback' in entry:
                            feedback_comments.append(entry['feedback'])

            # Compile ratings dictionary
            ratings = {
                "average_rating": float(average_rating),
                "rating_count": rating_count,
                "feedback_comments": feedback_comments
            }

            return ratings

        except Exception as e:
            self._logger.error(f"Error retrieving client ratings: {str(e)}")
            raise

    def compare_to_rates(self, attorney_id: str, client_id: Optional[str] = None,
                         as_of_date: Optional[datetime] = None) -> Dict:
        """
        Compares attorney performance metrics against their billing rates.

        Args:
            attorney_id: UUID of the attorney.
            client_id: Optional UUID of the client.
            as_of_date: Optional date to compare rates as of.

        Returns:
            Dictionary containing value metrics.
        """
        try:
            # Validate input parameters
            validators.validate_uuid(attorney_id, "attorney_id")
            if client_id:
                validators.validate_uuid(client_id, "client_id")

            # Retrieve attorney performance metrics using get_attorney_billing_performance
            performance_metrics = self.get_billing_performance(attorney_id, client_id)

            # Retrieve attorney rate information from RateRepository
            rates = self._rate_repository.get_by_attorney(attorney_id, client_id, as_of_date)

            # Calculate performance-to-rate ratios (value metrics)
            # (Implementation depends on the structure of Rate model and performance metrics)

            # Compare with peer averages if available
            # (Implementation depends on the availability of peer data)

            # Compile value metrics dictionary
            value_metrics = {
                "value_score": 0.0,  # Placeholder
                # Add other value metrics as needed
            }

            return value_metrics

        except Exception as e:
            self._logger.error(f"Error comparing performance to rates: {str(e)}")
            raise

    def get_comprehensive_metrics(self, attorney_id: str, client_id: Optional[str] = None,
                                  start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                                  include_unicourt: bool = True, include_ratings: bool = True,
                                  include_rate_comparison: bool = True) -> Dict:
        """
        Retrieves comprehensive performance metrics from all available sources.

        Args:
            attorney_id: UUID of the attorney.
            client_id: Optional UUID of the client.
            start_date: Optional start date for the performance period.
            end_date: Optional end date for the performance period.
            include_unicourt: Whether to include UniCourt data.
            include_ratings: Whether to include client ratings.
            include_rate_comparison: Whether to include rate comparison.

        Returns:
            Comprehensive dictionary containing all requested performance metrics.
        """
        try:
            # Validate input parameters
            validators.validate_uuid(attorney_id, "attorney_id")
            if client_id:
                validators.validate_uuid(client_id, "client_id")
            if start_date and end_date:
                validators.validate_date_range(start_date, end_date, "start_date", "end_date")

            # Initialize comprehensive metrics dictionary
            comprehensive_metrics = {}

            # Add billing performance metrics
            comprehensive_metrics["billing_performance"] = self.get_billing_performance(
                attorney_id, client_id, start_date, end_date
            )

            # Add UniCourt metrics if requested
            if include_unicourt:
                comprehensive_metrics["unicourt_performance"] = self.get_unicourt_performance(attorney_id)

            # Add ratings metrics if requested
            if include_ratings:
                comprehensive_metrics["client_ratings"] = self.get_client_ratings(attorney_id, client_id)

            # Add value metrics if requested
            if include_rate_comparison:
                comprehensive_metrics["value_metrics"] = self.compare_to_rates(attorney_id, client_id, end_date)

            # Calculate overall performance score based on available metrics
            # (Implementation depends on the specific scoring algorithm)
            comprehensive_metrics["overall_score"] = 0.0  # Placeholder

            return comprehensive_metrics

        except Exception as e:
            self._logger.error(f"Error retrieving comprehensive metrics: {str(e)}")
            raise

    def find_top_performers(self, client_id: Optional[str] = None, firm_id: Optional[str] = None,
                            practice_area: Optional[str] = None, staff_class_id: Optional[str] = None,
                            start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                            metrics: Optional[List[str]] = None, limit: int = 10) -> List[Dict]:
        """
        Identifies top-performing attorneys based on specified criteria.

        Args:
            client_id: Optional UUID of the client.
            firm_id: Optional UUID of the law firm.
            practice_area: Optional practice area.
            staff_class_id: Optional UUID of the staff class.
            start_date: Optional start date for the performance period.
            end_date: Optional end date for the performance period.
            metrics: Optional list of metrics to consider.
            limit: Maximum number of attorneys to return.

        Returns:
            List of top-performing attorneys with metrics.
        """
        try:
            # Validate input parameters
            if client_id:
                validators.validate_uuid(client_id, "client_id")
            if firm_id:
                validators.validate_uuid(firm_id, "firm_id")
            if staff_class_id:
                validators.validate_uuid(staff_class_id, "staff_class_id")
            if start_date and end_date:
                validators.validate_date_range(start_date, end_date, "start_date", "end_date")
            validators.validate_integer(limit, "limit", min_value=1, max_value=100)

            # Build query parameters for repository based on inputs
            search_params = {
                "organization_id": firm_id,
                "staff_class_id": staff_class_id,
                # Add other search parameters as needed
            }

            # Retrieve candidate attorneys from AttorneyRepository
            attorneys, _ = self._attorney_repository.search(search_params)

            # For each attorney, calculate performance metrics based on requested criteria
            attorney_metrics = []
            for attorney in attorneys:
                comprehensive_metrics = self.get_comprehensive_metrics(
                    str(attorney.id), client_id, start_date, end_date,
                    include_unicourt=True, include_ratings=True, include_rate_comparison=True
                )
                attorney_metrics.append({"attorney": attorney, "metrics": comprehensive_metrics})

            # Score attorneys based on specified metrics
            # (Implementation depends on the specific scoring algorithm)

            # Sort attorneys by overall score
            sorted_attorneys = sorted(attorney_metrics, key=lambda x: x["metrics"].get("overall_score", 0.0), reverse=True)

            # Return top attorneys limited by the limit parameter
            top_attorneys = sorted_attorneys[:limit]

            # Format the results
            formatted_results = []
            for item in top_attorneys:
                attorney_data = item["attorney"].to_dict()
                attorney_data["metrics"] = item["metrics"]
                formatted_results.append(attorney_data)

            return formatted_results

        except Exception as e:
            self._logger.error(f"Error finding top-performing attorneys: {str(e)}")
            raise

    def get_trends(self, attorney_id: str, client_id: Optional[str] = None,
                   start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                   period: str = "monthly") -> Dict:
        """
        Analyzes performance trends for an attorney over time.

        Args:
            attorney_id: UUID of the attorney.
            client_id: Optional UUID of the client.
            start_date: Optional start date for the trend period.
            end_date: Optional end date for the trend period.
            period: Time period for trend analysis (monthly, quarterly, yearly).

        Returns:
            Dictionary containing performance metrics over time periods.
        """
        try:
            # Validate input parameters
            validators.validate_uuid(attorney_id, "attorney_id")
            if client_id:
                validators.validate_uuid(client_id, "client_id")
            if start_date and end_date:
                validators.validate_date_range(start_date, end_date, "start_date", "end_date")

            # Determine time periods based on period parameter (monthly, quarterly, yearly)
            # (Implementation depends on the specific time period logic)

            # For each time period, retrieve performance metrics
            # (Implementation depends on the specific data retrieval logic)

            # Organize metrics by time period
            # (Implementation depends on the specific data organization logic)

            # Calculate trend indicators (improving, declining, stable)
            # (Implementation depends on the specific trend calculation logic)

            # Return time-series performance data
            trends = {
                "period1": {"total_hours": 100, "total_fees": 50000},
                "period2": {"total_hours": 120, "total_fees": 60000},
                # Add other periods as needed
            }

            return trends

        except Exception as e:
            self._logger.error(f"Error analyzing performance trends: {str(e)}")
            raise


@cache.cache_result(ttl=3600)
def get_attorney_billing_performance(attorney_id: str, client_id: Optional[str] = None,
                                start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
    """Retrieves and analyzes attorney performance metrics based on billing data."""
    with session_scope() as session:
        repo = AttorneyPerformanceService(attorney_repository.AttorneyRepository(session),
                                        billing_repository.BillingRepository(session),
                                        rate_repository.RateRepository(session),
                                        unicourt_client.UniCourtClient("test"),
                                        unicourt_mapper.UniCourtMapper())
        return repo.get_billing_performance(attorney_id, client_id, start_date, end_date)

@cache.cache_result(ttl=86400)
def get_attorney_unicourt_performance(attorney_id: str) -> Dict:
    """Retrieves attorney performance data from UniCourt API."""
    with session_scope() as session:
        repo = AttorneyPerformanceService(attorney_repository.AttorneyRepository(session),
                                        billing_repository.BillingRepository(session),
                                        rate_repository.RateRepository(session),
                                        unicourt_client.UniCourtClient("test"),
                                        unicourt_mapper.UniCourtMapper())
        return repo.get_unicourt_performance(attorney_id)

@cache.cache_result(ttl=3600)
def get_attorney_ratings(attorney_id: str, client_id: Optional[str] = None) -> Dict:
    """Retrieves client ratings and feedback for an attorney."""
    with session_scope() as session:
        repo = AttorneyPerformanceService(attorney_repository.AttorneyRepository(session),
                                        billing_repository.BillingRepository(session),
                                        rate_repository.RateRepository(session),
                                        unicourt_client.UniCourtClient("test"),
                                        unicourt_mapper.UniCourtMapper())
        return repo.get_client_ratings(attorney_id, client_id)

def compare_performance_to_rates(attorney_id: str, client_id: Optional[str] = None,
                         as_of_date: Optional[datetime] = None) -> Dict:
    """Compares attorney performance metrics against their billing rates."""
    with session_scope() as session:
        repo = AttorneyPerformanceService(attorney_repository.AttorneyRepository(session),
                                        billing_repository.BillingRepository(session),
                                        rate_repository.RateRepository(session),
                                        unicourt_client.UniCourtClient("test"),
                                        unicourt_mapper.UniCourtMapper())
        return repo.compare_to_rates(attorney_id, client_id, as_of_date)

def get_comprehensive_performance(attorney_id: str, client_id: Optional[str] = None,
                          start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                          include_unicourt: bool = True, include_ratings: bool = True,
                          include_rate_comparison: bool = True) -> Dict:
    """Retrieves comprehensive performance metrics from all available sources."""
    with session_scope() as session:
        repo = AttorneyPerformanceService(attorney_repository.AttorneyRepository(session),
                                        billing_repository.BillingRepository(session),
                                        rate_repository.RateRepository(session),
                                        unicourt_client.UniCourtClient("test"),
                                        unicourt_mapper.UniCourtMapper())
        return repo.get_comprehensive_metrics(attorney_id, client_id, start_date, end_date, include_unicourt, include_ratings, include_rate_comparison)

def find_top_performing_attorneys(client_id: Optional[str] = None, firm_id: Optional[str] = None,
                        practice_area: Optional[str] = None, staff_class_id: Optional[str] = None,
                        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                        metrics: Optional[List[str]] = None, limit: int = 10) -> List[Dict]:
    """Identifies top-performing attorneys based on specified criteria."""
    with session_scope() as session:
        repo = AttorneyPerformanceService(attorney_repository.AttorneyRepository(session),
                                        billing_repository.BillingRepository(session),
                                        rate_repository.RateRepository(session),
                                        unicourt_client.UniCourtClient("test"),
                                        unicourt_mapper.UniCourtMapper())
        return repo.find_top_performers(client_id, firm_id, practice_area, staff_class_id, start_date, end_date, metrics, limit)

def get_performance_trends(attorney_id: str, client_id: Optional[str] = None,
                   start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                   period: str = "monthly") -> Dict:
    """Analyzes performance trends for an attorney over time."""
    with session_scope() as session:
        repo = AttorneyPerformanceService(attorney_repository.AttorneyRepository(session),
                                        billing_repository.BillingRepository(session),
                                        rate_repository.RateRepository(session),
                                        unicourt_client.UniCourtClient("test"),
                                        unicourt_mapper.UniCourtMapper())
        return repo.get_trends(attorney_id, client_id, start_date, end_date, period)