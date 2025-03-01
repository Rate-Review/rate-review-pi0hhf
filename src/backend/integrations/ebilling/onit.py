"""
Implementation of the Onit eBilling system integration adapter. Provides functionality to connect to Onit's API,
authenticate, retrieve historical rate and billing data, and export approved rates.
"""

import requests  # Package version: 2.28.1
from oauthlib.oauth2 import BackendApplicationClient  # Package version: 3.2.0
from requests_oauthlib import OAuth2Session  # Package version: 1.3.1
import json  # Package version: standard library
from datetime import datetime  # Package version: standard library
from typing import Dict, List  # Package version: standard library
from urllib.parse import urljoin  # Package version: standard library

from ..common.adapter import APIAdapter, BaseAPIAdapter  # Internal import
from ..common.client import BaseIntegrationClient  # Internal import
from ..common.mapper import FieldMapper  # Internal import
from ...utils.constants import IntegrationType  # Internal import
from ...utils.logging import get_logger  # Internal import

# Initialize logger
logger = get_logger(__name__)

# Onit API version
ONIT_API_VERSION = "v1"

# Default page size for Onit API
DEFAULT_PAGE_SIZE = 100

# Default field mappings between Justice Bid and Onit
DEFAULT_FIELD_MAPPINGS = {
    "attorney": {
        "timekeeper_id": "id",
        "first_name": "firstName",
        "last_name": "lastName",
        "email": "emailAddress",
        "role": "role",
        "office": "office",
        "practice_area": "practiceArea",
        "bar_date": "barAdmission",
        "graduation_date": "gradYear"
    },
    "rate": {
        "id": "rateId",
        "attorney_id": "timekeeperId",
        "amount": "amount",
        "currency": "currency",
        "effective_date": "effectiveDate",
        "expiration_date": "expirationDate",
        "status": "status",
        "rate_type": "type"
    },
    "invoice": {
        "id": "invoiceId",
        "matter_id": "matterId",
        "number": "invoiceNumber",
        "date": "invoiceDate",
        "total_amount": "totalAmount",
        "currency": "currency",
        "line_items": "lineItems"
    }
}

# Onit API endpoints
ONIT_API_ENDPOINTS = {
    "rates": "/api/v1/rates",
    "timekeepers": "/api/v1/timekeepers",
    "invoices": "/api/v1/invoices",
    "matters": "/api/v1/matters"
}


def create_onit_client(config: Dict) -> 'OnitClient':
    """
    Factory function to create a configured Onit client instance

    Args:
        config: Configuration dictionary

    Returns:
        OnitClient: Initialized client for Onit
    """
    # Validate required configuration parameters
    if not all(key in config for key in ["base_url", "client_id", "client_secret"]):
        raise ValueError("Missing required configuration parameters for Onit client")

    # Create and return an OnitClient instance with the provided configuration
    return OnitClient(config=config)


def create_onit_adapter(name: str, base_url: str, auth_credentials: Dict, headers: Dict, timeout: int,
                        verify_ssl: bool) -> 'OnitAdapter':
    """
    Factory function to create a configured Onit adapter instance

    Args:
        name: Adapter name
        base_url: Base URL for the Onit API
        auth_credentials: Authentication credentials
        headers: HTTP headers
        timeout: Request timeout
        verify_ssl: SSL verification

    Returns:
        OnitAdapter: Initialized adapter for Onit
    """
    # Create a client with the provided configuration
    client = OnitClient(config={"base_url": base_url, "auth_credentials": auth_credentials})

    # Create a mapper with default field mappings
    mapper = OnitMapper(field_mappings=DEFAULT_FIELD_MAPPINGS)

    # Create and return an OnitAdapter with the client and mapper
    return OnitAdapter(name=name, base_url=base_url, auth_credentials=auth_credentials, headers=headers,
                       client=client, mapper=mapper, timeout=timeout, verify_ssl=verify_ssl)


