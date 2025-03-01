"""
Core authentication module for the Justice Bid Rate Negotiation System API.
Implements user authentication, session management, access control, and token handling for securing API endpoints.
Serves as the central authentication gateway for the entire application.
"""

import uuid
from datetime import datetime
from functools import wraps
from typing import Callable, Dict, Optional

from flask import request, g  # flask 2.2.0+

from .errors import AuthenticationError
from .config import get_config
from ...services.auth.jwt import (  # src/backend/services/auth/jwt.py
    validate_access_token,
    get_token_from_auth_header,
    blacklist_token,
    create_access_token,
    create_refresh_token
)
from ...services.auth.rbac import (  # src/backend/services/auth/rbac.py
    has_role,
    has_permission,
    can_access_organization,
    can_access_entity
)
from ...db.models.user import User  # src/backend/db/models/user.py
from ...db.repositories.user_repository import UserRepository  # src/backend/db/repositories/user_repository.py
from ...services.auth.mfa import (  # src/backend/services/auth/mfa.py
    generate_totp_secret,
    verify_totp_code,
    is_mfa_required,
    send_password_reset_email,
    send_mfa_email
)
from ...utils.security import hash_password  # src/backend/utils/security.py
from ...utils.logging import get_logger  # src/backend/utils/logging.py


# Initialize logger
logger = get_logger(__name__)

# Get application configuration
config = get_config()

# Global variables for authentication
user_repository: UserRepository = None  # type: ignore # UserRepository will be initialized in initialize_auth
JWT_ACCESS_TOKEN_EXPIRY = config.JWT_ACCESS_TOKEN_EXPIRY if hasattr(config, 'JWT_ACCESS_TOKEN_EXPIRY') else 60
JWT_REFRESH_TOKEN_EXPIRY = config.JWT_REFRESH_TOKEN_EXPIRY if hasattr(config, 'JWT_REFRESH_TOKEN_EXPIRY') else 24 * 60 * 30
MFA_REQUIRED_ROLES = config.MFA_REQUIRED_ROLES if hasattr(config, 'MFA_REQUIRED_ROLES') else []
MFA_TOKEN_EXPIRY = config.MFA_TOKEN_EXPIRY if hasattr(config, 'MFA_TOKEN_EXPIRY') else 10


def initialize_auth(UserRepository: UserRepository) -> None:
    """
    Initialize authentication with user repository dependency.

    Args:
        UserRepository: repository
    """
    global user_repository
    user_repository = UserRepository
    logger.info("Authentication initialized with user repository")


def log_security_event(event_type: str, event_data: dict) -> None:
    """Logs security-related events for audit purposes

    Args:
        event_type (str): event_type
        event_data (dict): event_data
    """
    event_data['timestamp'] = datetime.utcnow().isoformat()
    try:
        event_data['request_url'] = request.url
        event_data['request_method'] = request.method
        event_data['remote_addr'] = request.remote_addr
    except RuntimeError:
        pass

    if event_type.startswith('error'):
        logger.error(f"Security Event: {event_type}", extra={'additional_data': event_data})
    elif event_type.startswith('warning'):
        logger.warning(f"Security Event: {event_type}", extra={'additional_data': event_data})
    else:
        logger.info(f"Security Event: {event_type}", extra={'additional_data': event_data})


def login_user(email: str, password: str) -> Dict:
    """Authenticate a user with email and password

    Args:
        email (str): email
        password (str): password

    Returns:
        Dict: Authentication result with tokens or MFA challenge
    """
    user = user_repository.find_by_email(email)
    if not user:
        log_security_event('error:login_failed', {'email': email, 'reason': 'user_not_found'})
        raise AuthenticationError("Invalid credentials")

    if not user.verify_password(password):
        log_security_event('error:login_failed', {'email': email, 'reason': 'invalid_password'})
        raise AuthenticationError("Invalid credentials")

    if not user.is_active:
        log_security_event('error:login_failed', {'email': email, 'reason': 'inactive_user'})
        raise AuthenticationError("Account is inactive")

    user.update_last_login()
    user_repository._db.commit()

    if is_mfa_required(user) and user.mfa_enabled:
        challenge = generate_mfa_challenge(user)
        log_security_event('info:mfa_challenge_required', {'user_id': str(user.id), 'mfa_type': challenge['method']})
        return {'mfa_required': True, 'mfa_challenge': challenge}

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    log_security_event('info:login_success', {'user_id': str(user.id)})
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': serialize_user(user)
    }


