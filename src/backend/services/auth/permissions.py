"""
Permission system for the Justice Bid Rate Negotiation System.

This module defines the permission framework that underpins the application's
role-based access control system. It provides permission definitions, permission
categories, and utilities for permission management.
"""

import enum
from typing import Dict, List, Optional
from dataclasses import dataclass

from ../../utils/constants import UserRole, OrganizationType
from ../../utils/logging import get_logger

logger = get_logger(__name__)


class PermissionCategory(enum.Enum):
    """Enumeration of permission categories in the system."""
    SYSTEM = "system"
    USER = "user"
    ORGANIZATION = "organization"
    RATE = "rate"
    NEGOTIATION = "negotiation"
    ANALYTICS = "analytics"
    MESSAGE = "message"
    DOCUMENT = "document"
    OCG = "ocg"
    INTEGRATION = "integration"
    AI = "ai"


@dataclass
class Permission:
    """Represents a system permission with a name and description."""
    name: str
    description: str
    category: PermissionCategory
    
    def matches(self, permission_str: str) -> bool:
        """
        Check if permission matches a permission string, supporting wildcard patterns.
        
        Args:
            permission_str: The permission string to check against
            
        Returns:
            True if the permission matches, False otherwise
        """
        # Exact match
        if self.name == permission_str:
            return True
        
        # Wildcard match (e.g., "rates:*" matches "rates:create")
        if self.name.endswith('*'):
            prefix = self.name[:-1]  # Remove the asterisk
            if permission_str.startswith(prefix):
                return True
        
        return False
    
    def __str__(self) -> str:
        """String representation of the permission."""
        return self.name


class SystemPermissions:
    """Static class containing system-wide permissions."""
    ADMIN = Permission("system:admin", "Full system administration rights", PermissionCategory.SYSTEM)
    CONFIGURE = Permission("system:configure", "Configure system settings", PermissionCategory.SYSTEM)
    AUDIT_LOG_VIEW = Permission("system:audit_log_view", "View system audit logs", PermissionCategory.SYSTEM)
    ALL = Permission("system:*", "All system permissions", PermissionCategory.SYSTEM)


class UserPermissions:
    """Static class containing user management permissions."""
    CREATE = Permission("users:create", "Create users", PermissionCategory.USER)
    READ = Permission("users:read", "View user details", PermissionCategory.USER)
    UPDATE = Permission("users:update", "Update user details", PermissionCategory.USER)
    DELETE = Permission("users:delete", "Delete users", PermissionCategory.USER)
    MANAGE_PERMISSIONS = Permission("users:manage_permissions", "Manage user permissions", PermissionCategory.USER)
    ALL = Permission("users:*", "All user permissions", PermissionCategory.USER)


class OrganizationPermissions:
    """Static class containing organization management permissions."""
    CREATE = Permission("organizations:create", "Create organizations", PermissionCategory.ORGANIZATION)
    READ = Permission("organizations:read", "View organization details", PermissionCategory.ORGANIZATION)
    UPDATE = Permission("organizations:update", "Update organization details", PermissionCategory.ORGANIZATION)
    DELETE = Permission("organizations:delete", "Delete organizations", PermissionCategory.ORGANIZATION)
    MANAGE_SETTINGS = Permission("organizations:manage_settings", "Manage organization settings", PermissionCategory.ORGANIZATION)
    MANAGE_PEER_GROUPS = Permission("organizations:manage_peer_groups", "Manage organization peer groups", PermissionCategory.ORGANIZATION)
    ALL = Permission("organizations:*", "All organization permissions", PermissionCategory.ORGANIZATION)


class RatePermissions:
    """Static class containing rate management permissions."""
    CREATE = Permission("rates:create", "Create rates", PermissionCategory.RATE)
    READ = Permission("rates:read", "View rate details", PermissionCategory.RATE)
    UPDATE = Permission("rates:update", "Update rates", PermissionCategory.RATE)
    DELETE = Permission("rates:delete", "Delete rates", PermissionCategory.RATE)
    SUBMIT = Permission("rates:submit", "Submit rates for approval", PermissionCategory.RATE)
    APPROVE = Permission("rates:approve", "Approve rates", PermissionCategory.RATE)
    REJECT = Permission("rates:reject", "Reject rates", PermissionCategory.RATE)
    COUNTER_PROPOSE = Permission("rates:counter_propose", "Counter-propose rates", PermissionCategory.RATE)
    EXPORT = Permission("rates:export", "Export rates", PermissionCategory.RATE)
    IMPORT = Permission("rates:import", "Import rates", PermissionCategory.RATE)
    MANAGE_RULES = Permission("rates:manage_rules", "Manage rate rules", PermissionCategory.RATE)
    ALL = Permission("rates:*", "All rate permissions", PermissionCategory.RATE)


