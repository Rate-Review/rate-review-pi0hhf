"""
JWT (JSON Web Token) authentication service for the Justice Bid Rate Negotiation System.

This module provides functionality for generating and validating access and refresh tokens,
handling token expiration, and verifying user identity. It supports the authentication
framework for API access and user sessions.
"""

import datetime
from datetime import timedelta
import uuid
from typing import Dict, Optional, Union

import jwt  # PyJWT 2.6.0
import redis  # redis 4.5.0

from ...utils.logging import get_logger
from ...utils.constants import (
    JWT_EXPIRATION_MINUTES,
    REFRESH_TOKEN_EXPIRATION_DAYS,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    UserRole
)
from ...api.core.config import get_config
from ...utils.security import secure_compare
from ...db.models.user import User

# Configure logger
logger = get_logger(__name__)

# Get application config
config = get_config()

# Setup Redis connection for token blacklist if not in testing mode
redis_client = redis.from_url(config.REDIS_URI) if not config.TESTING else None

# Prefix for token blacklist keys in Redis
TOKEN_BLACKLIST_PREFIX = 'token:blacklist:'


def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token for the specified user.
    
    Args:
        user: User object for whom to create token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT access token string
    """
    # Generate a unique token ID
    jti = str(uuid.uuid4())
    
    # Set expiration time
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    
    # Create token payload
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "org": str(user.organization_id),
        "role": user.role.value,
        "type": TOKEN_TYPE_ACCESS,
        "jti": jti,
        "exp": expire,
        "iat": datetime.datetime.utcnow()
    }
    
    # Encode token with the application secret key
    encoded_jwt = jwt.encode(
        payload, 
        config.SECRET_KEY, 
        algorithm=config.ALGORITHM
    )
    
    logger.debug(f"Created access token for user {user.id}")
    return encoded_jwt


def create_refresh_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT refresh token for the specified user.
    
    Args:
        user: User object for whom to create token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT refresh token string
    """
    # Generate a unique token ID
    jti = str(uuid.uuid4())
    
    # Set expiration time
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)
    
    # Create token payload
    # Refresh tokens contain minimal information for security
    payload = {
        "sub": str(user.id),
        "type": TOKEN_TYPE_REFRESH,
        "jti": jti,
        "exp": expire,
        "iat": datetime.datetime.utcnow()
    }
    
    # Encode token with the application secret key
    encoded_jwt = jwt.encode(
        payload, 
        config.SECRET_KEY, 
        algorithm=config.ALGORITHM
    )
    
    logger.debug(f"Created refresh token for user {user.id}")
    return encoded_jwt


def decode_token(token: str) -> Dict:
    """
    Decodes and validates a JWT token.
    
    Args:
        token: The JWT token to decode and validate
        
    Returns:
        Decoded token payload as dictionary
        
    Raises:
        jwt.PyJWTError: If token is invalid or expired
    """
    # Check if token is blacklisted
    if redis_client:
        try:
            # Get token ID without verification to check blacklist
            unverified_payload = jwt.decode(
                token, 
                options={"verify_signature": False}
            )
            jti = unverified_payload.get("jti")
            
            if jti and is_token_blacklisted(jti):
                logger.warning(f"Attempted to use blacklisted token (jti: {jti})")
                raise jwt.InvalidTokenError("Token has been blacklisted")
        except jwt.PyJWTError:
            # If we can't decode the token to check blacklist, continue to full verification
            # which will fail and raise the appropriate error
            pass
    
    # Verify and decode token
    payload = jwt.decode(
        token, 
        config.SECRET_KEY, 
        algorithms=[config.ALGORITHM]
    )
    
    logger.debug(f"Successfully decoded token (jti: {payload.get('jti', 'unknown')})")
    return payload


def validate_access_token(token: str) -> Dict:
    """
    Validates an access token and returns the user information.
    
    Args:
        token: Access token to validate
        
    Returns:
        Dictionary with user information
        
    Raises:
        jwt.PyJWTError: If token is invalid or expired
        ValueError: If token is not an access token
    """
    payload = decode_token(token)
    
    # Ensure it's an access token
    if payload.get("type") != TOKEN_TYPE_ACCESS:
        logger.warning("Attempted to use a non-access token as an access token")
        raise ValueError("Invalid token type")
    
    # Extract user information
    user_id = payload.get("sub")
    email = payload.get("email")
    organization_id = payload.get("org")
    role = payload.get("role")
    
    # Return user information
    return {
        "user_id": uuid.UUID(user_id),
        "email": email,
        "organization_id": uuid.UUID(organization_id),
        "role": role
    }


