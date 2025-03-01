"""
Role-Based Access Control (RBAC) module for implementing and enforcing hierarchical roles and permissions across the Justice Bid system.
Handles role definitions, permission checking, and access control at organization, peer group, and entity levels.
"""

import enum  # latest
import uuid  # latest
from dataclasses import dataclass  # latest
from typing import Dict, List, Optional, Callable  # latest

import sqlalchemy  # ~=1.4.0
from sqlalchemy.orm import Session

from src.backend.db.models.organization import Organization  # Access organization information for organization-level permissions
from src.backend.db.models.user import User  # Access user model for role and permission information
from src.backend.db.repositories.user_repository import UserRepository  # Data access for user information
from src.backend.services.auth.jwt import verify_token  # Verify authentication tokens to extract user information
from src.backend.services.auth.permissions import (  # Check individual permissions for RBAC validation
    Permission,
    get_permissions_for_action,  # Get required permissions for specific actions
)
from src.backend.utils.logging import logger  # Logging activities and error handling
from src.backend.utils.security import secure_compare  # Securely compare strings to prevent timing attacks


# Define global constants for roles
SYSTEM_ADMIN_ROLE = "system_administrator"  # Administrator role with system-wide privileges
CLIENT_ADMIN_ROLE = "client_administrator"  # Administrator role for client organizations
FIRM_ADMIN_ROLE = "firm_administrator"  # Administrator role for law firm organizations
RATE_ADMIN_ROLE = "rate_administrator"  # Role for managing rates and negotiations
APPROVER_ROLE = "approver"  # Role for users who can approve rates
ANALYST_ROLE = "analyst"  # Role for users who can view analytics
STANDARD_USER_ROLE = "standard_user"  # Basic user role with limited permissions


@dataclass
class Role:
    """
    Data class representing a role in the system with its associated permissions.
    """

    code: str  # Unique code for the role
    name: str  # Human-readable name of the role
    description: str  # Description of the role
    permissions: List[str]  # List of permission codes assigned to the role
    is_admin: bool  # Flag indicating if the role is an administrator role
    organization_type: Optional[str]  # Type of organization this role applies to (client, firm, etc.)

    def __init__(self, code: str, name: str, description: str, permissions: List[str], is_admin: bool,
                 organization_type: Optional[str] = None):
        """
        Initialize a new Role instance.

        Args:
            code: Unique code for the role
            name: Human-readable name of the role
            description: Description of the role
            permissions: List of permission codes assigned to the role
            is_admin: Flag indicating if the role is an administrator role
            organization_type: Type of organization this role applies to (client, firm, etc.)
        """
        self.code = code
        self.name = name
        self.description = description
        self.permissions = permissions
        self.is_admin = is_admin
        self.organization_type = organization_type