class NegotiationPermissions:
    """Static class containing negotiation workflow permissions."""
    CREATE = Permission("negotiations:create", "Create negotiations", PermissionCategory.NEGOTIATION)
    READ = Permission("negotiations:read", "View negotiation details", PermissionCategory.NEGOTIATION)
    UPDATE = Permission("negotiations:update", "Update negotiations", PermissionCategory.NEGOTIATION)
    DELETE = Permission("negotiations:delete", "Delete negotiations", PermissionCategory.NEGOTIATION)
    INITIATE = Permission("negotiations:initiate", "Initiate negotiations", PermissionCategory.NEGOTIATION)
    APPROVE = Permission("negotiations:approve", "Approve negotiations", PermissionCategory.NEGOTIATION)
    REJECT = Permission("negotiations:reject", "Reject negotiations", PermissionCategory.NEGOTIATION)
    COUNTER_PROPOSE = Permission("negotiations:counter_propose", "Counter-propose in negotiations", PermissionCategory.NEGOTIATION)
    MANAGE_WORKFLOW = Permission("negotiations:manage_workflow", "Manage negotiation workflow", PermissionCategory.NEGOTIATION)
    ALL = Permission("negotiations:*", "All negotiation permissions", PermissionCategory.NEGOTIATION)


class AnalyticsPermissions:
    """Static class containing analytics and reporting permissions."""
    VIEW = Permission("analytics:view", "View analytics", PermissionCategory.ANALYTICS)
    CREATE_REPORTS = Permission("analytics:create_reports", "Create custom reports", PermissionCategory.ANALYTICS)
    EXPORT = Permission("analytics:export", "Export analytics data", PermissionCategory.ANALYTICS)
    SHARE = Permission("analytics:share", "Share analytics with others", PermissionCategory.ANALYTICS)
    ALL = Permission("analytics:*", "All analytics permissions", PermissionCategory.ANALYTICS)


class MessagePermissions:
    """Static class containing messaging permissions."""
    CREATE = Permission("messages:create", "Create messages", PermissionCategory.MESSAGE)
    READ = Permission("messages:read", "Read messages", PermissionCategory.MESSAGE)
    UPDATE = Permission("messages:update", "Update messages", PermissionCategory.MESSAGE)
    DELETE = Permission("messages:delete", "Delete messages", PermissionCategory.MESSAGE)
    ALL = Permission("messages:*", "All message permissions", PermissionCategory.MESSAGE)


class DocumentPermissions:
    """Static class containing document management permissions."""
    CREATE = Permission("documents:create", "Create documents", PermissionCategory.DOCUMENT)
    READ = Permission("documents:read", "Read documents", PermissionCategory.DOCUMENT)
    UPDATE = Permission("documents:update", "Update documents", PermissionCategory.DOCUMENT)
    DELETE = Permission("documents:delete", "Delete documents", PermissionCategory.DOCUMENT)
    SHARE = Permission("documents:share", "Share documents", PermissionCategory.DOCUMENT)
    ALL = Permission("documents:*", "All document permissions", PermissionCategory.DOCUMENT)


class OCGPermissions:
    """Static class containing Outside Counsel Guidelines permissions."""
    CREATE = Permission("ocg:create", "Create OCGs", PermissionCategory.OCG)
    READ = Permission("ocg:read", "Read OCGs", PermissionCategory.OCG)
    UPDATE = Permission("ocg:update", "Update OCGs", PermissionCategory.OCG)
    DELETE = Permission("ocg:delete", "Delete OCGs", PermissionCategory.OCG)
    PUBLISH = Permission("ocg:publish", "Publish OCGs", PermissionCategory.OCG)
    NEGOTIATE = Permission("ocg:negotiate", "Negotiate OCGs", PermissionCategory.OCG)
    SIGN = Permission("ocg:sign", "Sign OCGs", PermissionCategory.OCG)
    ALL = Permission("ocg:*", "All OCG permissions", PermissionCategory.OCG)


class IntegrationPermissions:
    """Static class containing integration permissions."""
    CONFIGURE = Permission("integrations:configure", "Configure integrations", PermissionCategory.INTEGRATION)
    IMPORT = Permission("integrations:import", "Import data from integrations", PermissionCategory.INTEGRATION)
    EXPORT = Permission("integrations:export", "Export data to integrations", PermissionCategory.INTEGRATION)
    SYNC = Permission("integrations:sync", "Synchronize data with integrations", PermissionCategory.INTEGRATION)
    ALL = Permission("integrations:*", "All integration permissions", PermissionCategory.INTEGRATION)


