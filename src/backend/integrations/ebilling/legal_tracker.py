"""
Implementation of the Legal Tracker eBilling system integration adapter.
Provides functionality to connect to Legal Tracker's API, authenticate,
retrieve historical rate and billing data, and export approved rates.
"""

import requests  # Version: 2.28.1
import json
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple
import urllib.parse  # URL handling for API endpoints

from ..common.adapter import APIAdapter  # Base adapter class for API integrations
from ..common.client import BaseIntegrationClient  # Base client class for API interactions
from ..common.mapper import FieldMapper  # Field mapping between Legal Tracker and Justice Bid formats
from ...utils.constants import IntegrationType  # Integration type enumeration
from ...utils.logging import get_logger, log_api_request, log_api_response  # Logging utilities

# Initialize logger
logger = get_logger(__name__)

# Legal Tracker API Version
LEGAL_TRACKER_API_VERSION = "v1"

# Default page size for API requests
DEFAULT_PAGE_SIZE = 100

# Default field mappings between Legal Tracker and Justice Bid
DEFAULT_FIELD_MAPPINGS = {
    "attorney": {
        "timekeeper_id": "id",
        "first_name": "firstName",
        "last_name": "lastName",
        "email": "emailAddress",
        "role": "role",
        "office": "officeLocation",
        "practice_area": "practiceArea",
        "bar_date": "barAdmissionDate",
        "graduation_date": "graduationDate"
    },
    "rate": {
        "id": "rateId",
        "attorney_id": "timekeeperId",
        "amount": "rateAmount",
        "currency": "currencyCode",
        "effective_date": "effectiveDate",
        "expiration_date": "expirationDate",
        "status": "rateStatus",
        "rate_type": "rateType"
    },
    "matter": {
        "id": "matterId",
        "number": "matterNumber",
        "name": "matterName",
        "description": "matterDescription",
        "practice_area": "practiceArea",
        "status": "matterStatus",
        "open_date": "openDate"
    }
}

# Legal Tracker API endpoints
LEGAL_TRACKER_API_ENDPOINTS = {
    "rates": "/api/rates",
    "timekeepers": "/api/timekeepers",
    "matters": "/api/matters"
}


def create_legal_tracker_client(config: Dict) -> 'LegalTrackerClient':
    """
    Factory function to create a configured Legal Tracker client instance
    """
    # Validate required configuration parameters
    if not config.get('base_url'):
        raise ValueError("Legal Tracker base_url is required")
    if not config.get('api_key'):
        raise ValueError("Legal Tracker api_key is required")

    # Create and return a LegalTrackerClient instance with the provided configuration
    return LegalTrackerClient(config)


def create_legal_tracker_adapter(name: str, base_url: str, auth_credentials: Dict, headers: Dict, timeout: int, verify_ssl: bool) -> 'LegalTrackerAdapter':
    """
    Factory function to create a configured Legal Tracker adapter instance
    """
    # Create a client with the provided configuration
    client = LegalTrackerClient(
        config={
            'base_url': base_url,
            'auth_credentials': auth_credentials,
            'headers': headers,
            'timeout': timeout,
            'verify_ssl': verify_ssl
        }
    )

    # Create a mapper with default field mappings
    mapper = LegalTrackerMapper(field_mappings=DEFAULT_FIELD_MAPPINGS)

    # Create and return a LegalTrackerAdapter with the client and mapper
    return LegalTrackerAdapter(
        name=name,
        base_url=base_url,
        auth_credentials=auth_credentials,
        headers=headers,
        client=client,
        mapper=mapper
    )


