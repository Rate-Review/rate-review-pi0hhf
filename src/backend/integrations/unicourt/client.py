"""
Client for the UniCourt API to retrieve attorney performance data and case information.
Handles API authentication, request/response processing, error handling, and data mapping.
"""

import requests  # Version: 2.28.2
import datetime  # Version: standard library
import logging  # Version: standard library
import json  # Version: standard library
import os  # Version: standard library
import time  # Version: standard library
import backoff  # Version: 2.2.1

from src.backend.integrations.common.client import APIClient
from src.backend.integrations.unicourt.mapper import map_attorney_data
from src.backend.integrations.unicourt.mapper import map_case_data
from src.backend.integrations.unicourt.mapper import map_performance_data
from src.backend.db.repositories.attorney_repository import get_attorney_by_unicourt_id
from src.backend.db.repositories.attorney_repository import update_attorney_performance_data

# Define global constants for UniCourt API
UNICOURT_API_BASE_URL = "https://api.unicourt.com"
UNICOURT_API_VERSION = "v1"
UNICOURT_RATE_LIMIT = 60

# Initialize logger
logger = logging.getLogger(__name__)


class UniCourtClient(APIClient):
    """
    Client for the UniCourt API to retrieve attorney performance data and case information.
    """

    def __init__(self, api_key: str, base_url: str = UNICOURT_API_BASE_URL, api_version: str = UNICOURT_API_VERSION):
        """
        Initialize the UniCourt API client with credentials and configuration.

        Args:
            api_key: The API key for accessing the UniCourt API.
            base_url: The base URL for the UniCourt API.
            api_version: The API version to use.
        """
        # Call parent constructor
        super().__init__(base_url=base_url, auth_config={'api_key': api_key}, auth_method='api_key')

        # Set API key, base URL and version
        self.api_key = api_key
        self.base_url = base_url
        self.api_version = api_version

        # Initialize session headers with authentication
        self.session_headers = {
            "X-UC-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        # Create requests session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.session_headers)

        # Set up logging
        self.logger = logger

        # Initialize rate limiting properties
        self.last_request_time = 0.0
        self.rate_limit_wait = 60.0 / UNICOURT_RATE_LIMIT  # Minimum time between requests

    def search_attorneys(self, name: str = None, bar_number: str = None, state: str = None, additional_params: dict = None) -> list:
        """
        Search for attorneys in UniCourt based on name, bar number, or other criteria.

        Args:
            name: The name of the attorney to search for.
            bar_number: The bar number of the attorney to search for.
            state: The state in which the attorney is licensed.
            additional_params: Additional search parameters to include in the request.

        Returns:
            A list of attorney search results.
        """
        # Construct search parameters from input
        params = {}
        if name:
            params["name"] = name
        if bar_number:
            params["bar_number"] = bar_number
        if state:
            params["state"] = state
        if additional_params:
            params.update(additional_params)

        # Build API endpoint URL for attorney search
        endpoint = f"{self.api_version}/attorneys"

        # Make GET request to UniCourt API with search parameters
        response = self.make_request(method="GET", endpoint=endpoint, params=params)

        # Handle pagination if needed
        attorneys = response.get("attorneys", [])
        while response.get("next_page_url"):
            next_page_url = response["next_page_url"]
            response = self.make_request(method="GET", endpoint=next_page_url)
            attorneys.extend(response.get("attorneys", []))

        # Process response using mapper functions
        attorney_list = [map_attorney_data(attorney) for attorney in attorneys]

        # Return list of attorney data objects
        return attorney_list

    def get_attorney_details(self, attorney_id: str) -> dict:
        """
        Retrieve detailed information about an attorney by UniCourt ID.

        Args:
            attorney_id: The UniCourt ID of the attorney.

        Returns:
            Attorney details formatted for Justice Bid.
        """
        # Build API endpoint URL for attorney details
        endpoint = f"{self.api_version}/attorneys/{attorney_id}"

        # Make GET request to UniCourt API
        response = self.make_request(method="GET", endpoint=endpoint)

        # Handle potential API errors
        if not response:
            self.logger.warning(f"No attorney details found for UniCourt ID: {attorney_id}")
            return None

        # Process response using map_attorney_data function
        attorney_details = map_attorney_data(response)

        # Return formatted attorney details
        return attorney_details

    def get_attorney_cases(self, attorney_id: str, limit: int = 100, page: int = 1) -> list:
        """
        Retrieve case history for an attorney by UniCourt ID.

        Args:
            attorney_id: The UniCourt ID of the attorney.
            limit: The number of cases to retrieve per page.
            page: The page number to retrieve.

        Returns:
            A list of case data objects.
        """
        # Build API endpoint URL for attorney cases
        endpoint = f"{self.api_version}/attorneys/{attorney_id}/cases"

        # Set up pagination parameters
        params = {
            "limit": limit,
            "page": page,
        }

        # Make GET request to UniCourt API
        response = self.make_request(method="GET", endpoint=endpoint, params=params)

        # Handle potential API errors and pagination
        if not response:
            self.logger.warning(f"No cases found for UniCourt ID: {attorney_id}")
            return []

        # Process response using map_case_data function
        cases = [map_case_data(case) for case in response.get("cases", [])]

        # Return list of case data objects
        return cases

    def get_attorney_performance(self, attorney_id: str) -> dict:
        """
        Retrieve performance metrics for an attorney by UniCourt ID.

        Args:
            attorney_id: The UniCourt ID of the attorney.

        Returns:
            Performance metrics formatted for Justice Bid.
        """
        # Build API endpoint URL for attorney analytics
        endpoint = f"{self.api_version}/analytics/attorneys/{attorney_id}"

        # Make GET request to UniCourt API
        response = self.make_request(method="GET", endpoint=endpoint)

        # Handle potential API errors
        if not response:
            self.logger.warning(f"No performance data found for UniCourt ID: {attorney_id}")
            return None

        # Process response using map_performance_data function
        performance_metrics = map_performance_data(response)

        # Return formatted performance metrics
        return performance_metrics

    def sync_attorney_data(self, justice_bid_attorney_id: str, unicourt_attorney_id: str) -> bool:
        """
        Synchronize attorney data between UniCourt and Justice Bid.

        Args:
            justice_bid_attorney_id: The Justice Bid ID of the attorney.
            unicourt_attorney_id: The UniCourt ID of the attorney.

        Returns:
            Success status of synchronization.
        """
        try:
            # Retrieve attorney details from UniCourt
            attorney_details = self.get_attorney_details(unicourt_attorney_id)
            if not attorney_details:
                self.logger.warning(f"Could not retrieve attorney details from UniCourt for ID: {unicourt_attorney_id}")
                return False

            # Retrieve attorney cases from UniCourt
            attorney_cases = self.get_attorney_cases(unicourt_attorney_id)
            if not attorney_cases:
                self.logger.warning(f"Could not retrieve attorney cases from UniCourt for ID: {unicourt_attorney_id}")

            # Retrieve attorney performance metrics from UniCourt
            performance_metrics = self.get_attorney_performance(unicourt_attorney_id)
            if not performance_metrics:
                self.logger.warning(f"Could not retrieve attorney performance metrics from UniCourt for ID: {unicourt_attorney_id}")

            # Update attorney record in Justice Bid database
            attorney_repository = get_attorney_by_unicourt_id(unicourt_attorney_id)
            if attorney_repository:
                update_attorney_performance_data(justice_bid_attorney_id, performance_metrics)
                self.logger.info(f"Successfully synchronized attorney data for Justice Bid ID: {justice_bid_attorney_id} and UniCourt ID: {unicourt_attorney_id}")
                return True
            else:
                self.logger.error(f"Could not find attorney in Justice Bid with UniCourt ID: {unicourt_attorney_id}")
                return False

        except Exception as e:
            self.logger.error(f"Error synchronizing attorney data for Justice Bid ID: {justice_bid_attorney_id} and UniCourt ID: {unicourt_attorney_id}: {str(e)}")
            return False

    def bulk_sync_attorneys(self, attorney_mapping: list) -> dict:
        """
        Synchronize data for multiple attorneys in batch.

        Args:
            attorney_mapping: A list of dictionaries containing Justice Bid and UniCourt attorney IDs.

        Returns:
            A summary of the synchronization results.
        """
        success_count = 0
        failure_count = 0

        for mapping in attorney_mapping:
            justice_bid_attorney_id = mapping.get("justice_bid_attorney_id")
            unicourt_attorney_id = mapping.get("unicourt_attorney_id")

            try:
                # Call sync_attorney_data for each mapping
                success = self.sync_attorney_data(justice_bid_attorney_id, unicourt_attorney_id)
                if success:
                    success_count += 1
                else:
                    failure_count += 1

                # Handle rate limiting between requests
                time.sleep(self.rate_limit_wait)

            except Exception as e:
                self.logger.error(f"Error synchronizing attorney data for Justice Bid ID: {justice_bid_attorney_id} and UniCourt ID: {unicourt_attorney_id}: {str(e)}")
                failure_count += 1

        # Return summary of synchronization results
        return {"success_count": success_count, "failure_count": failure_count}

    def _handle_rate_limiting(self):
        """
        Internal method to handle API rate limiting.
        """
        # Calculate time since last request
        elapsed_time = time.time() - self.last_request_time

        # If time is less than rate limit wait time, sleep for remaining time
        if elapsed_time < self.rate_limit_wait:
            wait_time = self.rate_limit_wait - elapsed_time
            time.sleep(wait_time)

        # Update last request time
        self.last_request_time = time.time()

    def _build_url(self, endpoint: str) -> str:
        """
        Internal method to build UniCourt API URLs.

        Args:
            endpoint: The API endpoint.

        Returns:
            The full API URL.
        """
        # Combine base URL, API version, and endpoint
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return url

    def make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None, headers: dict = None) -> dict:
        """
        Make a request to the UniCourt API with rate limiting and error handling.

        Args:
            method: The HTTP method to use.
            endpoint: The API endpoint to request.
            params: The query parameters to include in the request.
            data: The data to include in the request body.
            headers: The headers to include in the request.

        Returns:
            The API response as a dictionary.
        """
        # Handle rate limiting
        self._handle_rate_limiting()

        # Build full API URL
        url = self._build_url(endpoint)

        # Merge default headers with custom headers
        request_headers = self.session_headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            # Make HTTP request using session
            response = self.session.request(method=method, url=url, params=params, json=data, headers=request_headers)

            # Raise HTTPError for bad responses
            response.raise_for_status()

            # Return parsed response data
            return response.json()

        except requests.exceptions.RequestException as e:
            # Handle potential HTTP and API errors
            self.logger.error(f"Request to UniCourt API failed: {str(e)}")
            raise

    def authenticate(self) -> bool:
        """
        Authenticate with the UniCourt API.

        Returns:
            True if authentication is successful, False otherwise.
        """
        # Authentication is handled via the X-UC-API-KEY header, so this method is not needed
        return True