class AIPermissions:
    """Static class containing AI feature permissions."""
    USE_CHAT = Permission("ai:use_chat", "Use AI chat functionality", PermissionCategory.AI)
    USE_RECOMMENDATIONS = Permission("ai:use_recommendations", "Use AI recommendations", PermissionCategory.AI)
    CONFIGURE = Permission("ai:configure", "Configure AI settings", PermissionCategory.AI)
    ALL = Permission("ai:*", "All AI permissions", PermissionCategory.AI)


class PermissionRegistry:
    """Registry of all permissions in the system with lookup functionality."""
    
    def __init__(self):
        """Initialize the permission registry with all system permissions."""
        self._permissions: Dict[str, Permission] = {}
        self._register_all()
        logger.info("Permission registry initialized", extra={"additional_data": {"permission_count": len(self._permissions)}})
    
    def register(self, permission: Permission) -> None:
        """
        Register a permission in the registry.
        
        Args:
            permission: The permission to register
        """
        self._permissions[permission.name] = permission
        logger.debug(f"Registered permission: {permission.name}", extra={"additional_data": {"permission": permission.name}})
    
    def get(self, name: str) -> Optional[Permission]:
        """
        Get a permission by name.
        
        Args:
            name: The name of the permission to retrieve
            
        Returns:
            The permission if found, None otherwise
        """
        return self._permissions.get(name)
    
    def get_all(self) -> List[Permission]:
        """
        Get all registered permissions.
        
        Returns:
            List of all permissions
        """
        return list(self._permissions.values())
    
    def get_by_category(self, category: PermissionCategory) -> List[Permission]:
        """
        Get all permissions in a specific category.
        
        Args:
            category: The category to filter by
            
        Returns:
            List of permissions in the specified category
        """
        return [p for p in self._permissions.values() if p.category == category]
    
    def has_permission(self, permission_str: str) -> bool:
        """
        Check if the provided permission string is a valid permission.
        
        Args:
            permission_str: The permission string to check
            
        Returns:
            True if the permission exists, False otherwise
        """
        # Direct lookup
        if permission_str in self._permissions:
            return True
        
        # Check for wildcard matches
        for permission in self._permissions.values():
            if permission.matches(permission_str):
                return True
        
        return False
    
    def _register_all(self) -> None:
        """Register all system permissions."""
        # System permissions
        self.register(SystemPermissions.ADMIN)
        self.register(SystemPermissions.CONFIGURE)
        self.register(SystemPermissions.AUDIT_LOG_VIEW)
        self.register(SystemPermissions.ALL)
        
        # User permissions
        self.register(UserPermissions.CREATE)
        self.register(UserPermissions.READ)
        self.register(UserPermissions.UPDATE)
        self.register(UserPermissions.DELETE)
        self.register(UserPermissions.MANAGE_PERMISSIONS)
        self.register(UserPermissions.ALL)
        
        # Organization permissions
        self.register(OrganizationPermissions.CREATE)
        self.register(OrganizationPermissions.READ)
        self.register(OrganizationPermissions.UPDATE)
        self.register(OrganizationPermissions.DELETE)
        self.register(OrganizationPermissions.MANAGE_SETTINGS)
        self.register(OrganizationPermissions.MANAGE_PEER_GROUPS)
        self.register(OrganizationPermissions.ALL)
        
        # Rate permissions
        self.register(RatePermissions.CREATE)
        self.register(RatePermissions.READ)
        self.register(RatePermissions.UPDATE)
        self.register(RatePermissions.DELETE)
        self.register(RatePermissions.SUBMIT)
        self.register(RatePermissions.APPROVE)
        self.register(RatePermissions.REJECT)
        self.register(RatePermissions.COUNTER_PROPOSE)
        self.register(RatePermissions.EXPORT)
        self.register(RatePermissions.IMPORT)
        self.register(RatePermissions.MANAGE_RULES)
        self.register(RatePermissions.ALL)
        
        # Negotiation permissions
        self.register(NegotiationPermissions.CREATE)
        self.register(NegotiationPermissions.READ)
        self.register(NegotiationPermissions.UPDATE)
        self.register(NegotiationPermissions.DELETE)
        self.register(NegotiationPermissions.INITIATE)
        self.register(NegotiationPermissions.APPROVE)
        self.register(NegotiationPermissions.REJECT)
        self.register(NegotiationPermissions.COUNTER_PROPOSE)
        self.register(NegotiationPermissions.MANAGE_WORKFLOW)
        self.register(NegotiationPermissions.ALL)
        
        # Analytics permissions
        self.register(AnalyticsPermissions.VIEW)
        self.register(AnalyticsPermissions.CREATE_REPORTS)
        self.register(AnalyticsPermissions.EXPORT)
        self.register(AnalyticsPermissions.SHARE)
        self.register(AnalyticsPermissions.ALL)
        
        # Message permissions
        self.register(MessagePermissions.CREATE)
        self.register(MessagePermissions.READ)
        self.register(MessagePermissions.UPDATE)
        self.register(MessagePermissions.DELETE)
        self.register(MessagePermissions.ALL)
        
        # Document permissions
        self.register(DocumentPermissions.CREATE)
        self.register(DocumentPermissions.READ)
        self.register(DocumentPermissions.UPDATE)
        self.register(DocumentPermissions.DELETE)
        self.register(DocumentPermissions.SHARE)
        self.register(DocumentPermissions.ALL)
        
        # OCG permissions
        self.register(OCGPermissions.CREATE)
        self.register(OCGPermissions.READ)
        self.register(OCGPermissions.UPDATE)
        self.register(OCGPermissions.DELETE)
        self.register(OCGPermissions.PUBLISH)
        self.register(OCGPermissions.NEGOTIATE)
        self.register(OCGPermissions.SIGN)
        self.register(OCGPermissions.ALL)
        
        # Integration permissions
        self.register(IntegrationPermissions.CONFIGURE)
        self.register(IntegrationPermissions.IMPORT)
        self.register(IntegrationPermissions.EXPORT)
        self.register(IntegrationPermissions.SYNC)
        self.register(IntegrationPermissions.ALL)
        
        # AI permissions
        self.register(AIPermissions.USE_CHAT)
        self.register(AIPermissions.USE_RECOMMENDATIONS)
        self.register(AIPermissions.CONFIGURE)
        self.register(AIPermissions.ALL)


