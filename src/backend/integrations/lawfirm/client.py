"""
Implements client classes for integrating with law firm billing systems. Provides functionality for fetching attorney profiles,
retrieving standard rates, and exporting approved rates back to the firm's billing system.
Supports multiple authentication methods and handles different law firm API structures.
"""

import uuid
from typing import Dict, List, Union
import json
import base64
from datetime import datetime

from ..common.client import BaseIntegrationClient, ApiError, ApiAuthenticationError  # Assuming version 1.0
from .mapper import LawFirmAttorneyMapper, LawFirmRateMapper, create_standard_mapping  # Assuming version 1.0
from ...utils.logging import get_logger  # Assuming version 1.0
from ...utils.constants import RateStatus, RateType  # Assuming version 1.0

# Initialize logger
logger = get_logger(__name__)

# List of supported law firm billing systems
SUPPORTED_LAW_FIRM_SYSTEMS = ['generic', 'elite', 'aderant', 'juris', 'centerbase', 'clio', 'practice_panther']


def get_law_firm_client(
    system_type: str,
    base_url: str,
    auth_config: Dict[str, str],
    auth_method: str,
    headers: Dict[str, str],
    mapping_config: Dict,
    organization_id: uuid.UUID
) -> 'LawFirmClient':
    """
    Factory function to create the appropriate law firm client based on system type.

    Args:
        system_type: Type of law firm billing system
        base_url: Base URL for the API
        auth_config: Authentication configuration (keys, tokens, credentials)
        auth_method: Authentication method ('api_key', 'oauth', 'basic', 'bearer', 'none')
        headers: Additional HTTP headers to include in requests
        mapping_config: Field mapping configuration
        organization_id: UUID of the law firm organization

    Returns:
        Instance of appropriate law firm client
    """
    # Validate that system_type is in SUPPORTED_LAW_FIRM_SYSTEMS
    if system_type not in SUPPORTED_LAW_FIRM_SYSTEMS:
        raise ValueError(f"Unsupported law firm system type: {system_type}")

    # Log client creation with masked auth details
    masked_auth = BaseIntegrationClient.mask_sensitive_data(auth_config)
    logger.info(
        f"Creating law firm client for system type: {system_type}",
        extra={
            'additional_data': {
                'system_type': system_type,
                'base_url': base_url,
                'auth_method': auth_method,
                'auth_config': masked_auth,
                'organization_id': organization_id
            }
        }
    )

    # Create and return appropriate client class based on system_type
    if system_type == 'elite':
        return EliteLawFirmClient(base_url, auth_config, auth_method, headers, mapping_config, organization_id)
    elif system_type == 'aderant':
        return AderantLawFirmClient(base_url, auth_config, auth_method, headers, mapping_config, organization_id)
    # Add other supported systems here with specific client classes
    else:
        # Default to GenericLawFirmClient for unrecognized types
        return GenericLawFirmClient(base_url, auth_config, auth_method, headers, mapping_config, organization_id)


