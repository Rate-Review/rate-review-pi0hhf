"""
Logging utilities for the Justice Bid Rate Negotiation System backend.

This module provides structured logging capabilities with JSON formatting,
correlation ID tracking, and sensitive data masking to ensure comprehensive
observability while maintaining security and compliance.
"""

import logging
import json
import os
import sys
import typing
import traceback
from datetime import datetime
from pythonjsonlogger import jsonlogger

from .constants import ErrorCode

# Default logging configuration
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
JSON_LOG_FORMAT = """{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "additional_data": "%(additional_data)s"}"""
SENSITIVE_FIELDS = ["password", "token", "secret", "authorization", "api_key", "credit_card", "ssn"]


class JsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for structured logging with additional data support.
    
    This formatter extends the standard JsonFormatter to handle additional
    contextual data and ensures sensitive information is properly masked.
    """
    
    def __init__(self, format_str=None, json_format=True):
        """
        Initialize the JSON formatter.
        
        Args:
            format_str (str): Format string for the log message
            json_format (bool): Whether to format logs as JSON
        """
        super(JsonFormatter, self).__init__(format_str)
        self.json_format = json_format
    
    def format(self, record):
        """
        Format log record as JSON or standard format.
        
        Args:
            record (logging.LogRecord): The log record to format
            
        Returns:
            str: Formatted log message
        """
        # Ensure record has additional_data attribute
        if not hasattr(record, 'additional_data'):
            record.additional_data = {}
        
        if self.json_format:
            # Convert additional_data to string if it's not already
            if isinstance(record.additional_data, dict):
                # Mask sensitive data
                record.additional_data = mask_sensitive_data(record.additional_data)
                record.additional_data = json.dumps(record.additional_data)
            return super(JsonFormatter, self).format(record)
        else:
            # Standard formatting
            return super(JsonFormatter, self).format(record)
    
    def add_fields(self, log_record, record, message_dict):
        """
        Add custom fields to the log record for JSON formatting.
        
        Args:
            log_record (dict): The log record being built
            record (logging.LogRecord): The original log record
            message_dict (dict): Additional message dictionary
            
        Returns:
            None
        """
        super(JsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add additional_data if present
        if hasattr(record, 'additional_data') and record.additional_data:
            if isinstance(record.additional_data, str):
                try:
                    log_record['additional_data'] = json.loads(record.additional_data)
                except json.JSONDecodeError:
                    log_record['additional_data'] = record.additional_data
            else:
                log_record['additional_data'] = record.additional_data
        
        # Add correlation ID if present
        if hasattr(record, 'correlation_id') and record.correlation_id:
            log_record['correlation_id'] = record.correlation_id
        
        # Add service name if present
        if hasattr(record, 'service_name') and record.service_name:
            log_record['service'] = record.service_name
            
        # Sanitize any sensitive fields
        mask_sensitive_data(log_record)


class AdditionalDataFilter(logging.Filter):
    """
    Logging filter that ensures additional_data field is present in log records.
    
    This filter adds an empty additional_data dictionary to records that
    don't already have one, ensuring consistency in log structure.
    """
    
    def __init__(self):
        """Initialize the filter."""
        super(AdditionalDataFilter, self).__init__()
    
    def filter(self, record):
        """
        Add additional_data field if not present.
        
        Args:
            record (logging.LogRecord): The log record to process
            
        Returns:
            bool: True (always passes the filter)
        """
        if not hasattr(record, 'additional_data'):
            record.additional_data = {}
        return True


def setup_logging(log_level=None, json_format=True, log_file=None):
    """
    Configure application-wide logging settings based on environment.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format (bool): Whether to use JSON formatting for logs
        log_file (str): Path to log file (if None, logs to console only)
        
    Returns:
        None
    """
    # Get log level from parameter, environment, or default
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
    
    numeric_level = getattr(logging, log_level.upper(), DEFAULT_LOG_LEVEL)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Add additional data filter
    console_handler.addFilter(AdditionalDataFilter())
    
    # Set formatter based on json_format flag
    if json_format:
        formatter = JsonFormatter(JSON_LOG_FORMAT, json_format=True)
    else:
        formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.addFilter(AdditionalDataFilter())
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Log configuration
    root_logger.info(
        f"Logging configured",
        extra={
            "additional_data": {
                "level": log_level,
                "json_format": json_format,
                "log_file": log_file
            }
        }
    )


def get_logger(name, log_level=None, json_format=True):
    """
    Get a configured logger instance with appropriate formatting.
    
    Args:
        name (str): Name of the logger
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format (bool): Whether to use JSON formatting for logs
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level if specified, otherwise inherit from root
    if log_level:
        numeric_level = getattr(logging, log_level.upper(), DEFAULT_LOG_LEVEL)
        logger.setLevel(numeric_level)
    
    # Ensure all handlers have proper formatters
    for handler in logger.handlers:
        if json_format:
            handler.setFormatter(JsonFormatter(JSON_LOG_FORMAT, json_format=True))
        else:
            handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        
        # Add additional data filter if not present
        if not any(isinstance(f, AdditionalDataFilter) for f in handler.filters):
            handler.addFilter(AdditionalDataFilter())
    
    return logger


def mask_sensitive_data(data):
    """
    Recursively mask sensitive fields in data structures to prevent logging sensitive information.
    
    Args:
        data (Any): Data to mask sensitive fields in
        
    Returns:
        Any: Data with sensitive fields masked
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
        # For other types, convert to string to ensure safe logging
        try:
            return str(data)
        except Exception:
            return "***UNPRINTABLE***"


def format_exception(exc, context=None):
    """
    Format exception information for logging.
    
    Args:
        exc (Exception): The exception to format
        context (dict): Additional context information
        
    Returns:
        str: Formatted exception message with context
    """
    # Format exception traceback
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    tb_text = ''.join(tb_lines)
    
    # Basic exception information
    exc_info = {
        'exception_type': exc.__class__.__name__,
        'exception_message': str(exc),
        'traceback': tb_text
    }
    
    # Add context if provided
    if context:
        # Mask any sensitive data in context
        context = mask_sensitive_data(context)
        exc_info['context'] = context
    
    return json.dumps(exc_info)


def log_exception(logger, exc, context=None):
    """
    Log an exception with context information at ERROR level.
    
    Args:
        logger (logging.Logger): Logger to use
        exc (Exception): The exception to log
        context (dict): Additional context information
        
    Returns:
        None
    """
    # Format the exception
    exc_message = format_exception(exc, context)
    
    # Additional data for structured logging
    additional_data = {
        'exception_type': exc.__class__.__name__,
    }
    
    # Add error code if available
    if context and 'error_code' in context:
        additional_data['error_code'] = context['error_code']
    elif isinstance(exc, ValueError) and hasattr(exc, 'error_code'):
        additional_data['error_code'] = exc.error_code
    else:
        additional_data['error_code'] = ErrorCode.SYSTEM_ERROR.value
    
    # Log the exception
    logger.error(
        f"Exception occurred: {str(exc)}",
        extra={'additional_data': additional_data},
        exc_info=True
    )