def get_permission_categories() -> Dict[str, str]:
    """
    Returns all available permission categories.
    
    Returns:
        Dictionary mapping category names to descriptions
    """
    return {
        PermissionCategory.SYSTEM.value: "System-wide permissions",
        PermissionCategory.USER.value: "User management permissions",
        PermissionCategory.ORGANIZATION.value: "Organization management permissions",
        PermissionCategory.RATE.value: "Rate management permissions",
        PermissionCategory.NEGOTIATION.value: "Negotiation workflow permissions",
        PermissionCategory.ANALYTICS.value: "Analytics and reporting permissions",
        PermissionCategory.MESSAGE.value: "Messaging permissions",
        PermissionCategory.DOCUMENT.value: "Document management permissions",
        PermissionCategory.OCG.value: "Outside Counsel Guidelines permissions",
        PermissionCategory.INTEGRATION.value: "Integration permissions",
        PermissionCategory.AI.value: "AI feature permissions"
    }


def get_all_permissions() -> List[Permission]:
    """
    Returns all available permissions in the system.
    
    Returns:
        List of all permission objects
    """
    registry = PermissionRegistry()
    return registry.get_all()


def get_permissions_by_category(category: PermissionCategory) -> List[Permission]:
    """
    Returns permissions filtered by category.
    
    Args:
        category: The category to filter by
        
    Returns:
        List of permissions in the category
    """
    registry = PermissionRegistry()
    return registry.get_by_category(category)


def get_system_permissions() -> List[Permission]:
    """
    Returns all system-level permissions.
    
    Returns:
        List of system permissions
    """
    return get_permissions_by_category(PermissionCategory.SYSTEM)


def get_user_permissions() -> List[Permission]:
    """
    Returns all user management permissions.
    
    Returns:
        List of user management permissions
    """
    return get_permissions_by_category(PermissionCategory.USER)


def get_organization_permissions() -> List[Permission]:
    """
    Returns all organization management permissions.
    
    Returns:
        List of organization management permissions
    """
    return get_permissions_by_category(PermissionCategory.ORGANIZATION)


def get_rate_permissions() -> List[Permission]:
    """
    Returns all rate management permissions.
    
    Returns:
        List of rate management permissions
    """
    return get_permissions_by_category(PermissionCategory.RATE)


def get_negotiation_permissions() -> List[Permission]:
    """
    Returns all negotiation workflow permissions.
    
    Returns:
        List of negotiation permissions
    """
    return get_permissions_by_category(PermissionCategory.NEGOTIATION)


def get_analytics_permissions() -> List[Permission]:
    """
    Returns all analytics and reporting permissions.
    
    Returns:
        List of analytics permissions
    """
    return get_permissions_by_category(PermissionCategory.ANALYTICS)


def get_integration_permissions() -> List[Permission]:
    """
    Returns all integration-related permissions.
    
    Returns:
        List of integration permissions
    """
    return get_permissions_by_category(PermissionCategory.INTEGRATION)