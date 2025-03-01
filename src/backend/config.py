"""
Configuration module for the Justice Bid Rate Negotiation System.

This module centralizes environment-specific configurations, manages environment 
variables, and provides access to configuration throughout the application.
It serves as the main entry point for all configuration needs of the backend system.
"""

import os
import pathlib
from dotenv import load_dotenv
from typing import Any, Type

from utils.constants import JWT_EXPIRATION_MINUTES, REFRESH_TOKEN_EXPIRATION_DAYS
from utils.logging import setup_logging

# Define base directory and environment constants
BASE_DIR = pathlib.Path(__file__).resolve().parent
ENV_DEVELOPMENT = 'development'
ENV_TESTING = 'testing'
ENV_STAGING = 'staging'
ENV_PRODUCTION = 'production'
DEFAULT_ENV = ENV_DEVELOPMENT


def load_env_file(env: str) -> None:
    """
    Loads environment variables from a .env file based on the current environment.
    
    Args:
        env (str): Current environment name (development, testing, staging, production)
    """
    env_file = BASE_DIR / f".env.{env}"
    default_env_file = BASE_DIR / ".env"
    flask_env_file = BASE_DIR / ".flaskenv"
    
    # Try environment-specific file first, then default .env file
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        print(f"Loaded environment variables from {env_file}")
    elif default_env_file.exists():
        load_dotenv(dotenv_path=default_env_file)
        print(f"Loaded environment variables from {default_env_file}")
    else:
        print(f"No environment file found at {env_file} or {default_env_file}")
    
    # Load Flask-specific variables if available
    if flask_env_file.exists():
        load_dotenv(dotenv_path=flask_env_file)
        print(f"Loaded Flask environment variables from {flask_env_file}")


def get_env_variable(key: str, default: Any = None, type_conversion: Type = None) -> Any:
    """
    Retrieves an environment variable value with optional type conversion and default value.
    
    Args:
        key (str): Environment variable name
        default (Any): Default value if environment variable is not set
        type_conversion (Type): Optional type to convert the value to
        
    Returns:
        The value of the environment variable or the default value
    """
    value = os.environ.get(key)
    
    if value is None:
        return default
    
    if type_conversion is not None:
        try:
            # Handle boolean conversion specially
            if type_conversion is bool:
                return value.lower() in ('true', 'yes', '1', 't', 'y')
            
            # Handle list conversion
            if type_conversion is list:
                return value.split(',') if value else []
            
            # Standard type conversion
            return type_conversion(value)
        except (ValueError, TypeError) as e:
            print(f"Warning: Failed to convert {key}={value} to {type_conversion.__name__}, using default {default}. Error: {str(e)}")
            return default
    
    return value


class BaseConfig:
    """Base configuration class with common settings for all environments."""
    
    def __init__(self):
        # Basic application settings
        self.SECRET_KEY = get_env_variable('SECRET_KEY', os.urandom(32).hex())
        self.PROJECT_NAME = get_env_variable('PROJECT_NAME', 'Justice Bid Rate Negotiation System')
        self.API_V1_PREFIX = get_env_variable('API_V1_PREFIX', '/api/v1')
        
        # Database URIs
        self.SQLALCHEMY_DATABASE_URI = get_env_variable('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/justicebid')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.MONGODB_URI = get_env_variable('MONGODB_URI', 'mongodb://localhost:27017/justicebid')
        self.REDIS_URL = get_env_variable('REDIS_URL', 'redis://localhost:6379/0')
        
        # JWT Configuration
        self.JWT_SECRET_KEY = get_env_variable('JWT_SECRET_KEY', self.SECRET_KEY)
        self.JWT_ACCESS_TOKEN_EXPIRES = get_env_variable('JWT_ACCESS_TOKEN_EXPIRES', 
                                                         JWT_EXPIRATION_MINUTES * 60, 
                                                         int)
        self.JWT_REFRESH_TOKEN_EXPIRES = get_env_variable('JWT_REFRESH_TOKEN_EXPIRES', 
                                                          REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60, 
                                                          int)
        
        # External API Keys
        self.OPENAI_API_KEY = get_env_variable('OPENAI_API_KEY', '')
        self.UNICOURT_API_KEY = get_env_variable('UNICOURT_API_KEY', '')
        
        # AWS Configuration
        self.AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID', '')
        self.AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY', '')
        self.AWS_S3_BUCKET_NAME = get_env_variable('AWS_S3_BUCKET_NAME', 'justicebid')
        self.AWS_REGION = get_env_variable('AWS_REGION', 'us-east-1')
        
        # Logging and debugging
        self.DEBUG = get_env_variable('DEBUG', False, bool)
        self.TESTING = get_env_variable('TESTING', False, bool)
        self.LOG_LEVEL = get_env_variable('LOG_LEVEL', 'INFO')
        self.USE_JSON_LOGGING = get_env_variable('USE_JSON_LOGGING', True, bool)
        
        # CORS Configuration
        self.CORS_ORIGINS = get_env_variable('CORS_ORIGINS', '*', list)


