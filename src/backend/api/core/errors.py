"""
Standardized error handling for the Justice Bid Rate Negotiation System API.

This module provides a consistent approach to API error responses, ensuring
uniform error handling across all endpoints while maintaining appropriate
error details for debugging and monitoring.
"""

from werkzeug.exceptions import HTTPException
import typing
import json
from pydantic import ValidationError

from ...utils.constants import ErrorCode
from ...utils.logging import get_logger, format_exception

# Set up logger for error handling
logger = get_logger('api.errors')

# HTTP status codes and their descriptions
HTTP_STATUS_CODES = {
    '400': 'Bad Request',
    '401': 'Unauthorized',
    '403': 'Forbidden',
    '404': 'Not Found',
    '409': 'Conflict',
    '422': 'Unprocessable Entity',
    '429': 'Too Many Requests',
    '500': 'Internal Server Error',
    '503': 'Service Unavailable'
}


def format_error_response(error_code: ErrorCode, message: str, details: dict = None, 
                         status_code: int = 400) -> dict:
    """
    Format an error into a standardized API error response.

    Args:
        error_code (ErrorCode): The error code enum value
        message (str): Human-readable error message
        details (dict, optional): Additional error details
        status_code (int, optional): HTTP status code

    Returns:
        dict: Standardized error response dictionary
    """
    response = {
        'error': {
            'code': error_code.value,
            'message': message,
            'status_code': status_code,
            'status': HTTP_STATUS_CODES.get(str(status_code), 'Unknown Error')
        }
    }

    # Add request ID if available in Flask context
    try:
        from flask import g
        if hasattr(g, 'request_id'):
            response['error']['request_id'] = g.request_id
    except ImportError:
        # Flask context not available
        pass

    # Add details if provided
    if details:
        response['error']['details'] = details

    return response


def handle_validation_errors(error: ValidationError) -> dict:
    """
    Convert Pydantic validation errors to a standardized format.

    Args:
        error (ValidationError): The Pydantic validation error

    Returns:
        dict: Formatted validation errors dictionary
    """
    formatted_errors = []
    
    for error in error.errors():
        error_entry = {
            'location': error.get('loc', []),
            'field': error.get('loc', [''])[0] if error.get('loc') else '',
            'message': error.get('msg', 'Validation error')
        }
        formatted_errors.append(error_entry)
    
    return {'validation_errors': formatted_errors}


def log_error(error: 'APIError', context: dict = None) -> None:
    """
    Log error details with appropriate severity based on status code.

    Args:
        error (APIError): The API error to log
        context (dict, optional): Additional context information

    Returns:
        None
    """
    log_context = {
        'error_code': error.error_code.value,
        'status_code': error.status_code,
    }
    
    if context:
        log_context.update(context)
    
    error_message = f"{error.error_code.value}: {error.message}"
    
    # Determine log level based on status code
    if error.status_code >= 500:
        # Server errors are logged at ERROR level with stack trace
        logger.error(
            error_message,
            extra={'additional_data': log_context},
            exc_info=True
        )
    elif error.status_code >= 400:
        # Client errors are logged at WARNING level
        logger.warning(
            error_message,
            extra={'additional_data': log_context}
        )
    else:
        # Other status codes are logged at INFO level
        logger.info(
            error_message,
            extra={'additional_data': log_context}
        )


class APIError(Exception):
    """
    Base exception class for all API errors with standardized formatting.
    
    This is the parent class for all API-specific exceptions to ensure
    consistent error handling across the application.
    """
    
    def __init__(self, message: str, error_code: ErrorCode, 
                 status_code: int = 400, details: dict = None):
        """
        Initialize an API error with standard attributes.

        Args:
            message (str): Human-readable error message
            error_code (ErrorCode): The error code enum value
            status_code (int, optional): HTTP status code
            details (dict, optional): Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        
        # Log the error
        log_error(self, {'details': self.details})
    
    def to_dict(self) -> dict:
        """
        Convert the error to a dictionary for JSON serialization.

        Returns:
            dict: Error as a dictionary
        """
        return format_error_response(
            self.error_code,
            self.message,
            self.details,
            self.status_code
        )


class ValidationException(APIError):
    """
    Exception for validation errors (typically from Pydantic validation).
    
    Used when request data fails validation checks.
    """
    
    def __init__(self, message: str, errors: list):
        """
        Initialize a validation exception.

        Args:
            message (str): Human-readable error message
            errors (list): List of validation errors
        """
        self.validation_errors = errors
        details = {'validation_errors': errors}
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details
        )


class AuthenticationException(APIError):
    """
    Exception for authentication failures.
    
    Used when a user cannot be authenticated properly.
    """
    
    def __init__(self, message: str, details: dict = None):
        """
        Initialize an authentication exception.

        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_ERROR,
            status_code=401,
            details=details
        )