class RoleManager:
    """
    Manages role definitions, assignments, and permission checks throughout the system.
    """

    def __init__(self):
        """
        Initialize the RoleManager with predefined roles and hierarchy.
        """
        self._roles: Dict[str, Role] = {}  # Dictionary to store registered roles
        self._role_hierarchy: Dict[str, List[str]] = {}  # Dictionary to store role hierarchy
        self._register_all()  # Register system-defined roles
        self._setup_role_hierarchy()  # Set up role hierarchy relationships

    def register_role(self, role: Role) -> None:
        """
        Register a new role in the system.

        Args:
            role: The Role object to register
        """
        self._roles[role.code] = role  # Add the role to the roles dictionary
        logger.info(f"Registered role: {role.code}")  # Log the registration of the new role

    def get_role(self, role_code: str) -> Optional[Role]:
        """
        Get a role by its code.

        Args:
            role_code: The code of the role to retrieve

        Returns:
            The Role object if found, None otherwise
        """
        return self._roles.get(role_code)  # Retrieve the role from the roles dictionary

    def get_all_roles(self) -> List[Role]:
        """
        Get all registered roles.

        Returns:
            List of all registered Role objects
        """
        return list(self._roles.values())  # Return a list of all roles in the roles dictionary

    def get_organization_roles(self, organization_type: str) -> List[Role]:
        """
        Get roles applicable to a specific organization type.

        Args:
            organization_type: The type of organization to filter by

        Returns:
            List of roles applicable to the specified organization type
        """
        return [role for role in self._roles.values() if
                role.organization_type == organization_type]  # Filter the roles dictionary

    def has_permission(self, role_code: str, permission: str) -> bool:
        """
        Check if a role has a specific permission.

        Args:
            role_code: The code of the role to check
            permission: The permission to check for

        Returns:
            True if the role has the permission, False otherwise
        """
        role = self.get_role(role_code)  # Get the role by its code
        if role:
            return permission in role.permissions  # Check if the permission is in the role's permissions list
        return False

    def set_parent_role(self, parent_role_code: str, child_role_code: str) -> None:
        """
        Set a parent-child relationship between roles.

        Args:
            parent_role_code: The code of the parent role
            child_role_code: The code of the child role
        """
        if parent_role_code not in self._roles or child_role_code not in self._roles:
            raise ValueError("Both parent and child roles must be registered before setting hierarchy.")

        if parent_role_code not in self._role_hierarchy:
            self._role_hierarchy[parent_role_code] = []

        self._role_hierarchy[parent_role_code].append(child_role_code)

    def get_effective_permissions(self, role_code: str) -> List[str]:
        """
        Get all permissions effective for a role, including inherited ones.

        Args:
            role_code: The code of the role to get permissions for

        Returns:
            Set of all permissions effective for the role
        """
        effective_permissions = set()
        role = self.get_role(role_code)
        if role:
            effective_permissions.update(role.permissions)
            inherited_roles = self._get_inherited_roles(role_code)
            for inherited_role_code in inherited_roles:
                inherited_role = self.get_role(inherited_role_code)
                if inherited_role:
                    effective_permissions.update(inherited_role.permissions)
        return list(effective_permissions)

    def _get_inherited_roles(self, role_code: str) -> List[str]:
        """
        Get all roles inherited by a specific role.

        Args:
            role_code: The code of the role to get inherited roles for

        Returns:
            List of all roles inherited by the specified role
        """
        inherited_roles = []
        if role_code in self._role_hierarchy:
            for child_role in self._role_hierarchy[role_code]:
                inherited_roles.append(child_role)
                inherited_roles.extend(self._get_inherited_roles(child_role))
        return inherited_roles

    def _register_all(self):
        """
        Register all system-defined roles.
        """
        self.register_role(
            Role(code=SYSTEM_ADMIN_ROLE, name="System Administrator", description="Full system access",
                 permissions=["system:*"], is_admin=True)
        )
        self.register_role(
            Role(code=CLIENT_ADMIN_ROLE, name="Client Administrator", description="Client organization admin",
                 permissions=["organizations:read", "organizations:update", "users:create", "users:read",
                              "users:update", "users:delete", "rates:read", "negotiations:read", "analytics:view",
                              "ocg:read", "ocg:update"], is_admin=True, organization_type="client")
        )
        self.register_role(
            Role(code=FIRM_ADMIN_ROLE, name="Law Firm Administrator", description="Law firm organization admin",
                 permissions=["organizations:read", "organizations:update", "users:create", "users:read",
                              "users:update", "users:delete", "rates:create", "rates:read", "rates:update",
                              "rates:delete", "negotiations:create", "negotiations:read", "negotiations:update",
                              "negotiations:delete", "ocg:read", "ocg:negotiate"], is_admin=True,
                 organization_type="law_firm")
        )
        self.register_role(
            Role(code=RATE_ADMIN_ROLE, name="Rate Administrator", description="Rate and negotiation manager",
                 permissions=["rates:create", "rates:read", "rates:update", "rates:delete", "rates:submit",
                              "rates:export", "rates:import", "negotiations:create", "negotiations:read",
                              "negotiations:update", "negotiations:delete"], is_admin=False)
        )
        self.register_role(
            Role(code=APPROVER_ROLE, name="Approver", description="Rate approver",
                 permissions=["rates:read", "rates:approve", "rates:reject", "negotiations:read",
                              "negotiations:approve", "negotiations:reject"], is_admin=False)
        )
        self.register_role(
            Role(code=ANALYST_ROLE, name="Analyst", description="Analytics viewer",
                 permissions=["analytics:view", "analytics:create_reports", "analytics:export"], is_admin=False)
        )
        self.register_role(
            Role(code=STANDARD_USER_ROLE, name="Standard User", description="Basic user",
                 permissions=["rates:read", "negotiations:read", "messages:create", "messages:read"],
                 is_admin=False)
        )

    def _setup_role_hierarchy(self):
        """
        Set up the role hierarchy relationships.
        """
        self.set_parent_role(SYSTEM_ADMIN_ROLE, CLIENT_ADMIN_ROLE)
        self.set_parent_role(SYSTEM_ADMIN_ROLE, FIRM_ADMIN_ROLE)
        self.set_parent_role(CLIENT_ADMIN_ROLE, RATE_ADMIN_ROLE)
        self.set_parent_role(FIRM_ADMIN_ROLE, RATE_ADMIN_ROLE)
        self.set_parent_role(RATE_ADMIN_ROLE, APPROVER_ROLE)
        self.set_parent_role(RATE_ADMIN_ROLE, ANALYST_ROLE)
        self.set_parent_role(APPROVER_ROLE, STANDARD_USER_ROLE)
        self.set_parent_role(ANALYST_ROLE, STANDARD_USER_ROLE)