class DevelopmentConfig(BaseConfig):
    """Configuration for development environment."""
    
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.LOG_LEVEL = 'DEBUG'
        self.SQLALCHEMY_ECHO = True
        self.USE_JSON_LOGGING = False
        
        # Override database URLs if not specified in environment
        if 'DATABASE_URL' not in os.environ:
            self.SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/justicebid_dev'
        if 'MONGODB_URI' not in os.environ:
            self.MONGODB_URI = 'mongodb://localhost:27017/justicebid_dev'
        if 'REDIS_URL' not in os.environ:
            self.REDIS_URL = 'redis://localhost:6379/0'


class TestingConfig(BaseConfig):
    """Configuration for testing environment."""
    
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = True
        self.LOG_LEVEL = 'DEBUG'
        
        # Use in-memory SQLite for testing
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        self.MONGODB_URI = 'mongodb://localhost:27017/justicebid_test'
        self.REDIS_URL = 'redis://localhost:6379/1'
        
        # Disable CSRF for testing
        self.WTF_CSRF_ENABLED = False
        
        # Disable JSON logging for readable test outputs
        self.USE_JSON_LOGGING = False


class StagingConfig(BaseConfig):
    """Configuration for staging environment."""
    
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.LOG_LEVEL = 'INFO'
        self.USE_JSON_LOGGING = True
        
        # Ensure all DB URLs and API keys come from environment variables
        if not all([
            os.environ.get('DATABASE_URL'),
            os.environ.get('MONGODB_URI'),
            os.environ.get('REDIS_URL')
        ]):
            print("Warning: Database URLs should be provided via environment variables in staging")


class ProductionConfig(BaseConfig):
    """Configuration for production environment."""
    
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.LOG_LEVEL = 'WARNING'
        self.USE_JSON_LOGGING = True
        
        # Verify required configuration
        required_vars = [
            'SECRET_KEY',
            'DATABASE_URL',
            'MONGODB_URI',
            'REDIS_URL',
            'JWT_SECRET_KEY',
            'OPENAI_API_KEY',
            'UNICOURT_API_KEY',
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            missing_vars_str = ', '.join(missing_vars)
            print(f"Warning: Missing required environment variables for production: {missing_vars_str}")
        
        # Additional security settings for production
        self.SESSION_COOKIE_SECURE = True
        self.SESSION_COOKIE_HTTPONLY = True
        self.REMEMBER_COOKIE_SECURE = True
        self.REMEMBER_COOKIE_HTTPONLY = True


def get_settings(env: str = None) -> BaseConfig:
    """
    Factory function that returns the appropriate configuration settings based on environment.
    
    Args:
        env (str): Environment name (development, testing, staging, production)
        
    Returns:
        Configuration settings object for the specified environment
    """
    # Determine environment from parameter or environment variable
    if env is None:
        env = os.environ.get('FLASK_ENV', os.environ.get('APP_ENV', DEFAULT_ENV))
    
    # Load environment variables for the specified environment
    load_env_file(env)
    
    # Map environment names to config classes
    env_config_map = {
        ENV_DEVELOPMENT: DevelopmentConfig,
        'dev': DevelopmentConfig,
        ENV_TESTING: TestingConfig,
        'test': TestingConfig,
        ENV_STAGING: StagingConfig,
        ENV_PRODUCTION: ProductionConfig,
        'prod': ProductionConfig
    }
    
    # Get the appropriate config class or default to development
    config_class = env_config_map.get(env.lower(), DevelopmentConfig)
    
    print(f"Using {config_class.__name__} for environment: {env}")
    
    # Create and return an instance of the config class
    return config_class()


def configure_logging(config: BaseConfig) -> None:
    """
    Configures application logging based on environment settings.
    
    Args:
        config (BaseConfig): Configuration object with logging settings
    """
    log_level = config.LOG_LEVEL
    use_json = config.USE_JSON_LOGGING
    
    # Determine log file path if log to file is enabled
    log_file = get_env_variable('LOG_FILE', None)
    
    # Configure logging
    setup_logging(
        log_level=log_level,
        json_format=use_json,
        log_file=log_file
    )
    
    # Log that logging has been configured
    import logging
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured successfully",
        extra={
            "additional_data": {
                "level": log_level,
                "json_format": use_json,
                "log_file": log_file
            }
        }
    )


# Initialize settings for the current environment
settings = get_settings()

# Configure logging using the settings
configure_logging(settings)