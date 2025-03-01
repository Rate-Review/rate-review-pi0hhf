"""
Redis client utility for connecting to Redis and providing common Redis operations.

This module provides a client for interacting with Redis cache, supporting operations
like getting and setting values, working with hashes, publishing messages, and more.
It implements the caching strategy for the Justice Bid Rate Negotiation System.
"""

import logging
import redis
from typing import Any, Optional, Dict
from redis import Redis, ConnectionPool
from urllib.parse import urlparse

from ..app.config import AppConfig

# Set up logger
logger = logging.getLogger(__name__)

def get_redis_config() -> Dict:
    """
    Get Redis configuration from application config.
    
    Returns:
        Dict: Redis configuration parameters
    """
    # Get AppConfig instance with current environment
    app_config = AppConfig()
    
    # Get Redis URL from config
    redis_url = app_config.config.REDIS_URL
    
    # Parse Redis URL
    parsed_url = urlparse(redis_url)
    
    # Extract parameters from URL
    host = parsed_url.hostname or 'localhost'
    port = parsed_url.port or 6379
    
    # Extract DB number from path
    path = parsed_url.path
    db = 0
    if path and path != '/':
        try:
            db = int(path.lstrip('/'))
        except ValueError:
            logger.warning(f"Invalid DB number in Redis URL: {path}")
    
    # Extract password
    password = parsed_url.password
    
    # Return Redis config as a dictionary
    return {
        'host': host,
        'port': port,
        'db': db,
        'password': password,
        'decode_responses': True,
        'socket_timeout': 5,
        'socket_connect_timeout': 5,
        'max_connections': 10
    }

def get_redis_connection_pool() -> ConnectionPool:
    """
    Creates and returns a Redis connection pool for efficient connection management.
    
    Returns:
        ConnectionPool: Redis connection pool
    """
    try:
        # Get Redis configuration
        redis_config = get_redis_config()
        
        # Create connection pool
        pool = redis.ConnectionPool(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            db=redis_config.get('db', 0),
            password=redis_config.get('password'),
            decode_responses=redis_config.get('decode_responses', True),
            socket_timeout=redis_config.get('socket_timeout', 5),
            socket_connect_timeout=redis_config.get('socket_connect_timeout', 5),
            max_connections=redis_config.get('max_connections', 10)
        )
        
        return pool
    except Exception as e:
        logger.error(f"Failed to create Redis connection pool: {str(e)}")
        raise

def get_redis_client() -> Redis:
    """
    Factory function to get a Redis client instance with the configured connection.
    
    Returns:
        Redis: Configured Redis client instance
    """
    try:
        # Get the connection pool
        pool = get_redis_connection_pool()
        
        # Create Redis client with the connection pool
        client = redis.Redis(connection_pool=pool)
        
        # Test the connection
        client.ping()
        
        return client
    except Exception as e:
        logger.error(f"Failed to create Redis client: {str(e)}")
        raise

class RedisClient:
    """
    Client class for interacting with Redis cache, providing methods for common Redis operations.
    """
    
    def __init__(self, connection_pool: Optional[ConnectionPool] = None):
        """
        Initialize a Redis client with connection pool.
        
        Args:
            connection_pool (ConnectionPool, optional): Redis connection pool.
                If not provided, a new one will be created.
        """
        self._connected = False
        
        try:
            # Use provided connection pool or create a new one
            if connection_pool is None:
                connection_pool = get_redis_connection_pool()
            
            # Set up Redis client with the connection pool
            self._client = redis.Redis(connection_pool=connection_pool)
            
            # Test connection
            self._client.ping()
            self._connected = True
            logger.debug("Redis client successfully connected")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {str(e)}")
            self._connected = False
    
    def get(self, key: str) -> Any:
        """
        Get a value from Redis by key.
        
        Args:
            key (str): The key to retrieve
            
        Returns:
            Any: Value from Redis or None if key doesn't exist
        """
        try:
            return self._client.get(key)
        except Exception as e:
            logger.error(f"Redis get error for key '{key}': {str(e)}")
            return None
    
    def set(self, key: str, value: Any, expiration_seconds: int = None) -> bool:
        """
        Set a key-value pair in Redis with optional expiration time.
        
        Args:
            key (str): The key to set
            value (Any): The value to store
            expiration_seconds (int, optional): Time in seconds before the key expires
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if expiration_seconds:
                return self._client.setex(key, expiration_seconds, value)
            else:
                return self._client.set(key, value)
        except Exception as e:
            logger.error(f"Redis set error for key '{key}': {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        
        Args:
            key (str): The key to delete
            
        Returns:
            bool: True if key was deleted, False otherwise
        """
        try:
            return bool(self._client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error for key '{key}': {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Args:
            key (str): The key to check
            
        Returns:
            bool: True if key exists, False otherwise
        """
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error for key '{key}': {str(e)}")
            return False
    
    def expire(self, key: str, expiration_seconds: int) -> bool:
        """
        Set expiration time for a key.
        
        Args:
            key (str): The key to set expiration for
            expiration_seconds (int): Time in seconds before the key expires
            
        Returns:
            bool: True if expiration was set, False otherwise
        """
        try:
            return bool(self._client.expire(key, expiration_seconds))
        except Exception as e:
            logger.error(f"Redis expire error for key '{key}': {str(e)}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a key's integer value.
        
        Args:
            key (str): The key to increment
            amount (int, optional): Amount to increment by, defaults to 1
            
        Returns:
            int: New value after increment or None if error
        """
        try:
            return self._client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis increment error for key '{key}': {str(e)}")
            return None
    
    def hget(self, hash_key: str, field: str) -> Any:
        """
        Get a value from a Redis hash.
        
        Args:
            hash_key (str): The hash key
            field (str): The field within the hash
            
        Returns:
            Any: Value from hash or None if not found
        """
        try:
            return self._client.hget(hash_key, field)
        except Exception as e:
            logger.error(f"Redis hget error for hash '{hash_key}', field '{field}': {str(e)}")
            return None
    
    def hset(self, hash_key: str, field: str, value: Any) -> bool:
        """
        Set a field-value pair in a Redis hash.
        
        Args:
            hash_key (str): The hash key
            field (str): The field within the hash
            value (Any): The value to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert return value (integer) to boolean
            return bool(self._client.hset(hash_key, field, value))
        except Exception as e:
            logger.error(f"Redis hset error for hash '{hash_key}', field '{field}': {str(e)}")
            return False
    
    def publish(self, channel: str, message: str) -> int:
        """
        Publish a message to a Redis channel.
        
        Args:
            channel (str): The channel to publish to
            message (str): The message to publish
            
        Returns:
            int: Number of clients that received the message
        """
        try:
            return self._client.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis publish error for channel '{channel}': {str(e)}")
            return 0
    
    def flush_db(self) -> bool:
        """
        Clear all keys from the current database (use with caution).
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis flush_db error: {str(e)}")
            return False