def complete_mfa_login(user_id: uuid.UUID, mfa_code: str) -> Dict:
    """Complete login process with MFA verification

    Args:
        user_id (uuid.UUID): user_id
        mfa_code (str): mfa_code

    Returns:
        Dict: Authentication result with tokens
    """
    user = user_repository.find_by_id(user_id)
    if not user:
        log_security_event('error:mfa_failed', {'user_id': str(user_id), 'reason': 'user_not_found'})
        raise AuthenticationError("Invalid user")

    if not user.preferences or 'mfa' not in user.preferences:
        log_security_event('error:mfa_failed', {'user_id': str(user_id), 'reason': 'mfa_not_configured'})
        raise AuthenticationError("MFA not configured")

    mfa_method = user.preferences['mfa'].get('method')
    if mfa_method == 'totp':
        if not verify_totp_code(user.mfa_secret, mfa_code):
            log_security_event('error:mfa_failed', {'user_id': str(user_id), 'mfa_type': 'totp', 'reason': 'invalid_code'})
            raise AuthenticationError("Invalid MFA code")
    elif mfa_method == 'email':
        # TODO: Implement email MFA verification
        log_security_event('error:mfa_failed', {'user_id': str(user_id), 'mfa_type': 'email', 'reason': 'not_implemented'})
        raise AuthenticationError("Email MFA not yet implemented")
    else:
        log_security_event('error:mfa_failed', {'user_id': str(user_id), 'reason': 'invalid_mfa_method'})
        raise AuthenticationError("Invalid MFA method")

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    log_security_event('info:mfa_success', {'user_id': str(user.id), 'mfa_type': mfa_method})
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': serialize_user(user)
    }


def refresh_auth_token(refresh_token: str) -> Dict:
    """Generate new tokens using a refresh token

    Args:
        refresh_token (str): refresh_token

    Returns:
        Dict: New access token and expiry
    """
    try:
        user_id = validate_access_token(refresh_token)['user_id']
        user = user_repository.find_by_id(user_id)

        if not user or not user.is_active:
            log_security_event('error:token_refresh_failed', {'user_id': str(user_id), 'reason': 'invalid_user'})
            raise AuthenticationError("Invalid user")

        blacklist_token(refresh_token)
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        log_security_event('info:token_refresh_success', {'user_id': str(user.id)})
        return {'access_token': access_token, 'refresh_token': refresh_token}
    except Exception as e:
        log_security_event('error:token_refresh_failed', {'token': refresh_token, 'reason': str(e)})
        raise AuthenticationError(str(e))


def logout_user(token: str) -> bool:
    """Log out a user by blacklisting their token

    Args:
        token (str): token

    Returns:
        bool: True if logout successful, False otherwise
    """
    success = blacklist_token(token)
    if success:
        log_security_event('info:logout_success', {'token': token})
    else:
        log_security_event('warning:logout_failed', {'token': token})
    return success


def get_current_user() -> User:
    """Get the current authenticated user from the request context

    Returns:
        User: Current authenticated user
    """
    if 'user' not in g:
        raise AuthenticationError("User not authenticated")
    return g.user


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication for API endpoints

    Args:
        f (Callable): f

    Returns:
        Callable: Wrapped function with authentication check
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            log_security_event('warning:auth_required', {'endpoint': request.path, 'reason': 'no_auth_header'})
            return {'message': 'Authentication required'}, 401

        token = get_token_from_auth_header(auth_header)
        if not token:
            log_security_event('warning:auth_required', {'endpoint': request.path, 'reason': 'invalid_auth_header'})
            return {'message': 'Invalid authentication header'}, 401

        try:
            payload = validate_access_token(token)
            user_id = payload['user_id']
            user = user_repository.find_by_id(user_id)
            if not user or not user.is_active:
                log_security_event('warning:auth_required', {'endpoint': request.path, 'user_id': str(user_id), 'reason': 'invalid_user'})
                return {'message': 'Invalid token'}, 401
            g.user = user
            return f(*args, **kwargs)
        except Exception as e:
            log_security_event('warning:auth_required', {'endpoint': request.path, 'token': token, 'reason': str(e)})
            return {'message': 'Invalid token'}, 401
    return decorated_function


