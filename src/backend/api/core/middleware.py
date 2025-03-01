"""
Core middleware components for the Justice Bid API, handling cross-cutting concerns such as request logging, authentication verification, error handling, CORS, and request tracing.
"""
import time
import uuid

from flask import Flask, request, g, Response, after_this_request  # flask 2.3+
from flask_cors import CORS  # flask_cors 3.0+
from werkzeug.exceptions import HTTPException  # werkzeug.exceptions 2.3+

from ..core.auth import jwt_required, get_logger, APIError, get_current_user  # src/backend/api/core/auth.py
from ..core.auth import track_event  # src/backend/api/core/auth.py
from ..core.config import API_VERSION  # src/backend/api/core/config.py


logger = get_logger('api.middleware')


def setup_middleware(app: Flask) -> Flask:
    """
    Configures and registers all middleware for the Flask application

    Args:
        app (Flask): The Flask application instance

    Returns:
        Flask: The Flask application with middleware configured
    """
    # Register CORS middleware for cross-origin requests
    CORS(app)

    # Register request_id middleware for request tracing
    request_id_middleware(app)

    # Register logging middleware for request/response logging
    logging_middleware(app)

    # Register error handling middleware
    error_handling_middleware(app)

    # Register JWT verification middleware
    jwt_verification_middleware(app)

    # Register response formatting middleware
    response_formatting_middleware(app)

    return app


def request_id_middleware(app: Flask) -> Flask:
    """
    Middleware to assign a unique ID to each request for tracing purposes

    Args:
        app (Flask): The Flask application instance

    Returns:
        Flask: Decorated Flask application with request ID middleware
    """
    @app.before_request
    def assign_request_id():
        """Assign a unique UUID to each request in g.request_id"""
        g.request_id = str(uuid.uuid4())

    @app.after_request
    def add_request_id_header(response: Response) -> Response:
        """Add the request ID to the response headers for client-side tracing"""
        response.headers['Request-ID'] = g.request_id
        return response

    return app


def logging_middleware(app: Flask) -> Flask:
    """
    Middleware to log request and response details for monitoring and debugging

    Args:
        app (Flask): The Flask application instance

    Returns:
        Flask: Decorated Flask application with logging middleware
    """
    @app.before_request
    def log_request_info():
        """Log incoming request details (method, path, client IP)"""
        logger.info(f"Incoming request: {request.method} {request.path}",
                    extra={'additional_data': {'client_ip': request.remote_addr}})
        g.start_time = time.time()

    @app.after_request
    def log_response_info(response: Response) -> Response:
        """Log response status, duration, and size after the request is processed"""
        duration = time.time() - g.start_time
        response_size = response.content_length or 0

        logger.info(f"Outgoing response: {response.status_code} {request.path}",
                    extra={'additional_data': {'duration': f"{duration:.4f}s", 'size': f"{response_size} bytes"}})

        # Track the API event for analytics
        track_event(
            event_type='api_request',
            data={'status_code': response.status_code, 'duration': duration, 'size': response_size},
            endpoint=request.path,
            method=request.method
        )
        return response

    return app


def error_handling_middleware(app: Flask) -> Flask:
    """
    Middleware to catch and format exceptions into standardized API error responses

    Args:
        app (Flask): The Flask application instance

    Returns:
        Flask: Decorated Flask application with error handling middleware
    """
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError) -> Response:
        """Handle APIError exceptions with their specified status codes and messages"""
        return handle_api_error(error)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> Response:
        """Handle HTTPException with standard HTTP error codes"""
        return handle_http_exception(error)

    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception) -> Response:
        """Handle general exceptions as 500 Internal Server Errors"""
        return handle_generic_exception(error)

    return app


