"""Initialization file for the API package that configures and exposes the Justice Bid Rate Negotiation API components."""
import logging  # Set up package-level logging

from flask import Flask  # flask==2.3+

from .routes.api_v1 import api_v1_router  # src/backend/api/routes/api_v1.py
from .core.errors import setup_error_handlers  # src/backend/api/core/errors.py
from .core.middleware import setup_middleware  # src/backend/api/core/middleware.py
from .core.config import API_PREFIX  # src/backend/api/core/config.py

logger = logging.getLogger(__name__)
__version__ = "1.0.0"


def setup_api(app: Flask) -> None:
    """Configures and initializes the Justice Bid API for the Flask application

    Args:
        app: Flask application instance

    Returns:
        None: Modifies the app in-place
    """
    # LD1: Register API v1 router with the Flask application
    app.register_blueprint(api_v1_router, url_prefix=API_PREFIX)

    # LD1: Set up error handlers for consistent error responses
    setup_error_handlers(app)

    # LD1: Configure middleware (CORS, request ID, security headers)
    setup_middleware(app)

    # LD1: Set up request logging and metrics collection
    # TODO: Implement request logging and metrics collection

    # LD1: Initialize API monitoring and instrumentation
    # TODO: Implement API monitoring and instrumentation
    logger.info("Justice Bid API initialized")