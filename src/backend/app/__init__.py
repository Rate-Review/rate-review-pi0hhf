"""
Initialization file for the Flask application package.
Implements the application factory pattern to create and configure the Flask application instance for the Justice Bid Rate Negotiation System.
"""
# Third-party imports
from flask import Flask  # flask==2.3+
import os  # standard library
import logging  # standard library

# Internal imports
from .config import Config  # src/backend/app/config.py
from .extensions import db, migrate, cors, jwt, cache, init_app  # src/backend/app/extensions.py
from ..api.routes import api_v1  # src/backend/api/routes/api_v1.py
from ..api.core.errors import register_error_handlers  # src/backend/api/core/errors.py
from ..api.core.middleware import setup_middleware  # src/backend/api/core/middleware.py
from ..utils.logging import setup_logging  # src/backend/utils/logging.py

# Initialize logger
logger = logging.getLogger(__name__)


def create_app(config_name: str = None) -> Flask:
    """
    Application factory function that creates and configures a Flask application instance with the appropriate configuration, extensions, routes, error handlers, and middleware

    Args:
        config_name (str): Configuration name (dev, staging, production)

    Returns:
        Flask: Configured Flask application instance ready for serving API requests
    """
    # Initialize logging using setup_logging function
    setup_logging()

    # Create Flask application instance
    app = Flask(__name__)

    # Load configuration based on config_name parameter (dev, staging, production)
    config = Config()
    app.config.from_object(config)

    # Initialize Flask extensions (db, migrate, cors, jwt, cache) with the app
    init_app(app)

    # Register API routes from api_v1 module
    app.register_blueprint(api_v1.create_api_v1_router(), url_prefix='/api/v1')

    # Register error handlers using register_error_handlers function
    register_error_handlers(app)

    # Register middleware using register_middleware function
    setup_middleware(app)

    # Configure request logging
    @app.after_request
    def after_request(response):
        timestamp = '%Y-%m-%d %H:%M:%S'
        logger.info('%s %s %s %s %s %s',
                    request.remote_addr,
                    datetime.datetime.now().strftime(timestamp),
                    request.method,
                    request.path,
                    response.status,
                    response.data)
        return response

    # Return the fully configured application instance
    return app