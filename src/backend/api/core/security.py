"""
Core security module for the Justice Bid Rate Negotiation System API.
Implements API-level security features including authentication middleware, request validation, CSRF protection, rate limiting, and security headers.
Serves as the central security gateway for the API layer, integrating with lower-level security utilities.
"""

import re  # standard library
import typing  # standard library
from typing import Dict, Optional  # standard library
import ipaddress  # standard library
from functools import wraps  # functools standard library

from flask import request, g, Response  # flask ^2.2.0
from marshmallow import Schema  # marshmallow ^3.19.0
from flask_limiter import rate_limit  # flask-limiter ^2.8.0

from .auth import get_current_user, validate_access_token, get_token_from_auth_header, AuthenticationError  # Import authentication functions for API security middleware
from .errors import AuthenticationError, SecurityError  # Import error classes for security-related exceptions
from .config import settings  # Import application configuration for security settings
from ...utils.security import hash_password, verify_password, generate_token, generate_csrf_token, verify_csrf_token, get_secure_headers, sanitize_input  # Import core security utilities for implementation
from ...utils.encryption import mask_pii, encrypt_string, decrypt_string  # Import encryption utilities for handling sensitive data
from ...utils.logging import get_logger  # Import logging utility for security events

# Initialize logger
logger = get_logger(__name__)

# Global variables for security configuration
ALLOWED_CONTENT_TYPES = ['application/json', 'multipart/form-data', 'application/x-www-form-urlencoded']
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
IP_WHITELIST = settings.ALLOWED_HOSTS if hasattr(settings, 'ALLOWED_HOSTS') else []
IP_BLACKLIST = []
RATE_LIMIT_DEFAULT = '100 per minute'
CSRF_EXEMPT_ENDPOINTS = ['api.auth.login', 'api.auth.refresh', 'api.health.check']


class CSRFProtection:
    """
    Class for managing CSRF token generation and validation
    """

    def __init__(self, session_key: str = '_csrf_token'):
        """
        Initialize the CSRF protection manager

        Args:
            session_key: Key to store CSRF token in session
        """
        self._session_key = session_key  # Store session key for CSRF token storage
        if not self._session_key:
            self._session_key = '_csrf_token'  # Set default session key if none provided

    def generate_token(self) -> str:
        """
        Generates a new CSRF token and stores in session

        Returns:
            Generated CSRF token
        """
        token = generate_csrf_token()  # Generate a new CSRF token using generate_csrf_token()
        # Store the token in the session using _session_key
        g.setdefault('csrf_tokens', {})[self._session_key] = token
        return token  # Return the generated token

    def validate_token(self, request_token: str) -> bool:
        """
        Validates a CSRF token against the stored session token

        Args:
            request_token: Token provided in the request

        Returns:
            True if token is valid, False otherwise
        """
        session_token = g.get('csrf_tokens', {}).get(self._session_key)  # Get the session token using _session_key
        if not session_token:
            return False  # If session token doesn't exist, return False
        # Use verify_csrf_token to validate the request token
        return verify_csrf_token(request_token, session_token)  # Return the validation result

    def get_token(self) -> str:
        """
        Gets the current CSRF token or generates a new one

        Returns:
            Current CSRF token
        """
        # Check if token exists in session using _session_key
        if self._session_key in g.get('csrf_tokens', {}):
            return g.get('csrf_tokens', {})[self._session_key]  # If token exists, return it
        else:
            return self.generate_token()  # If token doesn't exist, generate a new one


class SecurityMiddleware:
    """
    Middleware class for applying security controls to requests and responses
    """

    def __init__(self, app):
        """
        Initialize the security middleware with configuration

        Args:
            app: Flask application instance
        """
        self._csrf_protection = CSRFProtection()  # Initialize CSRF protection
        self._ip_whitelist = IP_WHITELIST  # Configure IP whitelist
        self._ip_blacklist = IP_BLACKLIST  # Configure IP blacklist
        # Setup rate limiting
        # Register request/response handlers on the app
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self) -> Optional[Response]:
        """
        Handler that runs before each request to verify security

        Returns:
            Response if security check fails, None otherwise
        """
        return verify_request_security()  # Call verify_request_security to perform security checks

    def after_request(self, response: Response) -> Response:
        """
        Handler that runs after each request to apply security headers

        Args:
            response: Flask response object

        Returns:
            Modified response with security headers
        """
        return apply_security_headers(response)  # Call apply_security_headers to add security headers


def apply_security_middleware(app) -> None:
    """Applies security middleware to the Flask application"""
    SecurityMiddleware(app)


