"""
Utility module providing caching functionality for the Justice Bid application.

This module implements a flexible caching system with Redis as the backend storage,
supporting function result caching, key-based operations, and pattern-based cache
invalidation.
"""

import json
import pickle
import hashlib
import functools
from typing import Any, Callable, Dict, Tuple, Optional, Union
from datetime import datetime, timedelta

from utils.redis_client import get_redis_client
from utils.logging import get_logger

# Set up logger
logger = get_logger(__name__)

# Cache configuration
CACHE_ENABLED = True
DEFAULT_TTL = 3600  # Default TTL in seconds (1 hour)
SERIALIZATION_METHODS = {'json': 0, 'pickle': 1}


def generate_cache_key(prefix: str, args: tuple, kwargs: dict) -> str:
    """
    Generates a unique cache key based on function name and arguments.
    
    Args:
        prefix: String prefix for the key (usually function name)
        args: Function positional arguments
        kwargs: Function keyword arguments
        
    Returns:
        A unique cache key string
    """
    # Create a string representation of args and kwargs
    arg_string = str(args) + str(sorted(kwargs.items()))
    
    # Create an MD5 hash of the arguments
    arg_hash = hashlib.md5(arg_string.encode('utf-8')).hexdigest()
    
    # Combine prefix and hash to create the key
    return f"{prefix}:{arg_hash}"


def serialize_value(value: Any, method: int = SERIALIZATION_METHODS['json']) -> bytes:
    """
    Serializes a Python object for storage in Redis.
    
    Args:
        value: The Python object to serialize
        method: Serialization method (0=json, 1=pickle)
        
    Returns:
        Serialized value as bytes with method prefix
    """
    try:
        if method == SERIALIZATION_METHODS['json']:
            # Try JSON serialization first (more efficient, secure)
            serialized = json.dumps(value).encode('utf-8')
            return b'0:' + serialized
        else:
            # Use pickle if explicitly requested
            serialized = pickle.dumps(value)
            return b'1:' + serialized
    except (TypeError, ValueError):
        # Fall back to pickle if JSON serialization fails
        serialized = pickle.dumps(value)
        return b'1:' + serialized
    except Exception as e:
        logger.error(f"Serialization error: {str(e)}")
        raise


def deserialize_value(serialized_value: bytes) -> Any:
    """
    Deserializes a value retrieved from Redis.
    
    Args:
        serialized_value: The serialized value as bytes
        
    Returns:
        Deserialized Python object
    """
    try:
        # Extract serialization method from prefix
        method = int(serialized_value[:2].decode('utf-8')[0])
        value = serialized_value[2:]
        
        if method == SERIALIZATION_METHODS['json']:
            # JSON deserialization
            return json.loads(value.decode('utf-8'))
        else:
            # Pickle deserialization
            return pickle.loads(value)
    except Exception as e:
        logger.error(f"Deserialization error: {str(e)}")
        return None


def set_cache(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
    """
    Sets a value in the cache with the specified key and TTL.
    
    Args:
        key: The cache key
        value: The value to cache
        ttl: Time-to-live in seconds
        
    Returns:
        True if successful, False otherwise
    """
    if not CACHE_ENABLED:
        return False
    
    try:
        redis_client = get_redis_client()
        serialized_value = serialize_value(value)
        redis_client.setex(key, ttl, serialized_value)
        logger.debug(f"Cache set for key {key}, TTL: {ttl}s")
        return True
    except Exception as e:
        logger.error(f"Failed to set cache for key {key}: {str(e)}")
        return False


def get_cache(key: str) -> Any:
    """
    Retrieves a value from the cache by key.
    
    Args:
        key: The cache key
        
    Returns:
        The cached value or None if not found
    """
    if not CACHE_ENABLED:
        return None
    
    try:
        redis_client = get_redis_client()
        value = redis_client.get(key)
        
        if value:
            deserialized = deserialize_value(value)
            logger.debug(f"Cache hit for key {key}")
            return deserialized
        
        logger.debug(f"Cache miss for key {key}")
        return None
    except Exception as e:
        logger.error(f"Failed to get cache for key {key}: {str(e)}")
        return None


def delete_cache(key: str) -> bool:
    """
    Deletes a value from the cache by key.
    
    Args:
        key: The cache key
        
    Returns:
        True if the key was deleted, False otherwise
    """
    if not CACHE_ENABLED:
        return False
    
    try:
        redis_client = get_redis_client()
        result = redis_client.delete(key)
        success = bool(result)
        
        if success:
            logger.debug(f"Cache deleted for key {key}")
        else:
            logger.debug(f"Cache key {key} not found for deletion")
            
        return success
    except Exception as e:
        logger.error(f"Failed to delete cache for key {key}: {str(e)}")
        return False


def clear_cache_pattern(pattern: str) -> int:
    """
    Clears all cache entries matching a pattern.
    
    Args:
        pattern: Redis key pattern to match (e.g., "user:*")
        
    Returns:
        Number of keys deleted
    """
    if not CACHE_ENABLED:
        return 0
    
    try:
        redis_client = get_redis_client()
        keys = list(redis_client.scan_iter(match=pattern))
        
        if not keys:
            logger.debug(f"No keys found matching pattern {pattern}")
            return 0
        
        count = len(keys)
        if count > 0:
            redis_client.delete(*keys)
            logger.debug(f"Deleted {count} keys matching pattern {pattern}")
        
        return count
    except Exception as e:
        logger.error(f"Failed to clear cache for pattern {pattern}: {str(e)}")
        return 0


def cached(ttl: int = DEFAULT_TTL, key_prefix: str = None):
    """
    Decorator that caches the result of a function.
    
    Args:
        ttl: Time-to-live in seconds for cached results
        key_prefix: Prefix for cache keys (defaults to function name)
        
    Returns:
        Decorated function with caching behavior
    """
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if not CACHE_ENABLED:
                return func(*args, **kwargs)
            
            # Generate a cache key from the function name and arguments
            prefix = key_prefix or func.__name__
            cache_key = generate_cache_key(prefix, args, kwargs)
            
            # Try to get result from cache
            cached_result = get_cache(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for function {func.__name__}")
                return cached_result
            
            # If not in cache, execute the function
            logger.debug(f"Cache miss for function {func.__name__}")
            result = func(*args, **kwargs)
            
            # Cache the result
            set_cache(cache_key, result, ttl)
            
            return result
        return inner
    return wrapper


def invalidate_cached(key_prefix: str) -> int:
    """
    Invalidates cache entries for a specific function prefix.
    
    Args:
        key_prefix: Prefix for cache keys to invalidate
        
    Returns:
        Number of invalidated cache entries
    """
    pattern = f"{key_prefix}:*"
    return clear_cache_pattern(pattern)


class CacheManager:
    """
    Class that provides an object-oriented interface for cache operations.
    """
    
    def __init__(self):
        """Initialize the cache manager."""
        self._redis_client = None
        self._enabled = CACHE_ENABLED
    
    def _get_client(self):
        """Get or initialize the Redis client."""
        if self._redis_client is None:
            self._redis_client = get_redis_client()
        return self._redis_client
    
    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time-to-live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        return set_cache(key, value, ttl)
    
    def get(self, key: str) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found
        """
        return get_cache(key)
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if deleted, False otherwise
        """
        return delete_cache(key)
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all cache entries matching a pattern.
        
        Args:
            pattern: Redis key pattern to match (e.g., "user:*")
            
        Returns:
            Number of keys deleted
        """
        return clear_cache_pattern(pattern)