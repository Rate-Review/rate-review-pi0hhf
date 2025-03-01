"""
Core security utilities for the Justice Bid Rate Negotiation System.

This module provides a comprehensive set of security functions for authentication,
authorization, data protection, and secure communication. These utilities implement
industry-standard security practices and are used throughout the application.
"""

import os
import hashlib
import hmac
import base64
import secrets
import uuid
import re
import datetime
import typing
from typing import Optional, Union, Tuple, Dict, Any
import json

import bcrypt  # version 3.2.0
import bleach  # version 4.1.0

from ..utils.constants import TOKEN_EXPIRY_MINUTES, REFRESH_TOKEN_EXPIRY_DAYS, UserRole
from ..utils.logging import get_logger

# Configure logger
logger = get_logger(__name__)

# Security configuration
SECURITY_SALT = os.getenv('SECURITY_SALT', os.urandom(32))
PASSWORD_HASH_ROUNDS = 12
PASSWORD_MIN_LENGTH = 12
PASSWORD_COMPLEXITY_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'
CSRF_TOKEN_BYTES = 32
TOKEN_ALGORITHM = "HS256"

# Security headers to be applied to all responses
SECURE_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Cache-Control': 'no-store',
    'Pragma': 'no-cache'
}


def hash_password(password: str) -> str:
    """
    Securely hash a password using bcrypt with appropriate work factor.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password as a string
    """
    # Convert password to bytes if it's a string
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt(rounds=PASSWORD_HASH_ROUNDS)
    hashed = bcrypt.hashpw(password, salt)
    
    # Return the hashed password as a string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        True if the password matches, False otherwise
    """
    # Convert inputs to bytes if they're strings
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    # Use bcrypt to verify the password
    try:
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate that a password meets security requirements.
    
    Password must:
    - Be at least PASSWORD_MIN_LENGTH characters long
    - Contain at least one uppercase letter, one lowercase letter, 
      one number, and one special character
    
    Args:
        password: The password to validate
        
    Returns:
        A tuple of (success, error_message)
    """
    # Check length
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
    
    # Check complexity using regex pattern
    if not re.search(PASSWORD_COMPLEXITY_PATTERN, password):
        return (False, "Password must contain at least one uppercase letter, "
                "one lowercase letter, one number, and one special character")
    
    # All checks passed
    return True, ""


def generate_token(bytes_length: int = 32) -> str:
    """
    Generate a secure random token for various security purposes.
    
    Args:
        bytes_length: Length of the random token in bytes
        
    Returns:
        Base64 encoded token string
    """
    # Generate secure random bytes
    token_bytes = secrets.token_bytes(bytes_length)
    
    # Encode as base64 and remove padding
    token = base64.urlsafe_b64encode(token_bytes).decode('utf-8').rstrip('=')
    
    return token


def generate_csrf_token() -> str:
    """
    Generate a CSRF token for form protection.
    
    Returns:
        Base64 encoded CSRF token
    """
    return generate_token(CSRF_TOKEN_BYTES)


def verify_csrf_token(request_token: str, expected_token: str) -> bool:
    """
    Verify a CSRF token against the expected token.
    
    Args:
        request_token: Token provided in the request
        expected_token: Expected token value from session
        
    Returns:
        True if tokens match, False otherwise
    """
    return secure_compare(request_token, expected_token)


def secure_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings match, False otherwise
    """
    # Convert inputs to bytes if they're strings
    if isinstance(a, str):
        a = a.encode('utf-8')
    if isinstance(b, str):
        b = b.encode('utf-8')
    
    # Use hmac.compare_digest for constant-time comparison
    return hmac.compare_digest(a, b)


def generate_password_reset_token(user_id: uuid.UUID, expiry_minutes: int = TOKEN_EXPIRY_MINUTES) -> str:
    """
    Generate a secure token for password reset.
    
    Args:
        user_id: ID of the user requesting password reset
        expiry_minutes: Expiration time in minutes
        
    Returns:
        Signed reset token
    """
    # Create payload with user ID and expiration time
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=expiry_minutes)
    expiry_timestamp = int(expiry.timestamp())
    
    payload = {
        'user_id': str(user_id),
        'exp': expiry_timestamp
    }
    
    # Serialize payload and sign it
    payload_json = json.dumps(payload)
    return sign_data(payload_json)


def verify_password_reset_token(token: str) -> Optional[uuid.UUID]:
    """
    Verify a password reset token and extract the user_id.
    
    Args:
        token: The token to verify
        
    Returns:
        User ID if token is valid, None otherwise
    """
    # Verify and extract data
    payload_json = verify_signed_data(token, as_json=True)
    
    if payload_json is None:
        logger.warning("Invalid reset token signature")
        return None
    
    try:
        # Check expiration
        expiry = payload_json.get('exp', 0)
        current_time = int(datetime.datetime.now().timestamp())
        
        if current_time > expiry:
            logger.warning("Reset token has expired")
            return None
        
        # Extract and return user_id
        user_id_str = payload_json.get('user_id')
        if not user_id_str:
            logger.warning("Reset token missing user_id")
            return None
            
        return uuid.UUID(user_id_str)
        
    except (ValueError, KeyError, AttributeError) as e:
        logger.error(f"Error processing reset token: {str(e)}")
        return None


def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        input_string: The input string to sanitize
        
    Returns:
        Sanitized string
    """
    if input_string is None:
        return ""
    
    # Use bleach to clean the input string
    # Remove all tags and attributes that could be used for XSS
    return bleach.clean(
        input_string,
        tags=[],  # No HTML tags allowed
        attributes={},  # No attributes allowed
        strip=True  # Strip disallowed tags
    )