def jwt_verification_middleware(app: Flask) -> Flask:
    """
    Middleware to verify JWT tokens and load current user for protected routes

    Args:
        app (Flask): The Flask application instance

    Returns:
        Flask: Decorated Flask application with JWT verification middleware
    """
    @app.before_request
    def verify_jwt_token():
        """Skip verification for public routes and OPTIONS requests, extract and validate the JWT token for protected routes"""
        if request.method == 'OPTIONS' or request.endpoint in app.view_functions and getattr(app.view_functions[request.endpoint], 'is_public', False):
            return  # Skip JWT verification for OPTIONS requests and public routes

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.warning('Authentication required: No Authorization header provided',
                           extra={'additional_data': {'endpoint': request.path}})
            return {'message': 'Authentication required'}, 401

        try:
            user = get_current_user()
            g.user = user
        except APIError as e:
            logger.warning(f'Authentication failed: {e.message}',
                           extra={'additional_data': {'endpoint': request.path}})
            return {'message': e.message}, e.status_code

    return app


def response_formatting_middleware(app: Flask) -> Flask:
    """
    Middleware to ensure consistent response formatting across the API

    Args:
        app (Flask): The Flask application instance

    Returns:
        Flask: Decorated Flask application with response formatting middleware
    """
    @app.after_request
    def format_response(response: Response) -> Response:
        """Ensure JSON responses follow the API's standard format, add standard headers"""
        # Check if the response is a JSON response
        if response.content_type == 'application/json':
            # Add standard headers like API-Version and Request-ID
            response.headers['API-Version'] = API_VERSION
            response.headers['Request-ID'] = g.request_id

        # Ensure proper content-type headers are set
        if 'Content-Type' not in response.headers:
            response.headers['Content-Type'] = 'application/json'

        return response

    return app


def handle_api_error(error: APIError) -> Response:
    """
    Error handler function for APIError exceptions

    Args:
        error (APIError): The APIError exception instance

    Returns:
        Response: Formatted error response
    """
    # Log the error details with appropriate level based on status code
    logger.error(f"APIError: {error.message}",
                 extra={'additional_data': {'error_code': error.error_code, 'status_code': error.status_code, 'details': error.details}})

    # Construct a standardized error response JSON with error code, message, and details
    response = error.to_dict()

    # Return the JSON response with the appropriate status code
    return response, error.status_code


def handle_http_exception(error: HTTPException) -> Response:
    """
    Error handler function for HTTP exceptions

    Args:
        error (HTTPException): The HTTPException instance

    Returns:
        Response: Formatted error response
    """
    # Log the HTTP exception with appropriate level based on status code
    logger.warning(f"HTTPException: {error.description}",
                   extra={'additional_data': {'status_code': error.code, 'name': error.name}})

    # Construct a standardized error response JSON with error code and message
    response = {
        'error': {
            'code': 'http_error',
            'message': error.description,
            'status_code': error.code,
            'status': error.name
        }
    }

    # Return the JSON response with the HTTP status code
    return response, error.code


def handle_generic_exception(error: Exception) -> Response:
    """
    Error handler function for all other uncaught exceptions

    Args:
        error (Exception): The Exception instance

    Returns:
        Response: Formatted error response
    """
    # Log the exception as an error with traceback
    logger.error(f"Unhandled Exception: {str(error)}", exc_info=True)

    # Construct a standardized error response without exposing internal details
    response = {
        'error': {
            'code': 'internal_server_error',
            'message': 'An unexpected error occurred. Please contact support.',
            'status_code': 500,
            'status': 'Internal Server Error'
        }
    }

    # Return the JSON response with 500 status code
    return response, 500


def format_response(response: Response) -> Response:
    """
    Function to format Flask responses according to API standards

    Args:
        response (Response): The Flask response object

    Returns:
        Response: The formatted response object
    """
    # Check if the response is a JSON response
    if response.content_type == 'application/json':
        # Add standard headers like API-Version and Request-ID
        response.headers['API-Version'] = API_VERSION
        response.headers['Request-ID'] = g.request_id

    return response