def verify_request_security() -> Optional[Response]:
    """Validates request security before processing, applied as before_request handler"""
    content_type = request.headers.get('Content-Type')
    if not verify_content_type(content_type):
        return {'message': 'Unsupported Content-Type'}, 415

    if request.content_length > MAX_CONTENT_LENGTH:
        return {'message': 'Request too large'}, 413

    client_ip = get_client_ip()
    if not verify_ip(client_ip):
        return {'message': 'IP address blocked'}, 403

    if request.endpoint not in CSRF_EXEMPT_ENDPOINTS:
        csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('_csrf_token')
        session_token = g.get('csrf_token')
        if not verify_csrf(csrf_token, session_token):
            return {'message': 'CSRF token validation failed'}, 403

    logger.debug(f"Request security checks passed for {request.path}")
    return None


def apply_security_headers(response: Response) -> Response:
    """Applies security headers to all API responses, applied as after_request handler"""
    secure_headers = get_secure_headers()
    for key, value in secure_headers.items():
        response.headers[key] = value
    return response


def verify_content_type(content_type: str) -> bool:
    """Verifies the request content type is allowed"""
    if not content_type:
        return True
    base_content_type = content_type.split(';')[0].strip()
    return base_content_type in ALLOWED_CONTENT_TYPES


def verify_ip(ip_address: str) -> bool:
    """Verifies client IP address against whitelist and blacklist"""
    if not IP_WHITELIST and not IP_BLACKLIST:
        return True
    if IP_WHITELIST and ip_address not in IP_WHITELIST:
        return False
    if ip_address in IP_BLACKLIST:
        return False
    return True


def verify_csrf(request_token: str, session_token: str) -> bool:
    """Verifies CSRF token for state-changing requests"""
    if request.endpoint in CSRF_EXEMPT_ENDPOINTS:
        return True

    if request.method in ['GET', 'HEAD', 'OPTIONS']:
        return True

    return verify_csrf_token(request_token, session_token)


def sanitize_request_data(data: dict) -> dict:
    """Sanitizes incoming request data to prevent injection attacks"""
    sanitized_data = data.copy()
    for key, value in sanitized_data.items():
        if isinstance(value, str):
            sanitized_data[key] = sanitize_input(value)
    return sanitized_data


def validate_schema(schema_class: Schema, location: str = 'json'):
    """Decorator to validate request data against a schema"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if location == 'json':
                data = request.get_json()
            elif location == 'form':
                data = request.form
            elif location == 'args':
                data = request.args
            else:
                return {'message': 'Invalid location parameter'}, 400

            schema = schema_class()
            errors = schema.validate(data)
            if errors:
                return {'message': 'Validation error', 'errors': errors}, 400

            result = schema.load(data)
            return f(*args, **kwargs, data=result)
        return wrapper
    return decorator


def limit_rate(limit: str):
    """Decorator to apply custom rate limits to specific endpoints"""
    def decorator(f):
        @wraps(f)
        @rate_limit(limit)
        def wrapper(*args, **kwargs):
            logger.info(f"Rate limit hit for endpoint {request.endpoint} with limit {limit}")
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_csrf(route_function):
    """Decorator to explicitly require CSRF protection for a route"""
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('_csrf_token')
        session_token = g.get('csrf_token')
        if not verify_csrf(csrf_token, session_token):
            return {'message': 'CSRF token validation failed'}, 403
        return route_function(*args, **kwargs)
    return wrapper


def exempt_csrf(route_function):
    """Decorator to exempt a route from CSRF protection"""
    route_function.csrf_exempt = True
    return route_function


def mask_sensitive_data(data: dict, fields_to_mask: list) -> dict:
    """Masks sensitive data in API responses"""
    masked_data = data.copy()
    for field in fields_to_mask:
        if field in masked_data:
            masked_data[field] = mask_pii(masked_data[field])
    return masked_data


def encode_sensitive_data(data: dict, fields_to_encrypt: list) -> dict:
    """Encrypts sensitive data in API responses"""
    encoded_data = data.copy()
    for field in fields_to_encrypt:
        if field in encoded_data and encoded_data[field] is not None:
            encoded_data[field] = encrypt_string(encoded_data[field])
    return encoded_data


def decode_sensitive_data(data: dict, fields_to_decrypt: list) -> dict:
    """Decrypts sensitive data from API requests"""
    decoded_data = data.copy()
    for field in fields_to_decrypt:
        if field in decoded_data and decoded_data[field] is not None:
            decoded_data[field] = decrypt_string(decoded_data[field])
    return decoded_data


def get_client_ip() -> str:
    """Gets the client IP address from the request"""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        return '127.0.0.1'


def log_security_event(event_type: str, event_data: dict) -> None:
    """Logs security-related events for audit purposes"""
    sanitized_data = sanitize_request_data(event_data)
    sanitized_data['timestamp'] = datetime.utcnow().isoformat()
    sanitized_data['request_url'] = request.url
    sanitized_data['request_method'] = request.method
    sanitized_data['remote_addr'] = request.remote_addr

    logger.info(f"Security Event: {event_type}", extra={'additional_data': sanitized_data})