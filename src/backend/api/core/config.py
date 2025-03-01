"""
Core configuration module for the Justice Bid backend API.

This module defines configuration settings for different environments,
loads environment variables, and provides access to configuration values
throughout the application.
"""

import os
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv
from pydantic import BaseSettings

from ...utils.constants import (
    JWT_EXPIRATION_MINUTES,
    REFRESH_TOKEN_EXPIRATION_DAYS,
    API_VERSION,
)

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_env_variable(key: str, default: Any = None) -> Any:
    """
    Retrieves an environment variable with a fallback default value.
    
    Args:
        key: The name of the environment variable
        default: The default value to return if the environment variable is not set
        
    Returns:
        The value of the environment variable or the default value
    """
    return os.environ.get(key, default)


def load_env_file() -> None:
    """
    Loads environment variables from a .env file based on the current environment.
    """
    env = get_env_variable("FLASK_ENV", "development")
    env_file = os.path.join(BASE_DIR, f".env.{env}")
    
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        # Fall back to the default .env file
        default_env_file = os.path.join(BASE_DIR, ".env")
        if os.path.exists(default_env_file):
            load_dotenv(default_env_file)


class BaseConfig:
    """Base configuration class with common settings for all environments."""
    
    API_V1_PREFIX: str = f"/api/{API_VERSION}"
    PROJECT_NAME: str = "Justice Bid Rate Negotiation System"
    DEBUG: bool = False
    SECRET_KEY: str = get_env_variable("SECRET_KEY", "dev-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = get_env_variable("ACCESS_TOKEN_EXPIRE_MINUTES", JWT_EXPIRATION_MINUTES)
    REFRESH_TOKEN_EXPIRE_DAYS: int = get_env_variable("REFRESH_TOKEN_EXPIRE_DAYS", REFRESH_TOKEN_EXPIRATION_DAYS)
    ALGORITHM: str = get_env_variable("ALGORITHM", "HS256")
    SQLALCHEMY_DATABASE_URI: str = get_env_variable(
        "SQLALCHEMY_DATABASE_URI", 
        "postgresql://postgres:postgres@localhost:5432/justice_bid"
    )
    MONGODB_URI: str = get_env_variable(
        "MONGODB_URI", 
        "mongodb://localhost:27017/justice_bid"
    )
    REDIS_URI: str = get_env_variable(
        "REDIS_URI", 
        "redis://localhost:6379/0"
    )
    ALLOWED_HOSTS: List[str] = get_env_variable("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS: List[str] = get_env_variable("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    AWS_ACCESS_KEY_ID: str = get_env_variable("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = get_env_variable("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET_NAME: str = get_env_variable("AWS_S3_BUCKET_NAME", "justice-bid")
    UNICOURT_API_KEY: str = get_env_variable("UNICOURT_API_KEY", "")
    OPENAI_API_KEY: str = get_env_variable("OPENAI_API_KEY", "")
    RATE_LIMIT_DEFAULT: int = get_env_variable("RATE_LIMIT_DEFAULT", 100)
    RATE_LIMIT_PER_API: Dict[str, int] = {
        "standard": get_env_variable("RATE_LIMIT_STANDARD", 100),
        "bulk": get_env_variable("RATE_LIMIT_BULK", 20),
        "analytics": get_env_variable("RATE_LIMIT_ANALYTICS", 30),
        "critical": get_env_variable("RATE_LIMIT_CRITICAL", 50),
    }
    LOG_LEVEL: str = get_env_variable("LOG_LEVEL", "INFO")
    
    def __init__(self):
        """Initializes the BaseConfig with default values."""
        # Initialize any values that need computation or complex logic here
        pass


class DevelopmentConfig(BaseConfig):
    """Configuration settings specific to the development environment."""
    
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    def __init__(self):
        """Initializes the DevelopmentConfig with development-specific settings."""
        super().__init__()
        # Override any settings specific to development environment here


class TestingConfig(BaseConfig):
    """Configuration settings specific to the testing environment."""
    
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = get_env_variable(
        "TEST_SQLALCHEMY_DATABASE_URI", 
        "postgresql://postgres:postgres@localhost:5432/justice_bid_test"
    )
    MONGODB_URI: str = get_env_variable(
        "TEST_MONGODB_URI", 
        "mongodb://localhost:27017/justice_bid_test"
    )
    
    def __init__(self):
        """Initializes the TestingConfig with testing-specific settings."""
        super().__init__()
        # Override any settings specific to testing environment here
        # Use in-memory databases or test-specific endpoints


class StagingConfig(BaseConfig):
    """Configuration settings specific to the staging environment."""
    
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    def __init__(self):
        """Initializes the StagingConfig with staging-specific settings."""
        super().__init__()
        # Override any settings specific to staging environment here


class ProductionConfig(BaseConfig):
    """Configuration settings specific to the production environment."""
    
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    PRODUCTION: bool = True
    
    def __init__(self):
        """Initializes the ProductionConfig with production-specific settings."""
        super().__init__()
        # Override any settings specific to production environment here


class Settings(BaseSettings):
    """Pydantic settings class for validating and accessing configuration values."""
    
    API_V1_PREFIX: str
    PROJECT_NAME: str
    DEBUG: bool
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM: str
    SQLALCHEMY_DATABASE_URI: str
    MONGODB_URI: str
    REDIS_URI: str
    ALLOWED_HOSTS: List[str]
    CORS_ORIGINS: List[str]
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str
    UNICOURT_API_KEY: str
    OPENAI_API_KEY: str
    RATE_LIMIT_DEFAULT: int
    RATE_LIMIT_PER_API: Dict[str, int]
    LOG_LEVEL: str
    
    class Config:
        env_file = ".env"
        
    def __init__(self, **data):
        """Initializes the Settings class based on the current environment."""
        config = self.get_config()
        for key, value in vars(config).items():
            if not key.startswith("__") and not callable(value):
                data.setdefault(key, value)
        super().__init__(**data)
    
    @staticmethod
    def get_config():
        """
        Returns the appropriate config class based on the current environment.
        
        Returns:
            Configuration class instance
        """
        env = get_env_variable("FLASK_ENV", "development").lower()
        
        if env == "production":
            return ProductionConfig()
        elif env == "staging":
            return StagingConfig()
        elif env == "testing":
            return TestingConfig()
        else:  # Default to development
            return DevelopmentConfig()


# Load environment variables
load_env_file()

# Create settings instance
settings = Settings()