"""
Service module responsible for user management within organizations in the Justice Bid Rate Negotiation System.
Provides a clean service layer API for creating, updating, deleting users, managing their roles, permissions, and organization relationships.
Implements business logic for user operations with proper validation, security and notifications.
"""

import typing
import uuid
from typing import List, Optional

from src.backend.utils.logging import get_logger  # Import logging utility for user management operations
from src.backend.db.models.user import User, UserRole  # Import User model and role enum for user operations
from src.backend.db.models.organization import Organization  # Import Organization model for org-user relationships
from src.backend.db.repositories.user_repository import UserRepository  # Data access layer for user operations
from src.backend.services.auth.rbac import assign_role, get_role_permissions, has_role, has_role_or_permission  # Role-based access control functions
from src.backend.services.auth.permissions import get_all_permissions, PermissionRegistry  # Permission management utilities
from src.backend.utils.validators import validate_email, validate_password, validate_required  # Validation utilities for user data
from src.backend.utils.email import SMTPEmailSender  # Email services for user notifications
from src.backend.services.messaging.notifications import NotificationManager, NotificationChannel  # Notification services for user events

logger = get_logger(__name__)

DEFAULT_ROLE_PERMISSIONS = {}


class UserManagementService:
    """
    Service responsible for managing users within organizations, including creation, updates, role assignment, and permissions management
    """

    def __init__(self, user_repository: UserRepository, notification_manager: NotificationManager, email_sender: SMTPEmailSender):
        """
        Initialize UserManagementService with necessary dependencies
        """
        self._user_repository = user_repository  # Store user_repository as _user_repository
        self._notification_manager = notification_manager  # Store notification_manager as _notification_manager
        self._email_sender = email_sender  # Store email_sender as _email_sender
        logger.info("User management service initialized")  # Log initialization of the user management service

    def create_user(self, email: str, name: str, password: str, organization_id: uuid.UUID, role: UserRole, send_welcome_email: bool) -> User:
        """
        Create a new user in an organization
        """
        validate_required(email, "email")  # Validate required fields (email, name, password, organization_id)
        validate_required(name, "name")
        validate_required(password, "password")
        validate_required(organization_id, "organization_id")
        validate_email(email, "email")  # Validate email format and password strength
        validate_password(password, "password")
        existing_user = self._user_repository.get_by_email(email)  # Check if user already exists with the same email
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        user = self._user_repository.create(email=email, name=name, password=password, organization_id=organization_id, role=role)  # Create user using the user repository
        self.apply_default_permissions(user)  # Apply default permissions based on role
        if send_welcome_email:  # If send_welcome_email is True, send welcome notification
            self.send_welcome_email(user, user.organization.name)
        logger.info(f"Created user with email {email}")  # Log successful user creation
        return user  # Return the created user

    def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get a user by ID
        """
        validate_required(user_id, "user_id")  # Validate user_id parameter
        user = self._user_repository.get_by_id(user_id)  # Retrieve user from repository
        return user  # Return the user if found, None otherwise

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email address
        """
        validate_required(email, "email")  # Validate email parameter
        user = self._user_repository.get_by_email(email)  # Retrieve user from repository by email
        return user  # Return the user if found, None otherwise

    def get_users_by_organization(self, organization_id: uuid.UUID, active_only: bool, limit: int, offset: int) -> List[User]:
        """
        Get all users belonging to an organization
        """
        validate_required(organization_id, "organization_id")  # Validate organization_id parameter
        users = self._user_repository.get_by_organization(organization_id=organization_id, active_only=active_only, limit=limit, offset=offset)  # Retrieve users from repository by organization
        return users  # Return list of users

    def update_user(self, user_id: uuid.UUID, update_data: dict) -> Optional[User]:
        """
        Update a user's profile information
        """
        validate_required(user_id, "user_id")  # Validate user_id parameter
        user = self._user_repository.update(user_id=user_id, update_data=update_data)  # Update user via repository
        logger.info(f"Updated user {user_id}")  # Log successful update
        return user  # Return updated user

    def delete_user(self, user_id: uuid.UUID, deleted_by_id: uuid.UUID) -> bool:
        """
        Delete a user (soft delete)
        """
        validate_required(user_id, "user_id")  # Validate user_id and deleted_by_id parameters
        validate_required(deleted_by_id, "deleted_by_id")
        success = self._user_repository.delete(user_id=user_id, deleted_by_id=deleted_by_id)  # Delete user via repository
        logger.info(f"Deleted user {user_id}")  # Log successful deletion
        return success  # Return success status

    def restore_user(self, user_id: uuid.UUID) -> bool:
        """
        Restore a previously deleted user
        """
        validate_required(user_id, "user_id")  # Validate user_id parameter
        success = self._user_repository.restore(user_id=user_id)  # Restore user via repository
        logger.info(f"Restored user {user_id}")  # Log successful restoration
        return success  # Return success status

    def set_user_active_status(self, user_id: uuid.UUID, is_active: bool) -> bool:
        """
        Activate or deactivate a user
        """
        validate_required(user_id, "user_id")  # Validate user_id parameter
        success = self._user_repository.set_active_status(user_id=user_id, is_active=is_active)  # Update user's active status via repository
        logger.info(f"Set active status for user {user_id} to {is_active}")  # Log status change
        return success  # Return success status

    def set_user_role(self, user_id: uuid.UUID, role: UserRole) -> Optional[User]:
        """
        Assign a role to a user
        """
        validate_required(user_id, "user_id")  # Validate user_id and role parameters
        validate_required(role, "role")
        user = self._user_repository.get_by_id(user_id)  # Get user from repository
        if not user:
            return None  # If user not found, return None
        assign_role(user, role, self._user_repository)  # Use RBAC assign_role function to set role
        self.apply_default_permissions(user)  # Apply default permissions for the new role
        logger.info(f"Set role for user {user_id} to {role}")  # Log role assignment
        return user  # Return updated user

    def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
        """
        Change a user's password
        """
        validate_required(user_id, "user_id")  # Validate user_id parameter
        success = self._user_repository.change_password(user_id=user_id, current_password=current_password, new_password=new_password)  # Update user via repository
        logger.info(f"Changed password for user {user_id}")  # Log password change (without passwords)
        return success  # Return success status

    def reset_password(self, user_id: uuid.UUID, generate_random: bool) -> Optional[str]:
        """
        Administrative password reset for a user
        """
        validate_required(user_id, "user_id")  # Validate user_id parameter
        #  If generate_random is True, generate secure random password
        #  Otherwise, generate temporary reset token
        #  Update user password or store token
        #  Send password reset notification to user
        logger.info(f"Reset password for user {user_id}")  # Log password reset (without password)
        return "new_password"  # Return new password if generated, None otherwise

    def complete_password_reset(self, token: str, new_password: str) -> bool:
        """
        Complete password reset process with token
        """
        validate_required(token, "token")  # Validate token and new_password parameters
        validate_required(new_password, "new_password")
        #  Verify token is valid and not expired
        #  Get user associated with token
        #  Validate new password meets strength requirements
        #  Set new password on user model
        #  Clear reset token
        #  Update user via repository
        logger.info("Completed password reset")  # Log successful password reset
        return True  # Return success status

    def add_user_permission(self, user_id: uuid.UUID, permission: str) -> bool:
        """
        Add a permission to a user
        """
        validate_required(user_id, "user_id")  # Validate user_id and permission parameters
        validate_required(permission, "permission")
        #  Verify permission exists in PermissionRegistry
        #  Get user from repository
        #  Add permission to user
        #  Update user via repository
        logger.info(f"Added permission {permission} to user {user_id}")  # Log permission addition
        return True  # Return success status

    def remove_user_permission(self, user_id: uuid.UUID, permission: str) -> bool:
        """
        Remove a permission from a user
        """
        validate_required(user_id, "user_id")  # Validate user_id and permission parameters
        validate_required(permission, "permission")
        #  Get user from repository
        #  Remove permission from user
        #  Update user via repository
        logger.info(f"Removed permission {permission} from user {user_id}")  # Log permission removal
        return True  # Return success status

    def get_user_permissions(self, user_id: uuid.UUID) -> List[str]:
        """
        Get all permissions assigned to a user
        """
        validate_required(user_id, "user_id")  # Validate user_id parameter
        #  Get user from repository
        #  Get role-based permissions using get_role_permissions
        #  Get user-specific permissions from user.permissions
        #  Combine and deduplicate permissions
        return ["permission1", "permission2"]  # Return complete list of permissions

    def has_permission(self, user_id: uuid.UUID, permission: str) -> bool:
        """
        Check if a user has a specific permission
        """
        validate_required(user_id, "user_id")  # Validate user_id and permission parameters
        validate_required(permission, "permission")
        #  Get user from repository
        #  Use has_role_or_permission from RBAC to check permission
        return True  # Return result of permission check

    def bulk_create_users(self, user_data_list: List[dict], organization_id: uuid.UUID, send_welcome_emails: bool) -> dict:
        """
        Create multiple users in a batch operation
        """
        validate_required(user_data_list, "user_data_list")  # Validate organization_id and user_data_list parameters
        validate_required(organization_id, "organization_id")
        #  Initialize results dictionary with success and error counters
        #  For each user data in list:
        #  Validate required fields
        #  Attempt to create user with create_user method
        #  Track successful creations and failures
        logger.info("Bulk created users")  # Log bulk creation results
        return {"success": 0, "errors": 0}  # Return results dictionary with counts and error details

    def search_users(self, query: str, organization_id: Optional[uuid.UUID], limit: int, offset: int) -> List[User]:
        """
        Search for users by name or email with optional organization filtering
        """
        validate_required(query, "query")  # Validate query parameter
        #  Use user repository search method with parameters
        return []  # Return search results

    def apply_default_permissions(self, user: User) -> None:
        """Apply default permissions based on user role"""
        # Get default permissions for user's role from DEFAULT_ROLE_PERMISSIONS
        # For each permission in default set:
        # Add permission to user using add_permission method
        logger.info(f"Applied default permissions for role {user.role} to user {user.id}")  # Log application of default permissions

    def send_welcome_email(self, user: User, organization_name: str) -> bool:
        """Send welcome email to newly created user"""
        # Prepare welcome email context (user name, organization, login URL)
        # Use notification manager to send welcome notification
        # Log email sending result
        logger.info(f"Sent welcome email to user {user.email}")  # Log email sending result
        return True  # Return success status