class LawFirmClient(BaseIntegrationClient):
    """
    Abstract base class for law firm billing system integrations.
    """

    def __init__(
        self,
        base_url: str,
        auth_config: Dict[str, str],
        auth_method: str,
        headers: Dict[str, str],
        mapping_config: Dict,
        organization_id: uuid.UUID
    ):
        """
        Initialize the law firm client with connection parameters.

        Args:
            base_url: Base URL for the API
            auth_config: Authentication configuration (keys, tokens, credentials)
            auth_method: Authentication method ('api_key', 'oauth', 'basic', 'bearer', 'none')
            headers: Additional HTTP headers to include in requests
            mapping_config: Field mapping configuration
            organization_id: UUID of the law firm organization
        """
        # Call BaseIntegrationClient.__init__ with connection parameters
        super().__init__(base_url, auth_config, auth_method, headers)

        # Store organization_id for use in API requests
        self.organization_id = organization_id

        # Extract attorney and rate mapping configurations from mapping_config
        self.attorney_mapping_config = mapping_config.get('attorney_mapping', {})
        self.rate_mapping_config = mapping_config.get('rate_mapping', {})

        # Initialize attorney_mapper with organization_id and attorney mapping config
        self.attorney_mapper = LawFirmAttorneyMapper(self.organization_id, self.attorney_mapping_config)

        # Initialize rate_mapper with organization_id and rate mapping config
        self.rate_mapper = LawFirmRateMapper(self.organization_id, mapping_config=self.rate_mapping_config)

        # Log client initialization with masked auth details
        masked_auth = BaseIntegrationClient.mask_sensitive_data(auth_config)
        logger.info(
            f"Initialized {self.__class__.__name__} for {self.base_url}",
            extra={
                'additional_data': {
                    'base_url': self.base_url,
                    'auth_method': self.auth_method,
                    'auth_config': masked_auth,
                    'organization_id': self.organization_id
                }
            }
        )

    def authenticate(self) -> bool:
        """
        Authenticate with the law firm billing system.

        This method should be implemented by subclasses to handle authentication
        based on the specified auth_method and auth_config.

        Returns:
            True if authentication is successful, False otherwise
        """
        # Override abstract method from BaseIntegrationClient
        # Implementation depends on specific authentication mechanism
        logger.warning("Authentication method not implemented in base class. Please implement in subclass.")
        return False

    def get_attorneys(self, params: Dict = None) -> List[Dict]:
        """
        Retrieve attorney profiles from the law firm system.

        Args:
            params: Query parameters

        Returns:
            List of attorney objects in Justice Bid format
        """
        raise NotImplementedError("get_attorneys method must be implemented in subclass")

    def get_attorney(self, attorney_id: str) -> Dict:
        """
        Retrieve a specific attorney profile by ID.

        Args:
            attorney_id: ID of the attorney to retrieve

        Returns:
            Attorney object in Justice Bid format
        """
        raise NotImplementedError("get_attorney method must be implemented in subclass")

    def get_rates(self, params: Dict = None, client_id: uuid.UUID = None) -> List[Dict]:
        """
        Retrieve standard rates from the law firm system.

        Args:
            params: Query parameters
            client_id: UUID of the client for whom rates are being retrieved

        Returns:
            List of rate objects in Justice Bid format
        """
        raise NotImplementedError("get_rates method must be implemented in subclass")

    def get_rate(self, attorney_id: str, client_id: uuid.UUID) -> Dict:
        """
        Retrieve a specific rate by attorney ID and client ID.

        Args:
            attorney_id: ID of the attorney
            client_id: UUID of the client

        Returns:
            Rate object in Justice Bid format
        """
        raise NotImplementedError("get_rate method must be implemented in subclass")

    def export_rates(self, rates: List[Dict]) -> bool:
        """
        Export approved rates back to the law firm system.

        Args:
            rates: List of rate objects in Justice Bid format

        Returns:
            True if export is successful, False otherwise
        """
        raise NotImplementedError("export_rates method must be implemented in subclass")

    def handle_pagination(self, response: Dict, resource_key: str, endpoint: str, params: Dict) -> List:
        """
        Handle pagination for API responses that return multiple pages.

        Args:
            response: API response
            resource_key: Key in the response containing the resource list
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Combined list of all resources across pages
        """
        raise NotImplementedError("handle_pagination method must be implemented in subclass")


