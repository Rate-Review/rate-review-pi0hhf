"""
Initialization file for the common integration module that provides shared functionality,
base classes, and error types for integrating with external systems like eBilling
platforms, law firm systems, and UniCourt.
"""

from .adapter import BaseAdapter
from .client import BaseClient
from .mapper import BaseMapper

# Define the module version for tracking compatibility
VERSION = '0.1.0'

class IntegrationError(Exception):
    """Base exception class for all integration-related errors"""
    
    def __init__(self, message):
        """
        Initialize the exception with a message
        
        Args:
            message (str): Error message
        """
        super().__init__(message)


class ConnectionError(IntegrationError):
    """Exception raised when connection to external system fails"""
    
    def __init__(self, message, details=None):
        """
        Initialize the exception with a message and optional details
        
        Args:
            message (str): Error message
            details (dict): Additional error details
        """
        super().__init__(message)
        self.details = details or {}


class AuthenticationError(IntegrationError):
    """Exception raised when authentication with external system fails"""
    
    def __init__(self, message):
        """
        Initialize the exception with a message
        
        Args:
            message (str): Error message
        """
        super().__init__(message)


class ValidationError(IntegrationError):
    """Exception raised when data validation fails during integration"""
    
    def __init__(self, message, errors=None):
        """
        Initialize the exception with a message and validation errors
        
        Args:
            message (str): Error message
            errors (dict): Validation errors by field
        """
        super().__init__(message)
        self.errors = errors or {}


# Define exports
__all__ = [
    'BaseAdapter',
    'BaseClient',
    'BaseMapper',
    'IntegrationError',
    'ConnectionError',
    'AuthenticationError',
    'ValidationError',
    'VERSION'
]