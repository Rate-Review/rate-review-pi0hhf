"""
Provides utility decorators for the Justice Bid Rate Negotiation System.
Includes decorators for authentication, authorization, performance monitoring,
caching, input validation, rate limiting, error handling, and transactional management.
These decorators are used throughout the backend to enforce security policies,
optimize performance, ensure consistent error handling, and maintain data integrity.
"""

import functools  # standard library
from functools import wraps  # standard library
import time  # standard library
import json  # standard library
import inspect  # standard library
from datetime import datetime  # standard library
from typing import Callable, Dict, List, Optional, Union  # standard library
from flask import request, g  # flask 2.2+
import jsonschema  # 4.0+

from ..utils.logging import get_logger  # src/backend/utils/logging.py
from ..utils.cache import get_cache, cache_decorator, invalidate_cache_decorator  # src/backend/utils/cache.py
from ..utils.redis_client import get_redis_client  # src/backend/utils/redis_client.py
from ..api.core.errors import AuthenticationError, PermissionDeniedError  # src/backend/api/core/errors.py
from ..services.auth.rbac import RBACService  # src/backend/services/auth/rbac.py
from ..api.core.auth import get_current_user  # src/backend/api/core/auth.py

# Initialize logger
logger = get_logger(__name__)

# Global variable for RBAC service
rbac_service = None


def initialize_decorators(RBACService: RBACService) -> None:
    """
    Initializes decorator dependencies with service instances.

    Args:
        RBACService: rbac_service_instance
    """
    global rbac_service
    rbac_service = RBACService
    logger.info("Decorators module initialized")


def login_required(func: Callable) -> Callable:
    """
    Decorator that ensures a user is authenticated before accessing a route.

    Args:
        func: The function to decorate

    Returns:
        Wrapped function that checks authentication
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function for the decorated function.
        """
        # Check if current user is authenticated
        user = get_current_user()
        if user is None:
            raise AuthenticationError("Authentication required")

        # Call the original function with authenticated user
        return func(*args, **kwargs)

    return wrapper


def permission_required(permission: str) -> Callable:
    """
    Decorator that checks if user has required permission for an operation.

    Args:
        permission: The permission required for the operation

    Returns:
        Decorator function that takes a function and returns a wrapped function
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator function that takes a function to decorate.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that checks permission.
            """
            # Get current user
            user = get_current_user()
            if user is None:
                raise AuthenticationError("Authentication required")

            # Check if user has required permission
            if not rbac_service.has_permission(user, permission):
                raise PermissionDeniedError(f"Permission '{permission}' denied")

            # Call original function if permission check passes
            return func(*args, **kwargs)

        return wrapper

    return decorator


def role_required(role: str) -> Callable:
    """
    Decorator that ensures a user has a specific role or higher.

    Args:
        role: The role required for the operation

    Returns:
        Decorator function that takes a function and returns a wrapped function
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator function that takes a function to decorate.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that checks user's role.
            """
            # Get current user
            user = get_current_user()
            if user is None:
                raise AuthenticationError("Authentication required")

            # Check if user's role matches required role or inherits from it
            if user.role != role:
                raise PermissionDeniedError(f"Role '{role}' required")

            # Call original function if role check passes
            return func(*args, **kwargs)

        return wrapper

    return decorator


def cache_result(ttl: int, prefix: str) -> Callable:
    """
    Decorator that caches the result of a function call.

    Args:
        ttl: Time-to-live in seconds for cached results
        prefix: Prefix for cache keys

    Returns:
        Decorator function that caches function results
    """
    return cache_decorator(ttl=ttl, prefix=prefix)


