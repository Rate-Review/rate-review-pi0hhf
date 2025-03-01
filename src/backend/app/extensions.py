"""
Extensions module.

This module initializes and configures Flask extensions for the Justice Bid application.
Extensions are created without binding them to a specific Flask app to avoid circular imports.
They are later initialized with the Flask app instance in the application factory.
"""

# Flask and extensions imports
from flask_sqlalchemy import SQLAlchemy  # v2.0+
from flask_migrate import Migrate  # v4.0+
from flask_restful import Api  # v0.3.10+
from flask_cors import CORS  # v3.0+
from flask_jwt_extended import JWTManager  # v4.4+
from flask_caching import Cache  # v2.0+
from flask_limiter import Limiter  # v3.0+
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow  # v0.14+
from celery import Celery  # v5.3+
from flask_pymongo import PyMongo  # v4.3+

# Local imports
from . import config  # Import configuration settings for extensions

# Create extension instances
db = SQLAlchemy()
migrate = Migrate()
api = Api()
cors = CORS()
jwt = JWTManager()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
ma = Marshmallow()
mongo = PyMongo()


def init_app(app):
    """
    Initialize extensions with the Flask application instance.
    
    Args:
        app: Flask application instance
    
    Returns:
        None
    """
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Migrate with app and SQLAlchemy instance
    migrate.init_app(app, db)
    
    # Initialize REST API
    api.init_app(app)
    
    # Initialize CORS
    cors.init_app(app)
    
    # Initialize JWT Manager
    jwt.init_app(app)
    
    # Initialize Cache with Redis
    cache_config = {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': app.config.get('REDIS_URL'),
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    cache.init_app(app, config=cache_config)
    
    # Initialize Rate Limiter
    limiter.init_app(app)
    
    # Initialize Marshmallow
    ma.init_app(app)
    
    # Initialize MongoDB client
    mongo.init_app(app)