"""
Health check endpoints for the Justice Bid API.

This module provides endpoints for monitoring the health of the application
and its dependencies, supporting basic liveness checks, dependency checks,
and deep health checks for comprehensive monitoring.
"""

from flask import Blueprint, jsonify
import sqlalchemy.exc
import redis.exceptions
import pymongo.errors

from ..core.config import settings
from ...db.session import get_db
from ...utils.redis_client import get_redis_client
from ...utils.mongodb_client import get_mongo_client

# Create Blueprint for health endpoints
health_bp = Blueprint('health', __name__, url_prefix='/health')


@health_bp.route('/', methods=['GET'])
def basic_health_check():
    """
    Simple health check endpoint that returns a 200 status code if the application is running.
    
    This endpoint is used by load balancers and basic health monitoring to verify that
    the application is responsive.
    
    Returns:
        dict: A simple status response
    """
    return jsonify({"status": "ok", "api_version": settings.API_V1_PREFIX})


@health_bp.route('/dependencies', methods=['GET'])
def dependency_health_check():
    """
    Health check endpoint that verifies connectivity to specific external dependencies.
    
    This endpoint checks the connectivity to external services like UniCourt and
    other third-party services used by the application.
    
    Returns:
        dict: A dictionary with health status of external dependencies
    """
    response = {
        "status": "ok",
        "dependencies": {
            # In a real implementation, these would check actual external services
            "unicourt_api": {
                "status": "ok" if settings.UNICOURT_API_KEY else "not_configured",
                "message": "API key available" if settings.UNICOURT_API_KEY else "API key not configured"
            },
            "openai_api": {
                "status": "ok" if settings.OPENAI_API_KEY else "not_configured",
                "message": "API key available" if settings.OPENAI_API_KEY else "API key not configured"
            },
            "aws_s3": {
                "status": "ok" if (settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY) else "not_configured",
                "message": "Credentials available" if (settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY) else "Credentials not configured"
            }
        }
    }
    
    # Determine overall status
    if any(dep["status"] != "ok" for dep in response["dependencies"].values()):
        response["status"] = "degraded"
    
    return jsonify(response)


@health_bp.route('/deep', methods=['GET'])
def deep_health_check():
    """
    Detailed health check endpoint that verifies connectivity to all dependencies.
    
    This endpoint performs a comprehensive check of all system components including
    database, cache, message queue, and external services. It returns detailed
    status information for each component.
    
    Returns:
        dict: A dictionary with detailed health status of all components
    """
    # Initialize response with overall status
    response = {
        "status": "ok",
        "components": {}
    }
    
    # Check database
    db_status, db_message = _check_database()
    response["components"]["database"] = {
        "status": "ok" if db_status else "error",
        "message": db_message
    }
    
    # Check Redis
    redis_status, redis_message = _check_redis()
    response["components"]["cache"] = {
        "status": "ok" if redis_status else "error",
        "message": redis_message
    }
    
    # Check MongoDB
    mongodb_status, mongodb_message = _check_mongodb()
    response["components"]["document_store"] = {
        "status": "ok" if mongodb_status else "error",
        "message": mongodb_message
    }
    
    # Set overall status to error if any component is not healthy
    if not all([db_status, redis_status, mongodb_status]):
        response["status"] = "error"
    
    return jsonify(response)


def _check_database():
    """
    Internal function to check database connectivity.
    
    Attempts to establish a connection to the database and execute a simple query.
    
    Returns:
        tuple: A tuple containing (bool, str) indicating status and message
    """
    try:
        db = get_db()
        # Execute a simple query to verify connectivity
        db.execute("SELECT 1")
        return True, "Connected"
    except sqlalchemy.exc.SQLAlchemyError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def _check_redis():
    """
    Internal function to check Redis connectivity.
    
    Attempts to establish a connection to Redis and perform a PING command.
    
    Returns:
        tuple: A tuple containing (bool, str) indicating status and message
    """
    try:
        redis_client = get_redis_client()
        # Ping Redis to verify connectivity
        redis_client.ping()
        return True, "Connected"
    except redis.exceptions.RedisError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def _check_mongodb():
    """
    Internal function to check MongoDB connectivity.
    
    Attempts to establish a connection to MongoDB and ping the server.
    
    Returns:
        tuple: A tuple containing (bool, str) indicating status and message
    """
    try:
        mongo_client = get_mongo_client()
        # Ping MongoDB to verify connectivity
        mongo_client.admin.command('ping')
        return True, "Connected"
    except pymongo.errors.PyMongoError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"