class AuthorizationException(APIError):
    """
    Exception for authorization failures (permission denied).
    
    Used when a user is authenticated but does not have the required permissions.
    """
    
    def __init__(self, message: str, details: dict = None):
        """
        Initialize an authorization exception.

        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHORIZATION_ERROR,
            status_code=403,
            details=details
        )


class ResourceNotFoundException(APIError):
    """
    Exception for resource not found errors.
    
    Used when a requested resource does not exist.
    """
    
    def __init__(self, resource_type: str, resource_id: str, details: dict = None):
        """
        Initialize a resource not found exception.

        Args:
            resource_type (str): Type of resource that was not found
            resource_id (str): ID of the resource that was not found
            details (dict, optional): Additional error details
        """
        message = f"{resource_type} with ID '{resource_id}' not found"
        details = details or {}
        details.update({
            'resource_type': resource_type,
            'resource_id': resource_id
        })
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            status_code=404,
            details=details
        )


class ResourceConflictException(APIError):
    """
    Exception for resource conflicts (e.g., duplicate resources).
    
    Used when an operation cannot be completed due to a conflict.
    """
    
    def __init__(self, message: str, details: dict = None):
        """
        Initialize a resource conflict exception.

        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_CONFLICT,
            status_code=409,
            details=details
        )


class RateRuleViolationException(APIError):
    """
    Exception for violations of client rate rules.
    
    Used when a rate submission violates client-defined rate rules.
    """
    
    def __init__(self, message: str, details: dict = None):
        """
        Initialize a rate rule violation exception.

        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_RULE_VIOLATION,
            status_code=422,
            details=details
        )


class InvalidStateTransitionException(APIError):
    """
    Exception for invalid state transitions in workflows.
    
    Used when an operation attempts to transition an entity to an invalid state.
    """
    
    def __init__(self, current_state: str, target_state: str, 
                entity_type: str, details: dict = None):
        """
        Initialize an invalid state transition exception.

        Args:
            current_state (str): Current state of the entity
            target_state (str): Target state that was invalid
            entity_type (str): Type of entity (rate, negotiation, etc.)
            details (dict, optional): Additional error details
        """
        message = f"Cannot transition {entity_type} from '{current_state}' to '{target_state}'"
        details = details or {}
        details.update({
            'current_state': current_state,
            'target_state': target_state,
            'entity_type': entity_type
        })
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_STATE_TRANSITION,
            status_code=422,
            details=details
        )


class IntegrationException(APIError):
    """
    Exception for external integration failures.
    
    Used when an operation fails due to an external integration issue.
    """
    
    def __init__(self, message: str, integration_name: str, details: dict = None):
        """
        Initialize an integration exception.

        Args:
            message (str): Human-readable error message
            integration_name (str): Name of the integration that failed
            details (dict, optional): Additional error details
        """
        details = details or {}
        details['integration_name'] = integration_name
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INTEGRATION_ERROR,
            status_code=503,
            details=details
        )


class SystemException(APIError):
    """
    Exception for internal system errors.
    
    Used for unexpected errors and system failures.
    """
    
    def __init__(self, message: str, details: dict = None):
        """
        Initialize a system exception.

        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        # Ensure we don't expose sensitive information in details
        safe_details = {}
        if details:
            for key, value in details.items():
                # Only include safe keys and don't expose stack traces or sensitive data
                if key not in ['stack_trace', 'password', 'token', 'secret']:
                    safe_details[key] = value
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SYSTEM_ERROR,
            status_code=500,
            details=safe_details
        )