def get_secure_headers() -> Dict[str, str]:
    """
    Return security headers to be applied to all HTTP responses.
    
    Returns:
        Dictionary of security headers
    """
    return SECURE_HEADERS


def sign_data(data: Union[str, bytes, Dict]) -> str:
    """
    Sign data to ensure integrity.
    
    Args:
        data: Data to sign (string, bytes, or dictionary)
        
    Returns:
        Base64 encoded signature + data
    """
    # Convert data to appropriate format
    if isinstance(data, dict):
        data = json.dumps(data)
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Create signature
    signature = hmac.new(
        key=SECURITY_SALT if isinstance(SECURITY_SALT, bytes) else SECURITY_SALT.encode('utf-8'),
        msg=data,
        digestmod=hashlib.sha256
    ).digest()
    
    # Combine signature and data
    signed_data = signature + data
    
    # Encode to base64
    return base64.urlsafe_b64encode(signed_data).decode('utf-8')


def verify_signed_data(signed_data: str, as_json: bool = False) -> Union[str, Dict, None]:
    """
    Verify and extract data from a signed string.
    
    Args:
        signed_data: The signed data to verify
        as_json: Whether to parse the data as JSON
        
    Returns:
        Original data if signature is valid, None otherwise
    """
    try:
        # Decode from base64
        decoded = base64.urlsafe_b64decode(signed_data)
        
        # Extract signature and data
        signature_size = 32  # SHA-256 produces 32-byte signatures
        signature = decoded[:signature_size]
        data = decoded[signature_size:]
        
        # Compute expected signature
        expected_signature = hmac.new(
            key=SECURITY_SALT if isinstance(SECURITY_SALT, bytes) else SECURITY_SALT.encode('utf-8'),
            msg=data,
            digestmod=hashlib.sha256
        ).digest()
        
        # Verify signature
        if not secure_compare(signature, expected_signature):
            logger.warning("Invalid signature in signed data")
            return None
        
        # Return the data
        if as_json:
            return json.loads(data)
        else:
            return data.decode('utf-8') if isinstance(data, bytes) else data
            
    except Exception as e:
        logger.error(f"Error verifying signed data: {str(e)}")
        return None


def generate_api_key() -> str:
    """
    Generate a secure API key for integration authentication.
    
    Returns:
        Secure API key string
    """
    # Generate a random 48-byte hex string
    return secrets.token_hex(48)


def hash_api_key(api_key: str) -> str:
    """
    Create a hash of an API key for storage.
    
    Args:
        api_key: The API key to hash
        
    Returns:
        Hashed API key
    """
    # Use SHA-256 to hash the API key with the salt
    if isinstance(SECURITY_SALT, bytes):
        salt = SECURITY_SALT
    else:
        salt = SECURITY_SALT.encode('utf-8')
        
    hash_obj = hashlib.sha256(salt + api_key.encode('utf-8'))
    return hash_obj.hexdigest()


def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """
    Verify an API key against a stored hash.
    
    Args:
        api_key: The API key to verify
        stored_hash: The stored hash to compare against
        
    Returns:
        True if API key is valid, False otherwise
    """
    # Hash the provided API key and compare with stored hash
    computed_hash = hash_api_key(api_key)
    return secure_compare(computed_hash, stored_hash)


def is_valid_email(email: str) -> bool:
    """
    Validate an email address format.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    # Basic email validation using regex
    # This regex is not exhaustive but covers most common email formats
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))