class RBACDecorator:
    """
    Decorator class for enforcing RBAC on API endpoints.
    """

    def __init__(self):
        """
        Initialize the RBACDecorator.
        """
        pass

    def require_role(self, role: str):
        """
        Decorator to require a specific role for accessing an endpoint.

        Args:
            role: The role required to access the endpoint
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                # Get the current user from the request context (replace with actual implementation)
                user = self._get_current_user()
                if user and has_role(user, role):
                    return func(*args, **kwargs)
                else:
                    return {"message": "Forbidden"}, 403

            return wrapper

        return decorator

    def require_permission(self, permission: str):
        """
        Decorator to require a specific permission for accessing an endpoint.

        Args:
            permission: The permission required to access the endpoint
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                # Get the current user from the request context (replace with actual implementation)
                user = self._get_current_user()
                if user and has_permission(user, permission):
                    return func(*args, **kwargs)
                else:
                    return {"message": "Forbidden"}, 403

            return wrapper

        return decorator

    def require_organization_access(self, org_id_param: str):
        """
        Decorator to require access to a specific organization.

        Args:
            org_id_param: The name of the parameter containing the organization ID
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                # Get the current user from the request context (replace with actual implementation)
                user = self._get_current_user()
                organization_id = kwargs.get(org_id_param)
                if user and organization_id and can_access_organization(user, organization_id):
                    return func(*args, **kwargs)
                else:
                    return {"message": "Forbidden"}, 403

            return wrapper

        return decorator

    def require_entity_access(self, entity_type: str, entity_id_param: str, action: str):
        """
        Decorator to require access to a specific entity for an action.

        Args:
            entity_type: The type of entity (e.g., "rate", "negotiation")
            entity_id_param: The name of the parameter containing the entity ID
            action: The action being performed on the entity (e.g., "read", "update")
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                # Get the current user from the request context (replace with actual implementation)
                user = self._get_current_user()
                entity_id = kwargs.get(entity_id_param)
                if user and entity_id and can_access_entity(user, entity_type, entity_id, action):
                    return func(*args, **kwargs)
                else:
                    return {"message": "Forbidden"}, 403

            return wrapper

        return decorator

    def _get_current_user(self) -> Optional[User]:
        """
        Helper function to retrieve the current user from the request context.
        (Replace with actual implementation using Flask or similar framework)
        """
        # Placeholder implementation - replace with actual logic to retrieve the user
        # from the request context (e.g., using Flask's 'g' object or similar)
        # This is just a stub and needs to be implemented based on the framework used
        return None


# Initialize the RoleManager
role_manager = RoleManager()


def get_role_permissions(role: str) -> List[str]:
    """
    Get the permissions associated with a specific role.

    Args:
        role: The role to get permissions for

    Returns:
        List of permission codes assigned to the role
    """
    return role_manager.get_effective_permissions(role)


def get_user_roles(user: User) -> List[str]:
    """
    Get all roles assigned to a user.

    Args:
        user: The User object to get roles for

    Returns:
        List of role codes assigned to the user
    """
    roles = [user.role.value]  # Extract the primary role from the user object
    if user.permissions and "admin" in user.permissions:  # Check for any additional roles
        roles.append("admin")
    return roles


def assign_role(user: User, role: str, user_repository: UserRepository) -> bool:
    """
    Assign a role to a user.

    Args:
        user: The User object to assign the role to
        role: The role to assign
        user_repository: The UserRepository instance to use for updating the user

    Returns:
        True if role was successfully assigned, False otherwise
    """
    if role_manager.get_role(role):  # Validate the role exists
        user.role = role
        user_repository.update(user.id, {'role': role})  # Save the updated user via the repository
        logger.info(f"Assigned role {role} to user {user.id}")  # Log the role assignment
        return True
    else:
        logger.warning(f"Attempted to assign invalid role {role} to user {user.id}")
        return False


