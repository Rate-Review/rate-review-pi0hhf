"""
Configuration module for the Justice Bid Rate Negotiation System backend application.

This module provides environment-specific configuration options, environment variable loading,
and configuration classes for different deployment environments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from ..utils.constants import JWT_EXPIRATION_MINUTES, REFRESH_TOKEN_EXPIRATION_DAYS

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def load_env_vars():
    """
    Loads environment variables from .env and .flaskenv files based on the current environment.
    """
    # Determine the current environment (development, testing, staging, production) from FLASK_ENV
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    # Construct path to the appropriate .env file
    env_file = BASE_DIR / f".env.{env}"
    
    # If environment-specific file doesn't exist, use default .env
    if not env_file.exists():
        env_file = BASE_DIR / ".env"
    
    # Load variables from the .env file using dotenv.load_dotenv
    if env_file.exists():
        load_dotenv(env_file)
    
    # Load variables from .flaskenv file if it exists
    flask_env = BASE_DIR / ".flaskenv"
    if flask_env.exists():
        load_dotenv(flask_env)
    
    # Set default values for critical environment variables if not set
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = os.urandom(24).hex()
    
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'


def get_env_var(key, default=None):
    """
    Retrieves an environment variable value with optional default.
    
    Args:
        key (str): The name of the environment variable
        default (any): Default value if the variable is not set
        
    Returns:
        any: The value of the environment variable or the default value
    """
    # Get the value of the environment variable using os.environ.get
    value = os.environ.get(key)
    
    # Return the value if it exists, otherwise return the default value
    if value is None:
        return default
    
    # Apply type conversion if necessary based on default value type
    if default is not None:
        if isinstance(default, bool):
            return value.lower() in ('true', 'yes', '1', 'y')
        elif isinstance(default, int):
            return int(value)
        elif isinstance(default, float):
            return float(value)
        elif isinstance(default, list):
            return value.split(',')
    
    return value


class Config:
    """Base configuration class with common settings for all environments."""
    
    def __init__(self):
        """Initializes the base configuration with default values."""
        # Set SECRET_KEY from environment or generate a secure default
        self.SECRET_KEY = get_env_var('SECRET_KEY', os.urandom(24).hex())
        
        # Configure database URIs from environment variables
        self.SQLALCHEMY_DATABASE_URI = get_env_var(
            'DATABASE_URL', 
            f"postgresql://postgres:postgres@localhost:5432/justicebid"
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        
        self.MONGODB_URI = get_env_var(
            'MONGODB_URI',
            "mongodb://localhost:27017/justicebid"
        )
        
        self.REDIS_URL = get_env_var('REDIS_URL', "redis://localhost:6379/0")
        
        # Set up JWT configuration using constants
        self.JWT_SECRET_KEY = get_env_var('JWT_SECRET_KEY', self.SECRET_KEY)
        self.JWT_ACCESS_TOKEN_EXPIRES = JWT_EXPIRATION_MINUTES * 60  # Convert to seconds
        self.JWT_REFRESH_TOKEN_EXPIRES = REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60  # Convert to seconds
        
        # Configure API keys for external services
        self.OPENAI_API_KEY = get_env_var('OPENAI_API_KEY')
        self.UNICOURT_API_KEY = get_env_var('UNICOURT_API_KEY')
        
        # Set up AWS credentials for S3 storage
        self.AWS_ACCESS_KEY_ID = get_env_var('AWS_ACCESS_KEY_ID')
        self.AWS_SECRET_ACCESS_KEY = get_env_var('AWS_SECRET_ACCESS_KEY')
        self.AWS_S3_BUCKET_NAME = get_env_var('AWS_S3_BUCKET_NAME', 'justicebid')
        
        # Configure logging and debugging settings
        self.DEBUG = False
        self.TESTING = False
        self.LOG_LEVEL = get_env_var('LOG_LEVEL', 'INFO')
        
        # Set up CORS settings for API access
        self.CORS_ORIGINS = get_env_var('CORS_ORIGINS', ['http://localhost:3000'])


class DevelopmentConfig(Config):
    """Configuration for development environment."""
    
    def __init__(self):
        """Initializes the development configuration."""
        # Call the parent class constructor
        super().__init__()
        # Enable DEBUG mode
        self.DEBUG = True
        # Set LOG_LEVEL to DEBUG
        self.LOG_LEVEL = 'DEBUG'
        # Enable SQL query logging with SQLALCHEMY_ECHO
        self.SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Configuration for testing environment."""
    
    def __init__(self):
        """Initializes the testing configuration."""
        # Call the parent class constructor
        super().__init__()
        # Enable TESTING mode
        self.TESTING = True
        # Configure SQLite in-memory database for testing
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        # Configure MongoDB test database
        self.MONGODB_URI = 'mongodb://localhost:27017/justicebid_test'
        # Disable CSRF protection
        self.WTF_CSRF_ENABLED = False


class StagingConfig(Config):
    """Configuration for staging environment."""
    
    def __init__(self):
        """Initializes the staging configuration."""
        # Call the parent class constructor
        super().__init__()
        # Disable DEBUG mode
        self.DEBUG = False
        # Set LOG_LEVEL to INFO
        self.LOG_LEVEL = 'INFO'


class ProductionConfig(Config):
    """Configuration for production environment."""
    
    def __init__(self):
        """Initializes the production configuration."""
        # Call the parent class constructor
        super().__init__()
        # Disable DEBUG mode
        self.DEBUG = False
        # Set LOG_LEVEL to WARNING
        self.LOG_LEVEL = 'WARNING'
        # Ensure all sensitive configuration comes from environment variables
        # Apply stricter security settings


class AppConfig:
    """Main application configuration class that selects the appropriate config based on environment."""
    
    def __init__(self, env=None):
        """
        Initializes the application configuration.
        
        Args:
            env (str): The environment name (development, testing, staging, production)
        """
        # Determine which configuration class to use based on env parameter
        if env is None:
            env = os.environ.get('FLASK_ENV', 'development').lower()
        
        # Initialize the selected configuration class
        self.config = self.get_config(env)
        
        # Load any additional config overrides from environment
    
    @staticmethod
    def get_config(env):
        """
        Factory method to get the appropriate configuration class based on environment.
        
        Args:
            env (str): The environment name
            
        Returns:
            object: Instance of the appropriate Config class
        """
        # Match env parameter to corresponding config class
        if env in ('development', 'dev'):
            return DevelopmentConfig()
        elif env in ('testing', 'test'):
            return TestingConfig()
        elif env == 'staging':
            return StagingConfig()
        elif env in ('production', 'prod'):
            return ProductionConfig()
        else:
            # Default to DevelopmentConfig if env is not recognized
            return DevelopmentConfig()