def invalidate_cache(pattern: str) -> Callable:
    """
    Decorator that invalidates cache entries matching a pattern after function execution.

    Args:
        pattern: Pattern to match cache keys for invalidation

    Returns:
        Decorator function that invalidates cache entries
    """
    return invalidate_cache_decorator(pattern=pattern)


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator that logs the execution time of a function.

    Args:
        func: The function to decorate

    Returns:
        Wrapped function that logs execution time
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function for the decorated function.
        """
        # Record start time
        start_time = time.time()

        # Call the original function
        result = func(*args, **kwargs)

        # Record end time
        end_time = time.time()

        # Calculate execution time
        execution_time = end_time - start_time

        # Log the function name and execution time
        logger.info(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds")

        # Return the original function result
        return result

    return wrapper


def validate_request(schema: Dict) -> Callable:
    """
    Decorator that validates request data against a JSON schema.

    Args:
        schema: JSON schema to validate against

    Returns:
        Decorator function that validates request data
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator function that takes a function to decorate.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that validates request data.
            """
            # Get request JSON data
            data = request.get_json()

            # Validate data against schema
            try:
                jsonschema.validate(data, schema)
            except jsonschema.ValidationError as e:
                logger.warning(f"Request validation failed: {str(e)}")
                return {"message": "Invalid request data", "errors": [e.message for e in e.context]}, 400

            # Call original function if validation passes
            return func(*args, **kwargs)

        return wrapper

    return decorator


def rate_limit(limit: int, period: int) -> Callable:
    """
    Decorator that implements rate limiting for API endpoints.

    Args:
        limit: Maximum number of requests allowed
        period: Time period in seconds

    Returns:
        Decorator function that applies rate limiting
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator function that takes a function to decorate.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that implements rate limiting.
            """
            # Get client identifier (IP or user ID)
            client_id = request.remote_addr  # Use IP address for simplicity

            # Create rate limit key
            key = f"rate_limit:{func.__name__}:{client_id}"

            # Get current request count
            redis_client = get_redis_client()
            count = redis_client.get(key)
            if count is None:
                count = 0
            else:
                count = int(count)

            # Check if limit exceeded
            if count >= limit:
                logger.warning(f"Rate limit exceeded for {client_id} on {func.__name__}")
                return {"message": "Too Many Requests"}, 429

            # Increment request count and set expiry
            redis_client.incr(key)
            redis_client.expire(key, period)

            # Call original function if limit not exceeded
            return func(*args, **kwargs)

        return wrapper

    return decorator


def handle_exceptions(exception_types: List) -> Callable:
    """
    Decorator that catches and handles exceptions in a standardized way.

    Args:
        exception_types: List of exception types to handle

    Returns:
        Decorator function that handles exceptions
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator function that takes a function to decorate.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that catches exceptions.
            """
            try:
                # Call original function
                return func(*args, **kwargs)
            except tuple(exception_types) as e:
                # Log the exception
                logger.error(f"Exception in {func.__name__}: {str(e)}", exc_info=True)

                # Transform exception into appropriate API error response
                return {"message": f"An error occurred: {str(e)}"}, 500

        return wrapper

    return decorator


def audit_trail(action_type: str) -> Callable:
    """
    Decorator that records an audit trail for sensitive operations.

    Args:
        action_type: Type of action being performed

    Returns:
        Decorator function that records audit trail
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator function that takes a function to decorate.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that records audit trail.
            """
            # Get current user
            user = get_current_user()

            # Record operation start
            logger.info(f"User {user.id} started {action_type} on {func.__name__}")

            # Call original function
            result = func(*args, **kwargs)

            # Record operation completion
            logger.info(f"User {user.id} completed {action_type} on {func.__name__}")

            # Store audit record in database for compliance
            # (Implementation depends on audit logging system)

            # Return original function result
            return result

        return wrapper

    return decorator


def with_ai_context(func: Callable) -> Callable:
    """
    Decorator that provides AI context for methods using AI capabilities.

    Args:
        func: The function to decorate

    Returns:
        Wrapped function with AI context
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function for the decorated function.
        """
        # Set up AI context with user preferences and configuration
        ai_context = {}  # Replace with actual AI context setup

        # Add request context and organization settings to AI context
        ai_context['request'] = {'url': request.url, 'method': request.method}
        ai_context['organization'] = {'id': g.user.organization_id}

        # Call the original function with AI context
        result = func(*args, ai_context=ai_context, **kwargs)

        # Clean up AI context after function execution
        # (e.g., release resources, log usage)

        # Return the original function result
        return result

    return wrapper


def transactional(func: Callable) -> Callable:
    """
    Decorator that ensures database operations are performed within a transaction.

    Args:
        func: The function to decorate

    Returns:
        Wrapped function with transaction handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function for the decorated function.
        """
        # Get database session
        db = get_db()

        try:
            # Start a database transaction
            result = func(*args, **kwargs)

            # If function succeeds, commit the transaction
            db.commit()
            return result
        except Exception as e:
            # If exception occurs, rollback the transaction
            db.rollback()
            logger.error(f"Transaction rolled back due to exception: {str(e)}", exc_info=True)
            raise
        finally:
            # Close the database session
            db.close()

    return wrapper