class LegalTrackerClient(BaseIntegrationClient):
    """
    Client for interacting with the Legal Tracker API, handling authentication,
    requests, and response parsing
    """

    def __init__(self, config: Dict):
        """
        Initialize the Legal Tracker client with connection details
        """
        # Call parent constructor with configuration
        super().__init__(
            base_url=config.get('base_url'),
            auth_config=config.get('auth_credentials', {}),
            auth_method='api_key',
            headers=config.get('headers', {}),
            timeout=config.get('timeout', 30),
            max_retries=config.get('max_retries', 3),
            verify_ssl=config.get('verify_ssl', True)
        )

        # Set up base URL with API version
        self.base_url = f"{self.base_url.rstrip('/')}/{LEGAL_TRACKER_API_VERSION}"

        # Extract authentication credentials (api_key)
        self.api_key = self.auth_config.get('api_key')
        if not self.api_key:
            raise ValueError("Legal Tracker API key is required")

        # Set up endpoints dictionary
        self.endpoints = LEGAL_TRACKER_API_ENDPOINTS

        # Log client initialization
        logger.info(f"Initialized LegalTrackerClient for {self.base_url}")

    def authenticate(self) -> Dict:
        """
        Authenticate with the Legal Tracker API using API Key
        """
        # Create authentication headers using API key
        auth_headers = {'X-API-Key': self.api_key}

        # Return authentication headers
        return auth_headers

    def get_rates(self, params: Dict = None) -> Dict:
        """
        Retrieve rate data from Legal Tracker
        """
        # Authenticate with the API
        auth_headers = self.authenticate()

        # Construct query parameters with filters and pagination
        endpoint = self.endpoints['rates']
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Make a GET request to the rates endpoint
        response = self.get(endpoint, params=params, headers=auth_headers)

        # Process the response and handle pagination
        rates = self.handle_pagination(endpoint, params, response)

        # Return the complete rate data
        return rates

    def get_timekeepers(self, params: Dict = None) -> Dict:
        """
        Retrieve timekeeper (attorney) data from Legal Tracker
        """
        # Authenticate with the API
        auth_headers = self.authenticate()

        # Construct query parameters with filters and pagination
        endpoint = self.endpoints['timekeepers']
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Make a GET request to the timekeepers endpoint
        response = self.get(endpoint, params=params, headers=auth_headers)

        # Process the response and handle pagination
        timekeepers = self.handle_pagination(endpoint, params, response)

        # Return the complete timekeeper data
        return timekeepers

    def get_matters(self, params: Dict = None) -> Dict:
        """
        Retrieve matter data from Legal Tracker
        """
        # Authenticate with the API
        auth_headers = self.authenticate()

        # Construct query parameters with filters and pagination
        endpoint = self.endpoints['matters']
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Make a GET request to the matters endpoint
        response = self.get(endpoint, params=params, headers=auth_headers)

        # Process the response and handle pagination
        matters = self.handle_pagination(endpoint, params, response)

        # Return the complete matter data
        return matters

    def update_rates(self, rates_data: Dict) -> Dict:
        """
        Send updated rates to Legal Tracker
        """
        # Authenticate with the API
        auth_headers = self.authenticate()

        # Format the rates data for Legal Tracker
        endpoint = self.endpoints['rates']
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # If rate has ID, use PUT to update, otherwise use POST to create
        if rates_data.get('rateId'):
            response = self.put(endpoint, json_data=rates_data, headers=auth_headers)
        else:
            response = self.post(endpoint, json_data=rates_data, headers=auth_headers)

        # Process the response and handle any errors
        # Return the operation result
        return response

    def handle_pagination(self, endpoint: str, params: Dict, initial_response: Dict) -> list:
        """
        Handle paginated responses from Legal Tracker API
        """
        # Extract items from initial response
        items = initial_response.get('items', [])
        total_count = initial_response.get('total_count', 0)
        page_size = initial_response.get('page_size', DEFAULT_PAGE_SIZE)
        current_page = initial_response.get('current_page', 1)

        # Check if more pages exist based on total_count and current_page
        while len(items) < total_count:
            # Increment page number and make additional requests
            params['page'] = current_page + 1
            response = self.get(endpoint, params=params)
            items.extend(response.get('items', []))
            current_page += 1

        # Return the complete list of items from all pages
        return items

    def test_connection(self) -> bool:
        """
        Test the connection to Legal Tracker API
        """
        try:
            logger.info("Testing connection to Legal Tracker API")

            # Attempt to authenticate
            auth_headers = self.authenticate()

            # Make a simple request to verify API access
            response = self.get(self.endpoints['rates'], params={'page': 1, 'page_size': 1}, headers=auth_headers, raw_response=True)

            success = 200 <= response.status_code < 300
            log_level = logger.info if success else logger.error
            log_level(
                f"Connection test to Legal Tracker API {'succeeded' if success else 'failed'} "
                f"with status {response.status_code}",
                extra={'additional_data': {'status_code': response.status_code}}
            )

            return success

        except Exception as e:
            logger.error(
                f"Connection test to Legal Tracker API failed with exception: {str(e)}",
                extra={'additional_data': {'error': str(e), 'type': type(e).__name__}}
            )
            return False


