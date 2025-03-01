import os  # standard library
import logging # standard library
from typing import Dict, Any # standard library

from flask import Flask # flask==2.3+

from .app.app import create_app # src/backend/app/app.py
from .config import get_settings, ENV_DEVELOPMENT, ENV_TESTING, ENV_STAGING, ENV_PRODUCTION, configure_logging # src/backend/config.py

logger = logging.getLogger(__name__)

def get_application(env_name: str = None) -> Flask:
    """Factory function that creates a configured Flask application instance"""
    # LD1: Determine the environment from parameter or environment variable
    if env_name is None:
        env_name = get_env()

    # LD1: Retrieve configuration settings for the environment
    settings = get_settings(env_name)

    # LD1: Configure application logging based on environment
    configure_logging(settings)

    # LD1: Create and configure the Flask application
    app = create_app(env_name)

    # LD1: Return the configured application instance
    return app

def get_env() -> str:
    """Retrieves the current environment name from environment variables or uses development as default"""
    # LD1: Check for FLASK_ENV environment variable
    env = os.environ.get('FLASK_ENV')

    # LD1: Check for APP_ENV environment variable if FLASK_ENV is not set
    if not env:
        env = os.environ.get('APP_ENV')

    # LD1: Map environment variable to predefined environment constants
    if env:
        env = env.lower()
        if env == 'development':
            env_name = ENV_DEVELOPMENT
        elif env == 'testing':
            env_name = ENV_TESTING
        elif env == 'staging':
            env_name = ENV_STAGING
        elif env == 'production':
            env_name = ENV_PRODUCTION
        else:
            env_name = ENV_DEVELOPMENT
    else:
        # LD1: Default to development environment if not specified
        env_name = ENV_DEVELOPMENT

    # LD1: Return the environment name
    return env_name

def create_dev_app() -> Flask:
    """Creates a Flask application configured for development use"""
    # LD1: Call get_application with development environment
    app = get_application(ENV_DEVELOPMENT)

    # LD1: Return the configured development application
    return app

# Create a pre-configured Flask application instance for development server
app = create_dev_app()

if __name__ == "__main__":
    # Run the Flask application in debug mode
    app.run(debug=True)