class GenericLawFirmClient(LawFirmClient):
    """
    Generic implementation of LawFirmClient for systems without dedicated support.
    """

    def __init__(
        self,
        base_url: str,
        auth_config: Dict[str, str],
        auth_method: str,
        headers: Dict[str, str],
        mapping_config: Dict,
        organization_id: uuid.UUID
    ):
        """
        Initialize the generic law firm client.

        Args:
            base_url: Base URL for the API
            auth_config: Authentication configuration (keys, tokens, credentials)
            auth_method: Authentication method ('api_key', 'oauth', 'basic', 'bearer', 'none')
            headers: Additional HTTP headers to include in requests
            mapping_config: Field mapping configuration
            organization_id: UUID of the law firm organization
        """
        # Call LawFirmClient.__init__ with all parameters
        super().__init__(base_url, auth_config, auth_method, headers, mapping_config, organization_id)

        # Initialize default endpoint mapping based on common patterns
        self.endpoint_map = {
            'attorneys': '/attorneys',
            'attorney_detail': '/attorneys/{attorney_id}',
            'rates': '/rates',
            'rate_detail': '/rates/{rate_id}',
            'rates_update': '/rates'
        }

        # Update endpoint_map with any custom endpoints from auth_config
        if 'endpoints' in auth_config:
            self.endpoint_map.update(auth_config['endpoints'])

        # Log initialization with endpoint configuration
        logger.info(
            f"Initialized GenericLawFirmClient for {self.base_url}",
            extra={'additional_data': {'endpoint_map': self.endpoint_map}}
        )

    def authenticate(self) -> bool:
        """
        Authenticate with the generic law firm system.

        Returns:
            True if authentication is successful, False otherwise
        """
        # Implement different auth methods based on auth_method property
        try:
            if self.auth_method == 'oauth':
                # Perform OAuth flow and store tokens
                logger.info("Performing OAuth flow (Not fully implemented)")
                return True  # Placeholder
            elif self.auth_method == 'api_key':
                # Validate API key with a test request
                logger.info("Validating API key (Not fully implemented)")
                return True  # Placeholder
            elif self.auth_method == 'basic':
                # Encode credentials and validate
                logger.info("Performing Basic Authentication")
                username = self.auth_config.get('username')
                password = self.auth_config.get('password')
                if not username or not password:
                    raise ApiAuthenticationError("Username and password are required for Basic Authentication")
                creds = f'{username}:{password}'.encode('utf-8')
                encoded_creds = base64.b64encode(creds).decode('utf-8')
                self.session.headers['Authorization'] = f'Basic {encoded_creds}'
                # Validate by making a test request
                self.get(self.endpoint_map.get('attorneys'), params={'limit': 1})
                return True
            elif self.auth_method == 'bearer':
                # Validate token with a test request
                logger.info("Validating Bearer token (Not fully implemented)")
                token = self.auth_config.get('token')
                if not token:
                    raise ApiAuthenticationError("Bearer token is required")
                self.session.headers['Authorization'] = f'Bearer {token}'
                 # Validate by making a test request
                self.get(self.endpoint_map.get('attorneys'), params={'limit': 1})
                return True
            elif self.auth_method == 'none':
                logger.info("No authentication required")
                return True
            else:
                logger.error(f"Unsupported authentication method: {self.auth_method}")
                return False
        except ApiError as e:
            logger.error(f"Authentication failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False

    def get_attorneys(self, params: Dict = None) -> List[Dict]:
        """
        Retrieve attorney profiles from the generic law firm system.

        Args:
            params: Query parameters

        Returns:
            List of attorney objects in Justice Bid format
        """
        try:
            # Get attorneys endpoint from endpoint_map
            endpoint = self.endpoint_map.get('attorneys')
            if not endpoint:
                raise ValueError("Attorneys endpoint not configured")

            # Make GET request to the attorneys endpoint with params
            response = self.get(endpoint, params=params)

            # Handle pagination using handle_pagination method
            attorneys_data = self.handle_pagination(response, 'attorneys', endpoint, params)

            # Process response data to extract attorney information
            attorneys = []
            for attorney_data in attorneys_data:
                # Map each attorney record to Justice Bid format
                mapped_attorney = self.attorney_mapper.map_data(attorney_data)

                # Create Attorney objects from mapped data
                attorneys.append(mapped_attorney)

            # Return list of Attorney objects
            return attorneys
        except Exception as e:
            logger.error(f"Error retrieving attorneys: {str(e)}")
            return []

    def get_attorney(self, attorney_id: str) -> Dict:
        """
        Retrieve a specific attorney profile by ID.

        Args:
            attorney_id: ID of the attorney to retrieve

        Returns:
            Attorney object in Justice Bid format
        """
        try:
            # Get attorney detail endpoint from endpoint_map
            endpoint = self.endpoint_map.get('attorney_detail')
            if not endpoint:
                raise ValueError("Attorney detail endpoint not configured")

            # Format endpoint with attorney_id parameter
            endpoint = endpoint.format(attorney_id=attorney_id)

            # Make GET request to the attorney endpoint
            response = self.get(endpoint)

            # Process response to extract attorney information
            mapped_attorney = self.attorney_mapper.map_data(response)

            # Return Attorney object
            return mapped_attorney
        except Exception as e:
            logger.error(f"Error retrieving attorney {attorney_id}: {str(e)}")
            return None

    def get_rates(self, params: Dict = None, client_id: uuid.UUID = None) -> List[Dict]:
        """
        Retrieve standard rates from the generic law firm system.

        Args:
            params: Query parameters
            client_id: UUID of the client for whom rates are being retrieved

        Returns:
            List of rate objects in Justice Bid format
        """
        try:
            # Get rates endpoint from endpoint_map
            endpoint = self.endpoint_map.get('rates')
            if not endpoint:
                raise ValueError("Rates endpoint not configured")

            # Prepare query parameters with client_id if provided
            if params is None:
                params = {}
            if client_id:
                params['client_id'] = str(client_id)

            # Make GET request to the rates endpoint with params
            response = self.get(endpoint, params=params)

            # Handle pagination using handle_pagination method
            rates_data = self.handle_pagination(response, 'rates', endpoint, params)

            # Process response data to extract rate information
            rates = []
            for rate_data in rates_data:
                # Map each rate record to Justice Bid format
                mapped_rate = self.rate_mapper.map_data(rate_data)

                # Create Rate objects from mapped data
                rates.append(mapped_rate)

            # Return list of Rate objects
            return rates
        except Exception as e:
            logger.error(f"Error retrieving rates: {str(e)}")
            return []

    def get_rate(self, attorney_id: str, client_id: uuid.UUID) -> Dict:
        """
        Retrieve a specific rate by attorney ID and client ID.

        Args:
            attorney_id: ID of the attorney
            client_id: UUID of the client

        Returns:
            Rate object in Justice Bid format
        """
        try:
            # Get rate detail endpoint from endpoint_map
            endpoint = self.endpoint_map.get('rate_detail')
            if not endpoint:
                raise ValueError("Rate detail endpoint not configured")

            # Prepare query parameters with attorney_id and client_id
            params = {'attorney_id': attorney_id, 'client_id': str(client_id)}

            # Make GET request to the rate endpoint
            response = self.get(endpoint, params=params)

            # Process response to extract rate information
            mapped_rate = self.rate_mapper.map_data(response)

            # Return Rate object
            return mapped_rate
        except Exception as e:
            logger.error(f"Error retrieving rate for attorney {attorney_id} and client {client_id}: {str(e)}")
            return None

    def export_rates(self, rates: List[Dict]) -> bool:
        """
        Export approved rates back to the generic law firm system.

        Args:
            rates: List of rate objects in Justice Bid format

        Returns:
            True if export is successful, False otherwise
        """
        try:
            # Get rates update endpoint from endpoint_map
            endpoint = self.endpoint_map.get('rates_update')
            if not endpoint:
                raise ValueError("Rates update endpoint not configured")

            # Transform Justice Bid rate objects to law firm format
            law_firm_rates = [self.rate_mapper.reverse_map_data(rate) for rate in rates]

            # Make PUT/POST request to update rates in law firm system
            response = self.put(endpoint, json_data=law_firm_rates)

            # Process response to verify successful update
            if response:
                logger.info(f"Successfully exported {len(rates)} rates")
                return True
            else:
                logger.warning("Rate export failed: No response received")
                return False
        except Exception as e:
            logger.error(f"Error exporting rates: {str(e)}")
            return False

    def handle_pagination(self, response: Dict, resource_key: str, endpoint: str, params: Dict) -> List:
        """
        Handle pagination for generic law firm API responses.

        Args:
            response: API response
            resource_key: Key in the response containing the resource list
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Combined list of all resources across pages
        """
        all_resources = []
        try:
            # Try to detect pagination format in response
            if 'next_page' in response:
                # Example: {"data": [...], "next_page": "url"}
                next_page_url = response.get('next_page')
                resources = response.get('data', [])
                all_resources.extend(resources)

                while next_page_url:
                    next_response = self.get(next_page_url)
                    resources = next_response.get('data', [])
                    all_resources.extend(resources)
                    next_page_url = next_response.get('next_page')

            elif 'items' in response and 'total_count' in response:
                # Example: {"items": [...], "total_count": 100, "page": 1, "page_size": 20}
                total_count = response.get('total_count')
                page = response.get('page', 1)
                page_size = response.get('page_size', 20)
                resources = response.get('items', [])
                all_resources.extend(resources)

                while len(all_resources) < total_count:
                    params['page'] = page + 1
                    next_response = self.get(endpoint, params=params)
                    resources = next_response.get('items', [])
                    all_resources.extend(resources)
                    page += 1

            else:
                # No pagination, assume all resources are in the response
                resources = response.get(resource_key, [])
                all_resources.extend(resources)

            return all_resources

        except Exception as e:
            logger.error(f"Error handling pagination: {str(e)}")
            return all_resources


class EliteLawFirmClient(LawFirmClient):
    """
    Specialized client implementation for Thomson Reuters Elite billing system.
    """

    def __init__(
        self,
        base_url: str,
        auth_config: Dict[str, str],
        auth_method: str,
        headers: Dict[str, str],
        mapping_config: Dict,
        organization_id: uuid.UUID
    ):
        """
        Initialize the Elite law firm client.

        Args:
            base_url: Base URL for the API
            auth_config: Authentication configuration (keys, tokens, credentials)
            auth_method: Authentication method ('api_key', 'oauth', 'basic', 'bearer', 'none')
            headers: Additional HTTP headers to include in requests
            mapping_config: Field mapping configuration
            organization_id: UUID of the law firm organization
        """
        # Call LawFirmClient.__init__ with all parameters
        super().__init__(base_url, auth_config, auth_method, headers, mapping_config, organization_id)

        # Initialize Elite-specific endpoint mapping
        self.endpoint_map = {
            'timekeepers': '/api/v1/Timekeepers',
            'rates': '/api/v1/Rates',
            'rates_update': '/api/v1/Rates'
        }

        # Set Elite-specific headers if needed
        self.session.headers['Content-Type'] = 'application/json'

        # Log initialization with Elite-specific configuration
        logger.info(f"Initialized EliteLawFirmClient for {self.base_url}")

    def authenticate(self) -> bool:
        """
        Authenticate with the Elite billing system.

        Returns:
            True if authentication is successful, False otherwise
        """
        # Implement Elite-specific authentication logic
        try:
            if self.auth_method == 'oauth':
                # Exchange credentials for access token
                logger.info("Performing Elite OAuth flow (Not fully implemented)")
                return True  # Placeholder
            elif self.auth_method == 'api_key':
                # Validate key with Elite API
                logger.info("Validating Elite API key (Not fully implemented)")
                return True  # Placeholder
            else:
                logger.error(f"Unsupported authentication method: {self.auth_method}")
                return False
        except Exception as e:
            logger.error(f"Elite authentication failed: {str(e)}")
            return False

    def get_attorneys(self, params: Dict = None) -> List[Dict]:
        """
        Retrieve attorney profiles from Elite system.

        Args:
            params: Query parameters

        Returns:
            List of attorney objects in Justice Bid format
        """
        try:
            # Make GET request to Elite-specific timekeepers endpoint
            response = self.get(self.endpoint_map['timekeepers'], params=params)

            # Handle Elite-specific pagination format
            attorneys_data = response.get('value', [])  # Elite uses 'value' for data

            # Process response data to extract attorney information
            attorneys = []
            for attorney_data in attorneys_data:
                # Map each Elite attorney to Justice Bid format
                mapped_attorney = self.attorney_mapper.map_data(attorney_data)

                # Create Attorney objects from mapped data
                attorneys.append(mapped_attorney)

            # Return list of Attorney objects
            return attorneys
        except Exception as e:
            logger.error(f"Error retrieving Elite attorneys: {str(e)}")
            return []

    def get_rates(self, params: Dict = None, client_id: uuid.UUID = None) -> List[Dict]:
        """
        Retrieve standard rates from Elite system.

        Args:
            params: Query parameters
            client_id: UUID of the client for whom rates are being retrieved

        Returns:
            List of rate objects in Justice Bid format
        """
        try:
            # Make GET request to Elite-specific rates endpoint
            response = self.get(self.endpoint_map['rates'], params=params)

            # Handle Elite-specific pagination format
            rates_data = response.get('value', [])  # Elite uses 'value' for data

            # Process response data to extract rate information
            rates = []
            for rate_data in rates_data:
                # Map each Elite rate to Justice Bid format
                mapped_rate = self.rate_mapper.map_data(rate_data)

                # Create Rate objects from mapped data
                rates.append(mapped_rate)

            # Return list of Rate objects
            return rates
        except Exception as e:
            logger.error(f"Error retrieving Elite rates: {str(e)}")
            return []

    def export_rates(self, rates: List[Dict]) -> bool:
        """
        Export approved rates back to Elite system.

        Args:
            rates: List of rate objects in Justice Bid format

        Returns:
            True if export is successful, False otherwise
        """
        try:
            # Transform Justice Bid rate objects to Elite format
            elite_rates = [self.rate_mapper.reverse_map_data(rate) for rate in rates]

            # Make POST request to Elite rates update endpoint
            response = self.post(self.endpoint_map['rates_update'], json_data={'value': elite_rates})  # Elite expects 'value'

            # Process Elite-specific response format
            if response and 'value' in response:
                logger.info(f"Successfully exported {len(rates)} rates to Elite")
                return True
            else:
                logger.warning("Elite rate export failed: Unexpected response format")
                return False
        except Exception as e:
            logger.error(f"Error exporting rates to Elite: {str(e)}")
            return False


class AderantLawFirmClient(LawFirmClient):
    """
    Specialized client implementation for Aderant Expert billing system.
    """

    def __init__(
        self,
        base_url: str,
        auth_config: Dict[str, str],
        auth_method: str,
        headers: Dict[str, str],
        mapping_config: Dict,
        organization_id: uuid.UUID
    ):
        """
        Initialize the Aderant law firm client.

        Args:
            base_url: Base URL for the API
            auth_config: Authentication configuration (keys, tokens, credentials)
            auth_method: Authentication method ('api_key', 'oauth', 'basic', 'bearer', 'none')
            headers: Additional HTTP headers to include in requests
            mapping_config: Field mapping configuration
            organization_id: UUID of the law firm organization
        """
        # Call LawFirmClient.__init__ with all parameters
        super().__init__(base_url, auth_config, auth_method, headers, mapping_config, organization_id)

        # Initialize Aderant-specific endpoint mapping
        self.endpoint_map = {
            'timekeepers': '/api/v1/Timekeepers',
            'rates': '/api/v1/Rates',
            'rates_update': '/api/v1/Rates'
        }

        # Set Aderant-specific headers if needed
        self.session.headers['Content-Type'] = 'application/json'

        # Log initialization with Aderant-specific configuration
        logger.info(f"Initialized AderantLawFirmClient for {self.base_url}")

    def authenticate(self) -> bool:
        """
        Authenticate with the Aderant billing system.

        Returns:
            True if authentication is successful, False otherwise
        """
        # Implement Aderant-specific authentication logic
        try:
            if self.auth_method == 'oauth':
                # Exchange credentials for access token
                logger.info("Performing Aderant OAuth flow (Not fully implemented)")
                return True  # Placeholder
            elif self.auth_method == 'api_key':
                # Validate key with Aderant API
                logger.info("Validating Aderant API key (Not fully implemented)")
                return True  # Placeholder
            else:
                logger.error(f"Unsupported authentication method: {self.auth_method}")
                return False
        except Exception as e:
            logger.error(f"Aderant authentication failed: {str(e)}")
            return False

    def get_attorneys(self, params: Dict = None) -> List[Dict]:
        """
        Retrieve attorney profiles from Aderant system.

        Args:
            params: Query parameters

        Returns:
            List of attorney objects in Justice Bid format
        """
        try:
            # Make GET request to Aderant-specific timekeeper endpoint
            response = self.get(self.endpoint_map['timekeepers'], params=params)

            # Handle Aderant-specific pagination format
            attorneys_data = response.get('value', [])  # Aderant uses 'value' for data

            # Process response data to extract attorney information
            attorneys = []
            for attorney_data in attorneys_data:
                # Map each Aderant attorney to Justice Bid format
                mapped_attorney = self.attorney_mapper.map_data(attorney_data)

                # Create Attorney objects from mapped data
                attorneys.append(mapped_attorney)

            # Return list of Attorney objects
            return attorneys
        except Exception as e:
            logger.error(f"Error retrieving Aderant attorneys: {str(e)}")
            return []

    def get_rates(self, params: Dict = None, client_id: uuid.UUID = None) -> List[Dict]:
        """
        Retrieve standard rates from Aderant system.

        Args:
            params: Query parameters
            client_id: UUID of the client for whom rates are being retrieved

        Returns:
            List of rate objects in Justice Bid format
        """
        try:
            # Make GET request to Aderant-specific rates endpoint
            response = self.get(self.endpoint_map['rates'], params=params)

            # Handle Aderant-specific pagination format
            rates_data = response.get('value', [])  # Aderant uses 'value' for data

            # Process response data to extract rate information
            rates = []
            for rate_data in rates_data:
                # Map each Aderant rate to Justice Bid format
                mapped_rate = self.rate_mapper.map_data(rate_data)

                # Create Rate objects from mapped data
                rates.append(mapped_rate)

            # Return list of Rate objects
            return rates
        except Exception as e:
            logger.error(f"Error retrieving Aderant rates: {str(e)}")
            return []

    def export_rates(self, rates: List[Dict]) -> bool:
        """
        Export approved rates back to Aderant system.

        Args:
            rates: List of rate objects in Justice Bid format

        Returns:
            True if export is successful, False otherwise
        """
        try:
            # Transform Justice Bid rate objects to Aderant format
            aderant_rates = [self.rate_mapper.reverse_map_data(rate) for rate in rates]

            # Make POST request to Aderant rates update endpoint
            response = self.post(self.endpoint_map['rates_update'], json_data={'value': aderant_rates})  # Aderant expects 'value'

            # Process Aderant-specific response format
            if response and 'value' in response:
                logger.info(f"Successfully exported {len(rates)} rates to Aderant")
                return True
            else:
                logger.warning("Aderant rate export failed: Unexpected response format")
                return False
        except Exception as e:
            logger.error(f"Error exporting rates to Aderant: {str(e)}")
            return False