def has_role(user: User, role: str) -> bool:
    """
    Check if a user has a specific role.

    Args:
        user: The User object to check
        role: The role to check for

    Returns:
        True if user has the role, False otherwise
    """
    user_roles = get_user_roles(user)  # Get all roles assigned to the user
    return role in user_roles  # Check if the requested role is in the user's roles


def has_role_or_permission(user: User, role: Optional[str] = None, permission: Optional[str] = None) -> bool:
    """
    Check if a user has a specific role or permission.

    Args:
        user: The User object to check
        role: The role to check for (optional)
        permission: The permission to check for (optional)

    Returns:
        True if user has the role or permission, False otherwise
    """
    if role and has_role(user, role):  # If role is provided, check if user has the role
        return True
    if permission and has_permission(user, permission):  # If permission is provided, check if user has the permission
        return True
    return False  # Return False if neither check passes


def has_permission(user: User, permission: str) -> bool:
    """
    Check if a user has a specific permission.

    Args:
        user: The User object to check
        permission: The permission to check for

    Returns:
        True if user has the permission, False otherwise
    """
    # Check if the user has the permission directly
    if user.permissions and permission in user.permissions:
        return True

    # Check if any of the user's roles have the permission
    user_roles = get_user_roles(user)
    for role in user_roles:
        if role_manager.has_permission(role, permission):
            return True

    return False


def can_access_organization(user: User, organization_id: uuid.UUID) -> bool:
    """
    Check if a user can access a specific organization.

    Args:
        user: The User object to check
        organization_id: The ID of the organization to check access to

    Returns:
        True if user can access the organization, False otherwise
    """
    if has_role(user, SYSTEM_ADMIN_ROLE):  # Check if user is a system administrator
        return True  # System admins can access all organizations
    if user.organization_id == organization_id:  # Check if the organization is the user's own organization
        return True
    # Add more complex logic here based on cross-organization permissions
    return False


def can_access_entity(user: User, entity_type: str, entity_id: uuid.UUID, action: str) -> bool:
    """
    Check if a user can access a specific entity (rate, negotiation, etc.).

    Args:
        user: The User object to check
        entity_type: The type of entity (e.g., "rate", "negotiation")
        entity_id: The ID of the entity to check access to
        action: The action being performed on the entity (e.g., "read", "update")

    Returns:
        True if user can access the entity for the specified action, False otherwise
    """
    # Determine organization ownership of the entity (replace with actual logic)
    organization_id = _get_entity_organization_id(entity_type, entity_id)
    if not organization_id:
        logger.warning(f"Could not determine organization for entity {entity_type} with ID {entity_id}")
        return False

    if not can_access_organization(user, organization_id):  # Check if user has access to the organization
        return False

    required_permissions = get_permissions_for_action(entity_type, action)  # Get required permissions for the action
    if not required_permissions:
        logger.warning(f"No permissions defined for action {action} on entity type {entity_type}")
        return False

    for permission in required_permissions:  # Check if user has the required permissions
        if not has_permission(user, permission):
            return False

    return True  # Return True if all checks pass


def _get_entity_organization_id(entity_type: str, entity_id: uuid.UUID) -> Optional[uuid.UUID]:
    """
    Helper function to determine the organization ID for a given entity.
    (Replace with actual implementation using database queries or similar)
    """
    # Placeholder implementation - replace with actual logic to retrieve the organization ID
    # based on the entity type and ID. This is just a stub and needs to be implemented
    # based on the data model and database access patterns.
    return uuid.uuid4()  # Placeholder - replace with actual logic


def get_role_hierarchy() -> Dict[str, List[str]]:
    """
    Get the hierarchy of roles in the system.

    Returns:
        Dictionary mapping parent roles to their child roles
    """
    return role_manager._role_hierarchy


def get_inherited_roles(role: str) -> List[str]:
    """
    Get all roles inherited by a specific role.

    Args:
        role: The role to get inherited roles for

    Returns:
        List of all roles inherited by the specified role
    """
    return role_manager._get_inherited_roles(role)


def has_inherited_role(user: User, role: str) -> bool:
    """
    Check if a user has a specific role or any role that inherits from it.

    Args:
        user: The User object to check
        role: The role to check for

    Returns:
        True if user has the role or an inheriting role, False otherwise
    """
    user_roles = get_user_roles(user)  # Get all roles assigned to the user
    inherited_roles = get_inherited_roles(role)  # Get the list of roles that inherit from the specified role
    if role in user_roles or any(inherited_role in user_roles for inherited_role in
                                 inherited_roles):  # Check if any of the user's roles match
        return True
    return False