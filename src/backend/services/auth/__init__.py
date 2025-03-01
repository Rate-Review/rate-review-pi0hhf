"""
Initializes the authentication and authorization service module by importing and re-exporting key functionality from submodules. This file serves as the entry point for authentication and authorization services in the Justice Bid system.
"""

from .password import (
    verify_password,
    hash_password,
    check_password_strength,
)
from .jwt import (
    create_token,
    validate_token,
    decode_token,
    refresh_token,
)
from .sso import (
    validate_saml_response,
    initiate_sso,
    handle_oauth_callback,
)
from .mfa import (
    generate_mfa_code,
    verify_mfa_code,
    setup_mfa,
)
from .permissions import (
    check_permission,
    get_user_permissions,
    has_permission,
)
from .rbac import (
    get_role_permissions,
    assign_role,
    check_role,
)

__all__ = [
    "verify_password",
    "hash_password",
    "check_password_strength",
    "create_token",
    "validate_token",
    "decode_token",
    "refresh_token",
    "validate_saml_response",
    "initiate_sso",
    "handle_oauth_callback",
    "generate_mfa_code",
    "verify_mfa_code",
    "setup_mfa",
    "check_permission",
    "get_user_permissions",
    "has_permission",
    "get_role_permissions",
    "assign_role",
    "check_role",
]