class OnitClient(BaseIntegrationClient):
    """
    Client for interacting with the Onit API, handling authentication, requests, and response parsing
    """

    def __init__(self, config: Dict):
        """
        Initialize the Onit client with connection details

        Args:
            config: Configuration dictionary
        """
        # Call parent constructor with configuration
        super().__init__(
            base_url=config["base_url"],
            auth_config=config["auth_credentials"],
            auth_method="oauth",
            timeout=config.get("timeout", 30),
            max_retries=config.get("max_retries", 3),
            verify_ssl=config.get("verify_ssl", True)
        )

        # Set up base URL with API version
        self.base_url = urljoin(self.base_url, ONIT_API_VERSION)

        # Extract authentication credentials (client_id, client_secret)
        self.client_id = self.auth_config.get("client_id")
        self.client_secret = self.auth_config.get("client_secret")

        # Initialize token and token_expiry as None
        self.token = None
        self.token_expiry = None

        # Initialize OAuth2Session
        self.oauth_session = OAuth2Session(client_id=self.client_id)

        # Log client initialization
        logger.info(f"Initialized OnitClient for {self.base_url}")

    def authenticate(self) -> Dict:
        """
        Authenticate with the Onit API using OAuth 2.0

        Returns:
            Dict: Authentication headers with token
        """
        # Check if existing token is valid
        if self.token and self.token_expiry > datetime.now():
            logger.debug("Using existing Onit API token")
            return {"Authorization": f"Bearer {self.token}"}

        # If token is expired or None, get a new OAuth token
        logger.info("Getting new Onit API token")

        # Create OAuth2Session with client_id and token
        client = BackendApplicationClient(client_id=self.client_id)
        self.oauth_session = OAuth2Session(client_id=self.client_id, client=client)

        # Request token using client_credentials grant
        token_url = urljoin(self.base_url, "/oauth/token")
        try:
            self.oauth_session.fetch_token(token_url=token_url, client_id=self.client_id,
                                           client_secret=self.client_secret)
            self.token = self.oauth_session.token.get("access_token")
            expires_in = self.oauth_session.token.get("expires_in")
            self.token_expiry = datetime.now() + datetime.timedelta(seconds=expires_in) if expires_in else None
            logger.info("Successfully retrieved Onit API token")
            return {"Authorization": f"Bearer {self.token}"}
        except Exception as e:
            logger.error(f"Error fetching Onit API token: {e}")
            raise

    def get_rates(self, params: Dict) -> Dict:
        """
        Retrieve rate data from Onit

        Args:
            params: Query parameters

        Returns:
            Dict: Rate data from Onit
        """
        # Authenticate with the API
        self.authenticate()

        # Construct query parameters with filters and pagination
        endpoint = ONIT_API_ENDPOINTS["rates"]
        url = urljoin(self.base_url, endpoint)

        # Make a GET request to the rates endpoint
        response = self.get(url, params=params)

        # Process the response and handle pagination
        return self.handle_pagination(endpoint, params, response)

    def get_timekeepers(self, params: Dict) -> Dict:
        """
        Retrieve timekeeper (attorney) data from Onit

        Args:
            params: Query parameters

        Returns:
            Dict: Timekeeper data from Onit
        """
        # Authenticate with the API
        self.authenticate()

        # Construct query parameters with filters and pagination
        endpoint = ONIT_API_ENDPOINTS["timekeepers"]
        url = urljoin(self.base_url, endpoint)

        # Make a GET request to the timekeepers endpoint
        response = self.get(url, params=params)

        # Process the response and handle pagination
        return self.handle_pagination(endpoint, params, response)

    def get_invoices(self, params: Dict) -> Dict:
        """
        Retrieve invoice data from Onit for historical billing analysis

        Args:
            params: Query parameters

        Returns:
            Dict: Invoice data from Onit
        """
        # Authenticate with the API
        self.authenticate()

        # Construct query parameters with filters and pagination
        endpoint = ONIT_API_ENDPOINTS["invoices"]
        url = urljoin(self.base_url, endpoint)

        # Make a GET request to the invoices endpoint
        response = self.get(url, params=params)

        # Process the response and handle pagination
        return self.handle_pagination(endpoint, params, response)

    def get_matters(self, params: Dict) -> Dict:
        """
        Retrieve matter data from Onit

        Args:
            params: Query parameters

        Returns:
            Dict: Matter data from Onit
        """
        # Authenticate with the API
        self.authenticate()

        # Construct query parameters with filters and pagination
        endpoint = ONIT_API_ENDPOINTS["matters"]
        url = urljoin(self.base_url, endpoint)

        # Make a GET request to the matters endpoint
        response = self.get(url, params=params)

        # Process the response and handle pagination
        return self.handle_pagination(endpoint, params, response)

    def update_rates(self, rates_data: Dict) -> Dict:
        """
        Send updated rates to Onit

        Args:
            rates_data: Rates data

        Returns:
            Dict: Response from rate update operation
        """
        # Authenticate with the API
        self.authenticate()

        # Format the rates data for Onit
        endpoint = ONIT_API_ENDPOINTS["rates"]
        url = urljoin(self.base_url, endpoint)

        # If rate has ID, use PUT to update, otherwise use POST to create
        if rates_data.get("id"):
            response = self.put(url, json_data=rates_data)
        else:
            response = self.post(url, json_data=rates_data)

        # Process the response and handle any errors
        return response

    def handle_pagination(self, endpoint: str, params: Dict, initial_response: Dict) -> List:
        """
        Handle paginated responses from Onit API

        Args:
            endpoint: API endpoint
            params: Query parameters
            initial_response: Initial response from the API

        Returns:
            List: Complete list of items from all pages
        """
        items = initial_response.get("items", [])
        total_count = initial_response.get("total_count")
        page_size = initial_response.get("page_size", DEFAULT_PAGE_SIZE)
        current_page = initial_response.get("current_page", 1)

        # Check if more pages exist based on total_count and current_page
        while total_count and current_page * page_size < total_count:
            current_page += 1
            params["page"] = current_page

            # Make additional requests
            url = urljoin(self.base_url, endpoint)
            response = self.get(url, params=params)
            items.extend(response.get("items", []))

        return items

    def refresh_token(self) -> bool:
        """
        Refresh the OAuth token for authentication

        Returns:
            bool: True if token refresh is successful, False otherwise
        """
        # Request a new OAuth token using client credentials
        client = BackendApplicationClient(client_id=self.client_id)
        self.oauth_session = OAuth2Session(client_id=self.client_id, client=client)
        token_url = urljoin(self.base_url, "/oauth/token")
        try:
            self.oauth_session.fetch_token(token_url=token_url, client_id=self.client_id,
                                           client_secret=self.client_secret)
            self.token = self.oauth_session.token.get("access_token")
            expires_in = self.oauth_session.token.get("expires_in")
            self.token_expiry = datetime.now() + datetime.timedelta(seconds=expires_in) if expires_in else None
            logger.info("Successfully refreshed Onit API token")
            return True
        except Exception as e:
            logger.error(f"Error refreshing Onit API token: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test the connection to Onit API

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            logger.info(f"Testing connection to {self.base_url}")

            # Attempt to authenticate
            self.authenticate()

            # Make a simple request to verify API access
            endpoint = ONIT_API_ENDPOINTS["rates"]
            url = urljoin(self.base_url, endpoint)
            response = self.get(url, raw_response=True)

            success = 200 <= response.status_code < 300
            log_level = logger.info if success else logger.error
            log_level(
                f"Connection test to {self.base_url} {'succeeded' if success else 'failed'} "
                f"with status {response.status_code}",
                extra={'additional_data': {'status_code': response.status_code}}
            )

            return success

        except Exception as e:
            logger.error(
                f"Connection test to {self.base_url} failed with exception: {str(e)}",
                extra={'additional_data': {'error': str(e), 'type': type(e).__name__}}
            )
            return False


class OnitMapper(FieldMapper):
    """
    Maps data between Onit format and Justice Bid format
    """

    def __init__(self, field_mappings: Dict):
        """
        Initialize the mapper with field mappings

        Args:
            field_mappings: Dictionary of field mappings
        """
        # Call parent constructor with field mappings and default values
        super().__init__(field_mappings=field_mappings)

        # Set up specific transformations for Onit data
        self.date_format = "%Y-%m-%d"

    def map_data(self, source_data: Dict, data_type: str) -> Dict:
        """
        Map data from Onit format to Justice Bid format

        Args:
            source_data: Data in Onit format
            data_type: Type of data being mapped

        Returns:
            Dict: Mapped data in Justice Bid format
        """
        # Select appropriate mapping configuration based on data_type
        mapping_config = self.field_mappings.get(data_type, {})

        # Apply field mapping to source data
        mapped_data = {}
        for target_field, source_field in mapping_config.items():
            mapped_data[target_field] = source_data.get(source_field)

        # Apply specific transformations for Onit data format (dates, enums, etc.)
        if "effective_date" in mapped_data and mapped_data["effective_date"]:
            mapped_data["effective_date"] = self.transform_date_format(mapped_data["effective_date"], "to_justice_bid")
        if "expiration_date" in mapped_data and mapped_data["expiration_date"]:
            mapped_data["expiration_date"] = self.transform_date_format(mapped_data["expiration_date"],
                                                                         "to_justice_bid")
        if "status" in mapped_data and mapped_data["status"]:
            mapped_data["status"] = self.transform_status(mapped_data["status"], "to_justice_bid")

        # Validate the mapped data
        # TODO: Implement data validation

        return mapped_data

    def reverse_map_data(self, source_data: Dict, data_type: str) -> Dict:
        """
        Map data from Justice Bid format to Onit format

        Args:
            source_data: Data in Justice Bid format
            data_type: Type of data being mapped

        Returns:
            Dict: Mapped data in Onit format
        """
        # Select appropriate mapping configuration based on data_type
        mapping_config = self.field_mappings.get(data_type, {})

        # Apply reverse field mapping to source data
        mapped_data = {}
        for target_field, source_field in mapping_config.items():
            mapped_data[source_field] = source_data.get(target_field)

        # Apply specific transformations for Onit format requirements
        if "effective_date" in mapped_data and mapped_data["effective_date"]:
            mapped_data["effective_date"] = self.transform_date_format(mapped_data["effective_date"], "to_onit")
        if "expiration_date" in mapped_data and mapped_data["expiration_date"]:
            mapped_data["expiration_date"] = self.transform_date_format(mapped_data["expiration_date"], "to_onit")
        if "status" in mapped_data and mapped_data["status"]:
            mapped_data["status"] = self.transform_status(mapped_data["status"], "to_onit")

        # Validate the mapped data
        # TODO: Implement data validation

        return mapped_data

    def transform_date_format(self, date_str: str, direction: str) -> str:
        """
        Transform date format between Justice Bid and Onit

        Args:
            date_str: Date string to transform
            direction: Transformation direction ("to_onit" or "to_justice_bid")

        Returns:
            str: Transformed date string
        """
        if direction == "to_onit":
            # Format as ISO 8601 (YYYY-MM-DD)
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        elif direction == "to_justice_bid":
            # Parse Onit date format and standardize
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d")
        else:
            raise ValueError(f"Invalid date transformation direction: {direction}")

    def transform_status(self, status: str, direction: str) -> str:
        """
        Transform status values between Justice Bid and Onit

        Args:
            status: Status value to transform
            direction: Transformation direction ("to_onit" or "to_justice_bid")

        Returns:
            str: Transformed status string
        """
        if direction == "to_onit":
            # Convert Justice Bid status to Onit status
            if status == "approved":
                return "Approved"
            elif status == "rejected":
                return "Rejected"
            elif status == "submitted":
                return "Submitted"
            else:
                return "Draft"  # Default status
        elif direction == "to_justice_bid":
            # Convert Onit status to Justice Bid status
            if status == "Approved":
                return "approved"
            elif status == "Rejected":
                return "rejected"
            elif status == "Submitted":
                return "submitted"
            else:
                return "draft"  # Default status
        else:
            raise ValueError(f"Invalid status transformation direction: {direction}")


class OnitAdapter(BaseAPIAdapter):
    """
    Adapter for the Onit eBilling system, implementing the specific integration details
    """

    def __init__(self, name: str, base_url: str, auth_credentials: Dict, headers: Dict, client: 'OnitClient',
                 mapper: 'OnitMapper', timeout: int = 30, verify_ssl: bool = True):
        """
        Initialize the Onit adapter with client and mapper

        Args:
            name: Adapter name
            base_url: Base URL for the Onit API
            auth_credentials: Authentication credentials
            headers: HTTP headers
            client: Onit client instance
            mapper: Onit mapper instance
        """
        # Call parent constructor with base parameters
        super().__init__(
            name=name,
            integration_type=IntegrationType.EBILLING_ONIT.value,
            base_url=base_url,
            auth_credentials=auth_credentials,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl
        )

        # Store the Onit client instance
        self.client = client

        # Store the Onit mapper instance
        self.mapper = mapper

        # Log adapter initialization
        logger.info(f"Initialized OnitAdapter for {base_url}")

    def authenticate(self) -> bool:
        """
        Authenticate with the Onit API

        Returns:
            bool: True if authentication is successful, False otherwise
        """
        try:
            # Delegate authentication to the client
            self.client.authenticate()
            return True
        except Exception as e:
            logger.error(f"Authentication failed for Onit: {e}")
            return False

    def validate_connection(self) -> bool:
        """
        Validate the connection to Onit

        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            # Attempt to authenticate
            self.authenticate()

            # Make a simple API call to verify connectivity
            return self.client.test_connection()
        except Exception as e:
            logger.error(f"Connection validation failed for Onit: {e}")
            return False

    def get_data(self, data_type: str, params: Dict = None, headers: Dict = None) -> Dict:
        """
        Retrieve data from Onit

        Args:
            data_type: Type of data to retrieve (rates, timekeepers, invoices)
            params: Query parameters
            headers: HTTP headers

        Returns:
            Dict: Mapped data from Onit
        """
        try:
            # Select appropriate client method based on data_type
            if data_type == "rate":
                client_method = self.client.get_rates
            elif data_type == "attorney":
                client_method = self.client.get_timekeepers
            elif data_type == "invoice":
                client_method = self.client.get_invoices
            elif data_type == "matter":
                client_method = self.client.get_matters
            else:
                raise ValueError(f"Invalid data_type: {data_type}")

            # Call the client method with provided parameters
            response_data = client_method(params=params)

            # Map the response data to Justice Bid format using the mapper
            mapped_data = []
            for item in response_data:
                mapped_item = self.mapper.map_data(item, data_type)
                mapped_data.append(mapped_item)

            return mapped_data
        except Exception as e:
            logger.error(f"Error retrieving data from Onit: {e}")
            raise

    def send_data(self, data_type: str, data: Dict, params: Dict = None, headers: Dict = None) -> Dict:
        """
        Send data to Onit

        Args:
            data_type: Type of data to send (rates)
            data: Data to send in Justice Bid format
            params: Query parameters
            headers: HTTP headers

        Returns:
            Dict: Response from Onit
        """
        try:
            # Map the data from Justice Bid format to Onit format
            mapped_data = self.mapper.reverse_map_data(data, data_type)

            # Select appropriate client method based on data_type
            if data_type == "rate":
                client_method = self.client.update_rates
            else:
                raise ValueError(f"Invalid data_type for sending data: {data_type}")

            # Call the client method with mapped data and parameters
            response = client_method(rates_data=mapped_data)
            return response
        except Exception as e:
            logger.error(f"Error sending data to Onit: {e}")
            raise

    def map_data(self, data: Dict, direction: str, data_type: str) -> Dict:
        """
        Map data between Onit and Justice Bid formats

        Args:
            data: Data to map
            direction: Direction of mapping ("to_justice_bid" or "to_onit")
            data_type: Type of data being mapped

        Returns:
            Dict: Mapped data in target format
        """
        try:
            # Determine mapping direction
            if direction == "to_justice_bid":
                # Map from Onit to Justice Bid
                return self.mapper.map_data(data, data_type)
            elif direction == "to_onit":
                # Map from Justice Bid to Onit
                return self.mapper.reverse_map_data(data, data_type)
            else:
                raise ValueError(f"Invalid mapping direction: {direction}")
        except Exception as e:
            logger.error(f"Error mapping data: {e}")
            raise

    def get_historical_rates(self, filters: Dict) -> Dict:
        """
        Retrieve historical rate data from Onit

        Args:
            filters: Filters for rate data

        Returns:
            Dict: Historical rate data
        """
        # Prepare query parameters with filters
        params = filters

        # Call get_data with data_type='rate'
        return self.get_data(data_type="rate", params=params)

    def get_attorneys(self, filters: Dict) -> Dict:
        """
        Retrieve attorney (timekeeper) data from Onit

        Args:
            filters: Filters for attorney data

        Returns:
            Dict: Attorney data
        """
        # Prepare query parameters with filters
        params = filters

        # Call get_data with data_type='attorney'
        return self.get_data(data_type="attorney", params=params)

    def get_matters(self, filters: Dict) -> Dict:
        """
        Retrieve matter data from Onit

        Args:
            filters: Filters for matter data

        Returns:
            Dict: Matter data
        """
        # Prepare query parameters with filters
        params = filters

        # Call get_data with data_type='matter'
        return self.get_data(data_type="matter", params=params)

    def get_billing_history(self, filters: Dict) -> Dict:
        """
        Retrieve historical billing data from Onit

        Args:
            filters: Filters for billing data

        Returns:
            Dict: Historical billing data
        """
        # Prepare query parameters with filters
        params = filters

        # Call get_data with data_type='invoice'
        return self.get_data(data_type="invoice", params=params)

    def export_approved_rates(self, rates_data: Dict) -> Dict:
        """
        Export approved rates to Onit

        Args:
            rates_data: Approved rate data

        Returns:
            Dict: Export result
        """
        try:
            # Validate the rates data structure
            # TODO: Implement data validation

            # Call send_data with data_type='rate'
            response = self.send_data(data_type="rate", data=rates_data)

            # Handle any export errors
            # TODO: Implement error handling

            # Return the export result with success and error counts
            return {"success": True, "message": "Successfully exported approved rates to Onit"}
        except Exception as e:
            logger.error(f"Error exporting approved rates to Onit: {e}")
            return {"success": False, "message": f"Error exporting approved rates to Onit: {e}"}

    def import_file(self, file_path: str, data_type: str, mapping_config: Dict) -> tuple[bool, str, list]:
        """
        Import data from a file exported from Onit

        Args:
            file_path: Path to the file to import
            data_type: Type of data contained in the file
            mapping_config: Configuration for mapping fields from file to internal format

        Returns:
            tuple[bool, str, list]: Success flag, message, and imported data
        """
        # Call parent import_file method
        success, message, data = super().import_file(file_path, data_type, mapping_config)

        if not success:
            return success, message, []

        # Apply Onit-specific transformations if needed
        # TODO: Implement Onit-specific transformations

        return success, message, data

    def export_file(self, file_path: str, data_type: str, data: List, mapping_config: Dict) -> tuple[bool, str]:
        """
        Export data to a file for import into Onit

        Args:
            file_path: Path to save the exported file
            data_type: Type of data to export
            data: Data to export in Justice Bid format
            mapping_config: Configuration for mapping fields from internal to file format

        Returns:
            tuple[bool, str]: Success flag and message
        """
        # Map data to Onit format using mapping_config or default mappings
        # TODO: Implement mapping logic

        # Call parent export_file method
        return super().export_file(file_path, data_type, data, mapping_config)