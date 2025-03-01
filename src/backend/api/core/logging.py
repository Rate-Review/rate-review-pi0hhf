"""
API-level logging configuration for the Justice Bid Rate Negotiation System.

This module configures structured logging for API requests and responses, 
provides correlation ID tracking across services, and ensures sensitive data
is properly masked for security compliance.
"""

import logging
import uuid
import flask
import json
import typing
from typing import Any, Dict, Optional
import traceback
import time
from flask import g, request, Flask

from ..core.config import get_config
from ...utils.logging import setup_logger, JsonFormatter

# Logging constants
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(correlation_id)s] %(name)s: %(message)s"
JSON_LOG_FORMAT = """{"timestamp": "%(asctime)s", "level": "%(levelname)s", "correlation_id": "%(correlation_id)s", "logger": "%(name)s", "message": "%(message)s", "additional_data": "%(additional_data)s"}"""
SENSITIVE_FIELDS = ["password", "token", "secret", "authorization", "api_key", "credit_card", "ssn"]
REQUEST_START_TIME_KEY = "request_start_time"


class CorrelationIdFilter(logging.Filter):
    """Logging filter that adds correlation ID to log records."""
    
    def __init__(self):
        """Initialize the correlation ID filter."""
        super(CorrelationIdFilter, self).__init__()
        self.correlation_id = None
        
    def filter(self, record):
        """
        Add correlation ID to the log record.
        
        Args:
            record (logging.LogRecord): The log record to process
            
        Returns:
            bool: True (always passes the filter)
        """
        record.correlation_id = get_correlation_id()
        
        # Ensure additional_data attribute exists
        if not hasattr(record, 'additional_data'):
            record.additional_data = {}
            
        return True


class RequestLogger:
    """Class for handling request/response logging in Flask applications."""
    
    def __init__(self, app: Flask):
        """
        Initialize the request logger with a Flask application.
        
        Args:
            app (Flask): The Flask application to monitor
        """
        self.app = app
        self.logger = get_api_logger("api.request")
        
        # Register Flask request handlers
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
    def before_request(self):
        """
        Handler called before each request to log request details.
        
        Returns:
            None
        """
        log_request()
        
    def after_request(self, response):
        """
        Handler called after each request to log response details.
        
        Args:
            response: Flask response object
            
        Returns:
            response: The same response object, unmodified
        """
        return log_response(response)


def setup_api_logging(app: Flask) -> None:
    """
    Initialize and configure API logging for the Justice Bid application.
    
    This function sets up structured JSON logging, request/response logging,
    correlation ID tracking, and integrates with Flask's error handlers.
    
    Args:
        app (Flask): The Flask application to configure logging for
        
    Returns:
        None
    """
    config = get_config()
    log_level = config.LOG_LEVEL
    
    # Configure basic logging
    setup_logger(log_level=log_level, json_format=True)
    
    # Get root logger and ensure it has our correlation ID filter
    root_logger = logging.getLogger()
    correlation_filter = CorrelationIdFilter()
    
    for handler in root_logger.handlers:
        if not any(isinstance(f, CorrelationIdFilter) for f in handler.filters):
            handler.addFilter(correlation_filter)
    
    # Configure Flask logging
    app.logger.setLevel(getattr(logging, log_level))
    
    # Setup request logging
    RequestLogger(app)
    
    # Log application startup
    app_logger = get_api_logger("api.startup")
    app_logger.info(
        f"API logging initialized",
        extra={
            "additional_data": {
                "log_level": log_level,
                "environment": config.FLASK_ENV if hasattr(config, "FLASK_ENV") else "unknown"
            }
        }
    )


def get_api_logger(name: str) -> logging.Logger:
    """
    Get a properly configured logger instance for API components.
    
    Args:
        name (str): Name of the logger
        
    Returns:
        logging.Logger: Configured logger instance with correlation ID filter
    """
    logger = logging.getLogger(name)
    
    # Ensure logger has correlation ID filter
    correlation_filter = CorrelationIdFilter()
    if not any(isinstance(f, CorrelationIdFilter) for f in logger.filters):
        logger.addFilter(correlation_filter)
    
    return logger


def get_correlation_id() -> str:
    """
    Get the current correlation ID from the request context or generate a new one.
    
    Returns:
        str: Correlation ID for the current request
    """
    # Try to get from Flask request headers
    if flask.has_request_context():
        # First check if we already stored it in g
        if hasattr(g, 'correlation_id'):
            return g.correlation_id
        
        # Check request headers
        correlation_id = request.headers.get('X-Correlation-ID')
        if correlation_id:
            # Store in g for future use in this request
            g.correlation_id = correlation_id
            return correlation_id
    
    # Generate a new ID if not found
    new_id = str(uuid.uuid4())
    
    # Store in Flask g if in request context
    if flask.has_request_context():
        g.correlation_id = new_id
        
    return new_id