def validate_refresh_token(token: str) -> uuid.UUID:
    """
    Validates a refresh token and returns the user ID.
    
    Args:
        token: Refresh token to validate
        
    Returns:
        UUID of the user
        
    Raises:
        jwt.PyJWTError: If token is invalid or expired
        ValueError: If token is not a refresh token
    """
    payload = decode_token(token)
    
    # Ensure it's a refresh token
    if payload.get("type") != TOKEN_TYPE_REFRESH:
        logger.warning("Attempted to use a non-refresh token as a refresh token")
        raise ValueError("Invalid token type")
    
    # Extract and return user ID
    user_id = payload.get("sub")
    return uuid.UUID(user_id)


def blacklist_token(token: str, expires_in: Optional[int] = None) -> bool:
    """
    Adds a token to the blacklist to invalidate it.
    
    Args:
        token: Token to blacklist
        expires_in: Optional custom expiration time in seconds
        
    Returns:
        True if token was blacklisted successfully, False otherwise
    """
    if not redis_client:
        logger.warning("Redis client not available for token blacklisting")
        return False
    
    try:
        # Decode token without verification to get ID and expiration
        unverified_payload = jwt.decode(
            token, 
            options={"verify_signature": False}
        )
        
        jti = unverified_payload.get("jti")
        if not jti:
            logger.warning("Token does not contain a JTI claim")
            return False
        
        # Calculate TTL (time-to-live)
        if expires_in:
            ttl = expires_in
        else:
            exp = unverified_payload.get("exp")
            if exp:
                current_time = datetime.datetime.utcnow().timestamp()
                ttl = max(1, int(exp - current_time))  # Ensure at least 1 second
            else:
                # Default TTL if no expiration in token
                ttl = 3600  # 1 hour
        
        # Add to blacklist with TTL
        blacklist_key = f"{TOKEN_BLACKLIST_PREFIX}{jti}"
        redis_client.setex(blacklist_key, ttl, "1")
        
        logger.info(f"Token blacklisted (jti: {jti}) for {ttl} seconds")
        return True
    
    except Exception as e:
        logger.error(f"Error blacklisting token: {str(e)}")
        return False


def is_token_blacklisted(jti: str) -> bool:
    """
    Checks if a token is in the blacklist.
    
    Args:
        jti: JWT ID to check
        
    Returns:
        True if token is blacklisted, False otherwise
    """
    if not redis_client:
        return False
    
    blacklist_key = f"{TOKEN_BLACKLIST_PREFIX}{jti}"
    return bool(redis_client.exists(blacklist_key))


def get_token_from_auth_header(auth_header: str) -> Optional[str]:
    """
    Extracts the JWT token from the Authorization header.
    
    Args:
        auth_header: Authorization header string
        
    Returns:
        Extracted token or None if not found
    """
    if not auth_header:
        return None
    
    parts = auth_header.split()
    
    # Check header format
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


def refresh_tokens(refresh_token: str, user: User) -> Dict:
    """
    Creates new access and refresh tokens using a valid refresh token.
    
    Args:
        refresh_token: The refresh token to use
        user: User object to verify and create new tokens for
        
    Returns:
        Dictionary with new access and refresh tokens
        
    Raises:
        jwt.PyJWTError: If refresh token is invalid or expired
        ValueError: If token is not a refresh token or user ID doesn't match
    """
    # Validate the refresh token
    user_id = validate_refresh_token(refresh_token)
    
    # Verify the user ID matches
    if user_id != user.id:
        logger.warning(f"User ID mismatch in refresh token. Token: {user_id}, User: {user.id}")
        raise ValueError("User ID mismatch in refresh token")
    
    # Blacklist the old refresh token
    blacklist_token(refresh_token)
    
    # Generate new tokens
    new_access_token = create_access_token(user)
    new_refresh_token = create_refresh_token(user)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }