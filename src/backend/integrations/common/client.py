"""
Base integration client for external API interactions.

This module provides a common interface for interacting with external APIs,
including consistent error handling, authentication, retry mechanisms, and
request functionality that can be extended by specific API integrations.
"""

import abc
import json
import time
import requests
from typing import Dict, List, Union, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result

from ...utils.logging import logger, mask_sensitive_data

# Import constants with fallback values
try:
    from ...utils.constants import API_TIMEOUT_DEFAULT, API_RETRY_DEFAULT
except ImportError:
    # Default values if not defined in constants
    API_TIMEOUT_DEFAULT = 30  # 30 seconds default timeout
    API_RETRY_DEFAULT = 3     # 3 retries by default

# Define authentication methods
AUTH_METHODS = {'api_key', 'oauth', 'basic', 'bearer', 'none'}

# Configure logger
logger = logger(__name__)


class BaseIntegrationClient(abc.ABC):
    """
    Abstract base class for integration clients providing common HTTP request handling,
    authentication, error management and retry mechanisms.
    """

    def __init__(
        self,
        base_url: str,
        auth_config: Dict[str, Any],
        auth_method: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        verify_ssl: bool = True
    ):
        """
        Initialize the integration client with connection parameters.

        Args:
            base_url: Base URL for the API
            auth_config: Authentication configuration (keys, tokens, credentials)
            auth_method: Authentication method ('api_key', 'oauth', 'basic', 'bearer', 'none')
            headers: Additional HTTP headers to include in requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
            verify_ssl: Whether to verify SSL certificates
        """
        # Store the provided parameters as instance variables
        self.base_url = base_url.rstrip('/')
        self.auth_config = auth_config
        self.headers = headers or {}
        self.timeout = timeout or API_TIMEOUT_DEFAULT
        self.max_retries = max_retries or API_RETRY_DEFAULT
        self.verify_ssl = verify_ssl

        # Validate auth_method against supported AUTH_METHODS
        if auth_method not in AUTH_METHODS:
            raise ValueError(f"Unsupported authentication method: {auth_method}. "
                             f"Supported methods: {', '.join(AUTH_METHODS)}")
        self.auth_method = auth_method

        # Initialize a requests session
        self.session = requests.Session()
        self.session.verify = verify_ssl

        # Apply default headers to the session
        default_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'JusticeBid/1.0'
        }
        # Update with custom headers
        default_headers.update(self.headers)
        self.session.headers.update(default_headers)

        # Log client initialization with masked auth_config
        masked_auth = mask_sensitive_data(self.auth_config)
        logger.info(
            f"Initialized {self.__class__.__name__} for {self.base_url}",
            extra={
                'additional_data': {
                    'base_url': self.base_url,
                    'auth_method': self.auth_method,
                    'auth_config': masked_auth,
                    'timeout': self.timeout,
                    'max_retries': self.max_retries,
                    'verify_ssl': self.verify_ssl
                }
            }
        )

    @abc.abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the external system.

        This method should be implemented by subclasses to handle authentication
        based on the specified auth_method and auth_config.

        Returns:
            bool: True if authentication is successful, False otherwise
        """
        pass

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        raw_response: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make an HTTP request to the external API with error handling and retries.

        Args:
            method: HTTP method ('GET', 'POST', 'PUT', 'DELETE', etc.)
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            data: Form data to send
            json_data: JSON data to send
            headers: Additional headers for this request
            timeout: Request timeout (overrides instance timeout)
            raw_response: If True, return the raw Response object instead of JSON

        Returns:
            Union[dict, requests.Response]: JSON response as dictionary or raw Response object

        Raises:
            ApiError: Base class for API-related errors
            ApiAuthenticationError: Authentication failed (401, 403)
            ApiRateLimitError: Rate limit exceeded (429)
            ApiResourceNotFoundError: Resource not found (404)
            ApiServerError: Server-side error (5xx)
        """
        # Prepare request parameters
        request_timeout = timeout if timeout is not None else self.timeout
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        # Construct full URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Log outgoing request details with masked sensitive data
        masked_params = mask_sensitive_data(params) if params else None
        masked_data = mask_sensitive_data(data) if data else None
        masked_json = mask_sensitive_data(json_data) if json_data else None
        masked_headers = mask_sensitive_data(request_headers)

        logger.debug(
            f"Making {method} request to {url}",
            extra={
                'additional_data': {
                    'method': method,
                    'url': url,
                    'params': masked_params,
                    'data': masked_data,
                    'json': masked_json,
                    'headers': masked_headers,
                    'timeout': request_timeout
                }
            }
        )

        # Define retry strategy function
        def retry_if_should_retry(exception):
            return self.should_retry(exception)

        # Use tenacity to implement retry logic for failed requests
        @retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_should_retry,
            reraise=True
        )
        def make_request():
            try:
                start_time = time.time()
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=request_headers,
                    timeout=request_timeout
                )
                elapsed_time = time.time() - start_time

                # Log response status and timing
                logger.debug(
                    f"{method} request to {url} completed with status {response.status_code}",
                    extra={
                        'additional_data': {
                            'status_code': response.status_code,
                            'elapsed_time': f"{elapsed_time:.3f}s",
                            'content_length': len(response.content) if response.content else 0
                        }
                    }
                )

                # Raise HTTPError for bad responses
                response.raise_for_status()

                # Return raw response if requested
                if raw_response:
                    return response

                # Return JSON response
                if response.content:
                    return response.json()
                return {}

            except requests.exceptions.HTTPError as e:
                self.handle_error(e.response)
            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Request failed: {str(e)}",
                    extra={
                        'additional_data': {
                            'method': method,
                            'url': url,
                            'error': str(e)
                        }
                    }
                )
                raise ApiError(f"Request failed: {str(e)}")

        return make_request()

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        raw_response: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a GET request to the external API.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout
            raw_response: If True, return the raw Response object

        Returns:
            Union[dict, requests.Response]: Response from the API
        """
        return self.request(
            method='GET',
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout,
            raw_response=raw_response
        )

    def post(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        raw_response: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a POST request to the external API.

        Args:
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            json_data: JSON data
            headers: Additional headers
            timeout: Request timeout
            raw_response: If True, return the raw Response object

        Returns:
            Union[dict, requests.Response]: Response from the API
        """
        return self.request(
            method='POST',
            endpoint=endpoint,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            timeout=timeout,
            raw_response=raw_response
        )

    def put(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        raw_response: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a PUT request to the external API.

        Args:
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            json_data: JSON data
            headers: Additional headers
            timeout: Request timeout
            raw_response: If True, return the raw Response object

        Returns:
            Union[dict, requests.Response]: Response from the API
        """
        return self.request(
            method='PUT',
            endpoint=endpoint,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            timeout=timeout,
            raw_response=raw_response
        )

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        raw_response: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a DELETE request to the external API.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout
            raw_response: If True, return the raw Response object

        Returns:
            Union[dict, requests.Response]: Response from the API
        """
        return self.request(
            method='DELETE',
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout,
            raw_response=raw_response
        )

    def handle_error(self, response: requests.Response) -> None:
        """
        Handle API error responses and raise appropriate exceptions.

        Args:
            response: Response object from a failed request

        Raises:
            ApiError: Base class for API-related errors
            ApiAuthenticationError: Authentication failed (401, 403)
            ApiRateLimitError: Rate limit exceeded (429)
            ApiResourceNotFoundError: Resource not found (404)
            ApiServerError: Server-side error (5xx)
        """
        status_code = response.status_code
        
        # Try to extract error details from response
        error_data = {}
        try:
            if response.content:
                error_data = response.json()
        except (ValueError, json.JSONDecodeError):
            error_data = {'raw_response': response.text[:1000]}

        # Log error details
        logger.error(
            f"API error: {status_code}",
            extra={
                'additional_data': {
                    'status_code': status_code,
                    'url': response.url,
                    'method': response.request.method,
                    'error_data': error_data
                }
            }
        )

        # Determine appropriate exception type based on status code
        error_message = error_data.get('message', error_data.get('error', str(response.reason)))
        
        if status_code == 401 or status_code == 403:
            raise ApiAuthenticationError(f"Authentication failed: {error_message}", status_code, error_data)
        
        elif status_code == 404:
            raise ApiResourceNotFoundError(f"Resource not found: {error_message}", status_code, error_data)
        
        elif status_code == 429:
            retry_after = response.headers.get('Retry-After', 60)
            try:
                retry_after = int(retry_after)
            except ValueError:
                retry_after = 60
            raise ApiRateLimitError(f"Rate limit exceeded: {error_message}", status_code, error_data, retry_after)
        
        elif 500 <= status_code < 600:
            raise ApiServerError(f"Server error: {error_message}", status_code, error_data)
        
        else:
            raise ApiError(f"API error ({status_code}): {error_message}", status_code, error_data)

    def close(self) -> None:
        """
        Close the API client session.
        """
        if self.session:
            self.session.close()
            logger.debug(f"Closed session for {self.base_url}")

    def test_connection(self) -> bool:
        """
        Test the connection to the external API.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            logger.info(f"Testing connection to {self.base_url}")
            
            # Authenticate if not using 'none' auth method
            if self.auth_method != 'none':
                authenticated = self.authenticate()
                if not authenticated:
                    logger.error(f"Authentication failed during connection test to {self.base_url}")
                    return False
            
            # Make a simple GET request to a health or status endpoint
            # This method should be overridden by subclasses to use appropriate endpoints
            response = self.get('', raw_response=True)
            
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

    def should_retry(self, exception: Exception) -> bool:
        """
        Determine if a failed request should be retried based on status code.

        Args:
            exception: The exception that occurred

        Returns:
            bool: True if the request should be retried, False otherwise
        """
        # Retry on connection errors, timeout errors, or 5xx server errors
        if isinstance(exception, requests.exceptions.ConnectionError):
            logger.info(f"Retrying due to connection error: {str(exception)}")
            return True
            
        if isinstance(exception, requests.exceptions.Timeout):
            logger.info(f"Retrying due to timeout: {str(exception)}")
            return True
            
        if isinstance(exception, ApiServerError):
            logger.info(f"Retrying due to server error: {str(exception)}")
            return True
            
        if isinstance(exception, ApiRateLimitError):
            logger.info(f"Retrying due to rate limit error: {str(exception)}")
            return True
            
        # Don't retry on client errors or other exceptions
        logger.info(f"Not retrying for exception: {type(exception).__name__} - {str(exception)}")
        return False


class ApiError(Exception):
    """
    Base exception class for API client errors.
    """
    
    def __init__(self, message: str, status_code: int = None, response_data: Dict[str, Any] = None):
        """
        Initialize the API error with details about the failed request.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Additional response data for debugging
        """
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.response_data = response_data or {}


class ApiAuthenticationError(ApiError):
    """
    Exception for API authentication failures (401, 403).
    """
    
    def __init__(self, message: str, status_code: int = None, response_data: Dict[str, Any] = None):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Additional response data for debugging
        """
        super().__init__(message, status_code, response_data)


class ApiRateLimitError(ApiError):
    """
    Exception for API rate limit errors (429).
    """
    
    def __init__(self, message: str, status_code: int = None, response_data: Dict[str, Any] = None, retry_after: int = None):
        """
        Initialize rate limit error with retry information.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Additional response data for debugging
            retry_after: Seconds to wait before retrying
        """
        super().__init__(message, status_code, response_data)
        self.retry_after = retry_after


class ApiResourceNotFoundError(ApiError):
    """
    Exception for resource not found errors (404).
    """
    
    def __init__(self, message: str, status_code: int = None, response_data: Dict[str, Any] = None):
        """
        Initialize resource not found error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Additional response data for debugging
        """
        super().__init__(message, status_code, response_data)


class ApiServerError(ApiError):
    """
    Exception for server-side errors (5xx).
    """
    
    def __init__(self, message: str, status_code: int = None, response_data: Dict[str, Any] = None):
        """
        Initialize server error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Additional response data for debugging
        """
        super().__init__(message, status_code, response_data)