class LegalTrackerMapper(FieldMapper):
    """
    Maps data between Legal Tracker format and Justice Bid format
    """

    def __init__(self, field_mappings: Dict):
        """
        Initialize the mapper with field mappings
        """
        # Call parent constructor with field mappings and default values
        super().__init__(mapping_config=field_mappings)

        # Set up specific transformations for Legal Tracker data
        self.date_format = "%Y-%m-%d"  # Legal Tracker date format

    def map_data(self, source_data: Dict, data_type: str) -> Dict:
        """
        Map data from Legal Tracker format to Justice Bid format
        """
        # Select appropriate mapping configuration based on data_type
        mapping_config = self.field_mappings.get(data_type)
        if not mapping_config:
            logger.warning(f"No mapping configuration found for data type '{data_type}'")
            return {}

        # Apply field mapping to source data
        mapped_data = {}
        for target_field, source_field in mapping_config.items():
            mapped_data[target_field] = source_data.get(source_field)

        # Apply specific transformations for Legal Tracker data format (dates, enums, etc.)
        if data_type == "rate":
            if mapped_data.get("effective_date"):
                mapped_data["effective_date"] = self.transform_date_format(mapped_data["effective_date"], "to_justice_bid")
            if mapped_data.get("expiration_date"):
                mapped_data["expiration_date"] = self.transform_date_format(mapped_data["expiration_date"], "to_justice_bid")
            if mapped_data.get("status"):
                mapped_data["status"] = self.transform_status(mapped_data["status"], "to_justice_bid")

        # Validate the mapped data
        # Return the mapped data
        return mapped_data

    def reverse_map_data(self, source_data: Dict, data_type: str) -> Dict:
        """
        Map data from Justice Bid format to Legal Tracker format
        """
        # Select appropriate mapping configuration based on data_type
        mapping_config = self.field_mappings.get(data_type)
        if not mapping_config:
            logger.warning(f"No reverse mapping configuration found for data type '{data_type}'")
            return {}

        # Apply reverse field mapping to source data
        mapped_data = {}
        for target_field, source_field in mapping_config.items():
            mapped_data[source_field] = source_data.get(target_field)

        # Apply specific transformations for Legal Tracker format requirements
        if data_type == "rate":
            if mapped_data.get("effective_date"):
                mapped_data["effective_date"] = self.transform_date_format(mapped_data["effective_date"], "to_legal_tracker")
            if mapped_data.get("expiration_date"):
                mapped_data["expiration_date"] = self.transform_date_format(mapped_data["expiration_date"], "to_legal_tracker")
            if mapped_data.get("status"):
                mapped_data["status"] = self.transform_status(mapped_data["status"], "to_legal_tracker")

        # Validate the mapped data
        # Return the mapped data
        return mapped_data

    def transform_date_format(self, date_str: str, direction: str) -> str:
        """
        Transform date format between Justice Bid and Legal Tracker
        """
        # Parse the input date string
        # Apply the appropriate format transformation based on direction
        if direction == "to_legal_tracker":
            # Format as expected by Legal Tracker API
            return datetime.strptime(date_str, "%Y-%m-%d").strftime(self.date_format)
        elif direction == "to_justice_bid":
            # Parse Legal Tracker date format and standardize
            return datetime.strptime(date_str, self.date_format).strftime("%Y-%m-%d")
        else:
            return date_str

    def transform_status(self, status: str, direction: str) -> str:
        """
        Transform status values between Justice Bid and Legal Tracker
        """
        # Map between Legal Tracker's status values and Justice Bid's status values
        legal_tracker_to_justice_bid = {
            "Approved": "approved",
            "Rejected": "rejected",
            "Pending": "pending_approval"
        }
        justice_bid_to_legal_tracker = {
            "approved": "Approved",
            "rejected": "Rejected",
            "pending_approval": "Pending"
        }

        # Convert Justice Bid status to Legal Tracker status
        if direction == "to_legal_tracker":
            return justice_bid_to_legal_tracker.get(status, "Unknown")
        # Convert Legal Tracker status to Justice Bid status
        elif direction == "to_justice_bid":
            return legal_tracker_to_justice_bid.get(status, "unknown")
        else:
            return status