def require_role(role: str) -> Callable:
    """Decorator to require specific role for API endpoints

    Args:
        role (str): role

    Returns:
        Callable: Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not has_role(user, role):
                log_security_event('warning:authz_failed', {'endpoint': request.path, 'user_id': str(user.id), 'required_role': role})
                return {'message': 'Forbidden'}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_permission(permission: str) -> Callable:
    """Decorator to require specific permission for API endpoints

    Args:
        permission (str): permission

    Returns:
        Callable: Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not has_permission(user, permission):
                log_security_event('warning:authz_failed', {'endpoint': request.path, 'user_id': str(user.id), 'required_permission': permission})
                return {'message': 'Forbidden'}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_organization_access(org_id_param: str) -> Callable:
    """Decorator to require access to a specific organization

    Args:
        org_id_param (str): org_id_param

    Returns:
        Callable: Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            organization_id = kwargs.get(org_id_param)
            if not can_access_organization(user, organization_id):
                log_security_event('warning:authz_failed', {'endpoint': request.path, 'user_id': str(user.id), 'org_id': str(organization_id)})
                return {'message': 'Forbidden'}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_entity_access(entity_type: str, entity_id_param: str, action: str) -> Callable:
    """Decorator to require access to a specific entity for an action

    Args:
        entity_type (str): entity_type
        entity_id_param (str): entity_id_param
        action (str): action

    Returns:
        Callable: Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            entity_id = kwargs.get(entity_id_param)
            if not can_access_entity(user, entity_type, entity_id, action):
                log_security_event('warning:authz_failed', {'endpoint': request.path, 'user_id': str(user.id), 'entity_type': entity_type, 'entity_id': str(entity_id), 'action': action})
                return {'message': 'Forbidden'}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def request_password_reset(email: str) -> bool:
    """Request a password reset for a user

    Args:
        email (str): email

    Returns:
        bool: True if request was processed, even if user not found (for security)
    """
    user = user_repository.get_by_email(email)
    if user and user.is_active:
        reset_token = generate_totp_secret()  # TODO: Replace with actual reset token generation
        send_password_reset_email(email, reset_token)
        log_security_event('info:password_reset_requested', {'email': email})
    return True  # Always return True to prevent email enumeration


def reset_password(token: str, new_password: str) -> bool:
    """Reset user password using a reset token

    Args:
        token (str): token
        new_password (str): new_password

    Returns:
        bool: True if password was reset successfully
    """
    # TODO: Implement token validation and password reset logic
    log_security_event('info:password_reset_attempt', {'token': token})
    return True


def change_password(user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
    """Change password for authenticated user

    Args:
        user_id (uuid.UUID): user_id
        current_password (str): current_password
        new_password (str): new_password

    Returns:
        bool: True if password was changed successfully
    """
    user = user_repository.find_by_id(user_id)
    if not user:
        log_security_event('error:password_change_failed', {'user_id': str(user_id), 'reason': 'user_not_found'})
        raise AuthenticationError("Invalid user")

    if not user.verify_password(current_password):
        log_security_event('error:password_change_failed', {'user_id': str(user_id), 'reason': 'invalid_current_password'})
        raise AuthenticationError("Invalid current password")

    user.set_password(new_password)
    user_repository._db.commit()
    log_security_event('info:password_change_success', {'user_id': str(user_id)})
    return True


def initiate_sso_login(provider: str, organization_id: uuid.UUID) -> Dict:
    """Initiate SSO authentication flow

    Args:
        provider (str): provider
        organization_id (uuid.UUID): organization_id

    Returns:
        Dict: SSO redirect information
    """
    # TODO: Implement SSO initiation logic
    log_security_event('info:sso_initiation', {'provider': provider, 'organization_id': str(organization_id)})
    return {}


def complete_sso_login(provider: str, organization_id: uuid.UUID, provider_data: dict) -> Dict:
    """Complete SSO authentication after provider callback

    Args:
        provider (str): provider
        organization_id (uuid.UUID): organization_id
        provider_data (dict): provider_data

    Returns:
        Dict: Authentication result with tokens
    """
    # TODO: Implement SSO completion logic
    log_security_event('info:sso_completion', {'provider': provider, 'organization_id': str(organization_id)})
    return {}


def serialize_user(user: User) -> dict:
    """Serialize user object for API responses

    Args:
        user (User): user

    Returns:
        dict: Serialized user data
    """
    return {
        'id': str(user.id),
        'email': user.email,
        'name': user.name,
        'role': user.role.value,
        'organization_id': str(user.organization_id),
        'mfa_enabled': user.mfa_enabled
    }


def generate_mfa_challenge(user: User) -> dict:
    """Generate MFA challenge for user authentication

    Args:
        user (User): user

    Returns:
        dict: MFA challenge details
    """
    # TODO: Implement MFA challenge generation logic
    log_security_event('info:mfa_challenge_generated', {'user_id': str(user.id)})
    return {}


class MFARequiredError(Exception):
    """Custom exception for MFA required scenarios"""
    def __init__(self, challenge: dict, message: str = "Multi-factor authentication required"):
        """Initialize MFA required error with challenge details

        Args:
            challenge (dict): challenge
            message (str): message
        """
        super().__init__(message)
        self.challenge = challenge