def log_request() -> None:
    """
    Log details of an incoming API request.
    
    Returns:
        None
    """
    if not flask.has_request_context():
        return
    
    logger = get_api_logger("api.request")
    
    # Extract request information
    method = request.method
    path = request.path
    params = request.args.to_dict() if request.args else {}
    headers = dict(request.headers)
    data = {}
    
    # Try to get request data if available
    try:
        if request.data:
            data = json.loads(request.data.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        # Not JSON or not decodable
        data = {"raw_data_size": len(request.data) if request.data else 0}
    
    # Mask sensitive information
    masked_headers = mask_sensitive_data(headers)
    masked_params = mask_sensitive_data(params)
    masked_data = mask_sensitive_data(data)
    
    # Store request start time for timing
    g.request_start_time = time.time()
    
    # Log the request
    logger.info(
        f"Received request: {method} {path}",
        extra={
            "additional_data": {
                "method": method,
                "path": path,
                "params": masked_params,
                "headers": masked_headers,
                "body": masked_data,
                "client_ip": request.remote_addr
            }
        }
    )


def log_response(response) -> flask.Response:
    """
    Log details of an API response.
    
    Args:
        response: Flask response object
        
    Returns:
        response: The same response object, unmodified
    """
    if not flask.has_request_context():
        return response
    
    logger = get_api_logger("api.response")
    
    # Calculate response time
    start_time = getattr(g, 'request_start_time', None)
    response_time_ms = None
    if start_time:
        response_time_ms = int((time.time() - start_time) * 1000)
    
    # Extract response information
    status_code = response.status_code
    headers = dict(response.headers)
    size = response.calculate_content_length() if hasattr(response, 'calculate_content_length') else len(response.data) if hasattr(response, 'data') else 0
    
    # Try to get response data if it's JSON
    response_data = {}
    if response.mimetype == 'application/json' and hasattr(response, 'json'):
        response_data = response.json
    elif hasattr(response, 'data'):
        try:
            response_data = json.loads(response.data.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            # Not JSON or not decodable
            response_data = {"raw_data_size": len(response.data) if response.data else 0}
    
    # Mask sensitive information
    masked_headers = mask_sensitive_data(headers)
    masked_data = mask_sensitive_data(response_data)
    
    # Log the response
    logger.info(
        f"Sending response: {status_code}",
        extra={
            "additional_data": {
                "status_code": status_code,
                "headers": masked_headers,
                "body": masked_data,
                "size_bytes": size,
                "response_time_ms": response_time_ms,
            }
        }
    )
    
    return response


def mask_sensitive_data(data: Any) -> Any:
    """
    Mask sensitive information in dictionaries, lists, or strings.
    
    Args:
        data: Data to mask sensitive fields in
        
    Returns:
        Data with sensitive information masked
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            # Check if the key is a sensitive field
            if any(sensitive_key in key.lower() for sensitive_key in SENSITIVE_FIELDS):
                result[key] = "***REDACTED***"
            else:
                # Recursively process nested structures
                result[key] = mask_sensitive_data(value)
        return result
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    elif isinstance(data, (str, int, float, bool, type(None))):
        return data
    else:
        # For other types, return as string to ensure safe logging
        try:
            return str(data)
        except Exception:
            return "***UNPRINTABLE***"


def log_exception(exception: Exception, context: Dict = None) -> None:
    """
    Log detailed information about an exception.
    
    Args:
        exception: The exception to log
        context: Additional context information
        
    Returns:
        None
    """
    logger = get_api_logger("api.exception")
    
    # Get traceback information
    tb_lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
    tb_text = ''.join(tb_lines)
    
    # Basic exception information
    exc_info = {
        'exception_type': exception.__class__.__name__,
        'exception_message': str(exception),
        'traceback': tb_text
    }
    
    # Add request information if available
    if flask.has_request_context():
        exc_info['request'] = {
            'method': request.method,
            'path': request.path,
            'client_ip': request.remote_addr
        }
    
    # Add context if provided
    if context:
        # Mask any sensitive data in context
        safe_context = mask_sensitive_data(context)
        exc_info['context'] = safe_context
    
    # Log the exception
    logger.error(
        f"Exception occurred: {str(exception)}",
        extra={"additional_data": exc_info},
        exc_info=True
    )