class LegalTrackerAdapter(APIAdapter):
    """
    Adapter for the Legal Tracker eBilling system, implementing the specific integration details
    """

    def __init__(self, name: str, base_url: str, auth_credentials: Dict, headers: Dict, client: LegalTrackerClient, mapper: LegalTrackerMapper):
        """
        Initialize the Legal Tracker adapter with client and mapper
        """
        # Call parent constructor with base parameters
        super().__init__(
            name=name,
            integration_type=IntegrationType.EBILLING_LEGAL_TRACKER.value,
            base_url=base_url,
            auth_credentials=auth_credentials,
            headers=headers
        )

        # Store the Legal Tracker client instance
        self.client = client

        # Store the Legal Tracker mapper instance
        self.mapper = mapper

        # Log adapter initialization
        logger.info(f"Initialized LegalTrackerAdapter for {self.base_url}")

    def authenticate(self) -> bool:
        """
        Authenticate with the Legal Tracker API
        """
        # Delegate authentication to the client
        try:
            self.client.authenticate()
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False

    def validate_connection(self) -> bool:
        """
        Validate the connection to Legal Tracker
        """
        try:
            # Attempt to authenticate
            auth_headers = self.client.authenticate()

            # Make a simple API call to verify connectivity
            response = self.client.get(self.client.endpoints['rates'], params={'page': 1, 'page_size': 1}, headers=auth_headers, raw_response=True)

            # Handle any connection errors
            return 200 <= response.status_code < 300

        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False

    def get_data(self, data_type: str, params: Dict = None, headers: Dict = None) -> Dict:
        """
        Retrieve data from Legal Tracker
        """
        try:
            # Select appropriate client method based on data_type (rates, timekeepers, matters)
            if data_type == "rate":
                client_method = self.client.get_rates
            elif data_type == "attorney":
                client_method = self.client.get_timekeepers
            elif data_type == "matter":
                client_method = self.client.get_matters
            else:
                raise ValueError(f"Unsupported data type: {data_type}")

            # Call the client method with provided parameters
            response_data = client_method(params=params)

            # Map the response data to Justice Bid format using the mapper
            mapped_data = []
            for item in response_data:
                mapped_item = self.mapper.map_data(item, data_type)
                mapped_data.append(mapped_item)

            # Return the mapped data
            return mapped_data

        except Exception as e:
            logger.error(f"Error retrieving data: {str(e)}")
            return {}

    def send_data(self, data_type: str, data: Dict, params: Dict = None, headers: Dict = None) -> Dict:
        """
        Send data to Legal Tracker
        """
        try:
            # Map the data from Justice Bid format to Legal Tracker format
            mapped_data = self.mapper.reverse_map_data(data, data_type)

            # Select appropriate client method based on data_type
            if data_type == "rate":
                client_method = self.client.update_rates
            else:
                raise ValueError(f"Unsupported data type for sending data: {data_type}")

            # Call the client method with mapped data and parameters
            response = client_method(rates_data=mapped_data)

            # Return the response
            return response

        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")
            return {}

    def map_data(self, data: Dict, direction: str, data_type: str) -> Dict:
        """
        Map data between Legal Tracker and Justice Bid formats
        """
        # Determine mapping direction (to_justice_bid or to_legal_tracker)
        if direction == "to_justice_bid":
            # Call the appropriate mapper method based on direction
            mapped_data = self.mapper.map_data(data, data_type)
        elif direction == "to_legal_tracker":
            # Call the appropriate mapper method based on direction
            mapped_data = self.mapper.reverse_map_data(data, data_type)
        else:
            raise ValueError(f"Invalid mapping direction: {direction}")

        # Return the mapped data
        return mapped_data

    def get_historical_rates(self, filters: Dict = None) -> Dict:
        """
        Retrieve historical rate data from Legal Tracker
        """
        # Prepare query parameters with filters
        params = filters or {}

        # Call get_data with data_type='rate'
        rate_data = self.get_data(data_type='rate', params=params)

        # Process and return the rate data
        return rate_data

    def get_attorneys(self, filters: Dict = None) -> Dict:
        """
        Retrieve attorney (timekeeper) data from Legal Tracker
        """
        # Prepare query parameters with filters
        params = filters or {}

        # Call get_data with data_type='attorney'
        attorney_data = self.get_data(data_type='attorney', params=params)

        # Process and return the attorney data
        return attorney_data

    def get_matters(self, filters: Dict = None) -> Dict:
        """
        Retrieve matter data from Legal Tracker
        """
        # Prepare query parameters with filters
        params = filters or {}

        # Call get_data with data_type='matter'
        matter_data = self.get_data(data_type='matter', params=params)

        # Process and return the matter data
        return matter_data

    def export_approved_rates(self, rates_data: Dict) -> Dict:
        """
        Export approved rates to Legal Tracker
        """
        # Validate the rates data structure
        # Call send_data with data_type='rate'
        export_result = self.send_data(data_type='rate', data=rates_data)

        # Handle any export errors
        # Return the export result with success and error counts
        return export_result

    def import_file(self, file_path: str, data_type: str, mapping_config: Dict) -> Tuple[bool, str, List]:
        """
        Import data from a file exported from Legal Tracker
        """
        # Determine file format based on extension (CSV, Excel, etc.)
        # Read and parse the file content
        # Apply mapping using provided mapping_config or default mappings
        # Transform data to Justice Bid format
        # Return success status, message, and imported data
        return super().import_file(file_path, data_type, mapping_config)

    def export_file(self, file_path: str, data_type: str, data: List, mapping_config: Dict) -> Tuple[bool, str]:
        """
        Export data to a file for import into Legal Tracker
        """
        # Determine output format based on file_path extension
        # Map data to Legal Tracker format using mapping_config or default mappings
        # Write the transformed data to the specified file
        # Return success status and message
        return super().export_file(file_path, data_type, data, mapping_config)