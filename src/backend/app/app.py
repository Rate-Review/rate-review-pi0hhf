"""
Initializes and configures the Flask application for the Justice Bid Rate Negotiation System.
This file serves as the application factory, creating properly configured Flask instances based on the environment,
registering extensions, blueprints, middleware, and error handlers.
"""
import os  # standard library
import logging # standard library
import json # standard library

from flask import Flask, jsonify # flask==2.3+

from .config import AppConfig # src/backend/app/config.py
from .extensions import init_app # src/backend/app/extensions.py
from ..api.routes.api_v1 import api_v1_bp # src/backend/api/routes/api_v1.py
from ..api.routes.graphql import graphql_blueprint # src/backend/api/routes/graphql.py
from ..api.core.middleware import setup_middleware # src/backend/api/core/middleware.py
from ..api/core/errors import register_error_handlers # src/backend/api/core/errors.py
from ..api/core/logging import setup_api_logging # src/backend/api/core/logging.py
from ..api/core/security import setup_security # src/backend/api/core/security.py
from ..api/core/auth import setup_auth # src/backend/api/core/auth.py
from ..db.session import initialize_db # src/backend/db/session.py

logger = logging.getLogger(__name__)

def create_app(env_name: str = None, config_override: dict = None) -> Flask:
    """
    Factory function that creates and configures a Flask application instance based on provided
    configuration or environment variables.
    
    Args:
        env_name: The environment name (development, testing, staging, production)
        config_override: A dictionary of configuration overrides
        
    Returns:
        Configured Flask application instance
    """
    # LD1: Create a new Flask application instance
    app = Flask(__name__)

    # LD1: Load configuration from config.py based on environment name
    app_config = AppConfig(env=env_name)
    app.config.from_object(app_config.config)

    # LD1: Apply any configuration overrides passed to the function
    if config_override:
        app.config.update(config_override)

    # LD1: Set up API logging for the application
    setup_api_logging(app)

    # LD1: Initialize database connection
    initialize_db()

    # LD1: Initialize Flask extensions (SQLAlchemy, Redis, CORS, etc.)
    init_app(app)

    # LD1: Set up security features (CORS, CSP, etc.)
    setup_security(app)

    # LD1: Set up authentication mechanisms
    setup_auth(app)

    # LD1: Register error handlers
    register_error_handlers(app)

    # LD1: Set up middleware for request/response processing
    setup_middleware(app)

    # LD1: Register API v1 blueprint with URL prefix /api/v1
    register_blueprints(app)

    # LD1: Register health check endpoint
    register_health_check(app)

    # LD1: Return the configured Flask application
    return app

def register_blueprints(app: Flask) -> None:
    """
    Registers all API blueprints with the Flask application
    
    Args:
        app: Flask application instance
        
    Returns:
        No return value
    """
    # LD1: Register the API v1 blueprint with URL prefix /api/v1
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    # LD1: Register the GraphQL blueprint if enabled in configuration
    if app.config.get('GRAPHQL_ENABLED', False):
        app.register_blueprint(graphql_blueprint)

    # LD1: Log the registration of each blueprint
    logger.info("Registered API blueprints")

def register_health_check(app: Flask) -> None:
    """
    Registers a basic health check endpoint for monitoring
    
    Args:
        app: Flask application instance
        
    Returns:
        No return value
    """
    # LD1: Create a simple /health endpoint that returns status: ok and environment information
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok', 'environment': app.config['FLASK_ENV']})

    # LD1: Ensure the endpoint doesn't require authentication

    # LD1: Include basic database connectivity check

    # LD1: Include Redis connectivity check if configured

    # LD1: Log the registration of the health check endpoint
    logger.info("Registered health check endpoint")