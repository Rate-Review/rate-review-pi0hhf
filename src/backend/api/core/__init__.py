"""
Initializes the core API package providing essential functionality for API configuration, error handling, logging, security, authentication, and middleware.
Serves as the central point for importing core API components throughout the application.
"""

# Import Flask for setting up the API
import flask  # flask 2.3+

# Import internal modules for API configuration, error handling, logging, security, authentication, and middleware
from .config import API_CONFIG, ENV_CONFIG  # src/backend/api/core/config.py
from .errors import APIError, error_handler  # src/backend/api/core/errors.py
from .logging import logger  # src/backend/api/core/logging.py
from .security import require_auth, CSRFProtect  # src/backend/api/core/security.py
from .auth import jwt_manager, authenticate  # src/backend/api/core/auth.py
from .middleware import request_context, response_handler  # src/backend/api/core/middleware.py

# Define the API version
__version__ = "1.0.0"

# Export the configuration settings
__all__ = [
    "API_CONFIG",
    "ENV_CONFIG",
    "APIError",
    "error_handler",
    "logger",
    "require_auth",
    "CSRFProtect",
    "jwt_manager",
    "authenticate",
    "request_context",
    "response_handler",
]