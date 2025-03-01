"""
Repository class for User model operations providing a data access layer for managing users
in the Justice Bid Rate Negotiation System. Handles CRUD operations, permissions management,
and organization-scoped user queries with proper validation and error handling.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import or_, and_, func, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..models.user import User, UserRole
from ..session import session_scope, get_db
from ...utils.logging import get_logger
from ...utils.validators import (
    validate_required, validate_email, validate_string, 
    validate_password, validate_enum_value
)

# Set up logger
logger = get_logger(__name__, 'repository')

class UserRepository:
    """
    Repository class that handles database operations for User entities, providing
    an abstraction layer over the data access logic.
    """
    
    def __init__(self, db_session):
        """
        Initialize a new UserRepository with a database session.
        
        Args:
            db_session (sqlalchemy.orm.Session): Database session
        """
        self._db = db_session
    
    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            user_id (uuid.UUID): The ID of the user to retrieve
            
        Returns:
            Optional[User]: User if found, None otherwise
        """
        try:
            return self._db.query(User).filter(
                User.id == user_id,
                User.is_deleted == False
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving user by ID {user_id}: {str(e)}")
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email address.
        
        Args:
            email (str): The email address of the user to retrieve
            
        Returns:
            Optional[User]: User if found, None otherwise
        """
        try:
            # Case-insensitive email search
            return self._db.query(User).filter(
                func.lower(User.email) == func.lower(email),
                User.is_deleted == False
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving user by email {email}: {str(e)}")
            return None
    
    def get_by_organization(self, organization_id: uuid.UUID, active_only: bool = True, 
                           limit: int = 100, offset: int = 0) -> List[User]:
        """
        Get all users belonging to an organization.
        
        Args:
            organization_id (uuid.UUID): The ID of the organization
            active_only (bool): If True, only return active users
            limit (int): Maximum number of users to return
            offset (int): Offset for pagination
            
        Returns:
            List[User]: List of users in the organization
        """
        try:
            query = self._db.query(User).filter(
                User.organization_id == organization_id,
                User.is_deleted == False
            )
            
            if active_only:
                query = query.filter(User.is_active == True)
            
            return query.order_by(User.name).limit(limit).offset(offset).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving users for organization {organization_id}: {str(e)}")
            return []
    
    def create(self, email: str, name: str, password: str, 
              organization_id: uuid.UUID, role: UserRole) -> User:
        """
        Create a new user.
        
        Args:
            email (str): User's email address
            name (str): User's name
            password (str): User's password
            organization_id (uuid.UUID): ID of the organization this user belongs to
            role (UserRole): User's role
            
        Returns:
            User: Newly created user
            
        Raises:
            ValueError: If validation fails or user with email already exists
        """
        try:
            # Validate required fields
            validate_required(email, "email")
            validate_required(name, "name")
            validate_required(password, "password")
            validate_required(organization_id, "organization_id")
            
            # Validate email format
            validate_email(email, "email")
            
            # Validate name
            validate_string(name, "name", min_length=2, max_length=255)
            
            # Validate password
            validate_password(password, "password")
            
            # Validate role
            validate_enum_value(role, UserRole, "role")
            
            # Check if user with email already exists
            existing_user = self.get_by_email(email)
            if existing_user:
                raise ValueError(f"User with email {email} already exists")
            
            # Create new user
            user = User(
                email=email,
                name=name,
                password=password,
                organization_id=organization_id,
                role=role
            )
            
            # Add to database and commit
            self._db.add(user)
            self._db.commit()
            
            logger.info(f"Created new user {user.id} with email {email} in organization {organization_id}")
            return user
            
        except ValueError as e:
            logger.warning(f"Validation error creating user: {str(e)}")
            self._db.rollback()
            raise
        except IntegrityError as e:
            logger.error(f"Integrity error creating user: {str(e)}")
            self._db.rollback()
            raise ValueError("Could not create user due to data integrity error")
        except SQLAlchemyError as e:
            logger.error(f"Database error creating user: {str(e)}")
            self._db.rollback()
            raise ValueError("Could not create user due to database error")
    
    def update(self, user_id: uuid.UUID, update_data: dict) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            user_id (uuid.UUID): ID of the user to update
            update_data (dict): Dictionary of fields to update
            
        Returns:
            Optional[User]: Updated user if successful, None if user not found
            
        Raises:
            ValueError: If validation fails or email already exists for another user
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return None
            
            # Process updateable fields
            if 'name' in update_data:
                validate_string(update_data['name'], "name", min_length=2, max_length=255)
                user.name = update_data['name']
            
            if 'role' in update_data:
                validate_enum_value(update_data['role'], UserRole, "role")
                user.role = update_data['role']
            
            if 'is_active' in update_data:
                user.is_active = bool(update_data['is_active'])
            
            # Handle email update (requires validation and duplicate check)
            if 'email' in update_data and update_data['email'] != user.email:
                validate_email(update_data['email'], "email")
                
                # Check if email is already in use by another user
                existing_user = self.get_by_email(update_data['email'])
                if existing_user and existing_user.id != user_id:
                    raise ValueError(f"Email {update_data['email']} is already in use by another user")
                
                user.email = update_data['email']
            
            # Handle password update
            if 'password' in update_data:
                validate_password(update_data['password'], "password")
                user.set_password(update_data['password'])
            
            # Process permissions if provided
            if 'permissions' in update_data and isinstance(update_data['permissions'], dict):
                user.permissions = update_data['permissions']
            
            # Process preferences if provided
            if 'preferences' in update_data and isinstance(update_data['preferences'], dict):
                user.preferences = update_data['preferences']
            
            # Commit changes
            self._db.commit()
            
            logger.info(f"Updated user {user_id}")
            return user
            
        except ValueError as e:
            logger.warning(f"Validation error updating user {user_id}: {str(e)}")
            self._db.rollback()
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error updating user {user_id}: {str(e)}")
            self._db.rollback()
            raise ValueError("Could not update user due to database error")
    
    def delete(self, user_id: uuid.UUID, deleted_by_id: Optional[uuid.UUID] = None) -> bool:
        """
        Delete a user (soft delete).
        
        Args:
            user_id (uuid.UUID): ID of the user to delete
            deleted_by_id (Optional[uuid.UUID]): ID of the user performing the deletion
            
        Returns:
            bool: True if successful, False if user not found
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            user.delete(deleted_by_id)
            self._db.commit()
            
            logger.info(f"Deleted user {user_id}" + 
                      (f" by {deleted_by_id}" if deleted_by_id else ""))
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def restore(self, user_id: uuid.UUID) -> bool:
        """
        Restore a soft-deleted user.
        
        Args:
            user_id (uuid.UUID): ID of the user to restore
            
        Returns:
            bool: True if successful, False if user not found
        """
        try:
            # Need to include deleted users in the query
            user = self._db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.restore()
            self._db.commit()
            
            logger.info(f"Restored user {user_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error restoring user {user_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.
        
        Args:
            email (str): User's email address
            password (str): User's password
            
        Returns:
            Optional[User]: User if authentication succeeds, None otherwise
        """
        try:
            user = self.get_by_email(email)
            if not user:
                logger.info(f"Authentication failed: no user found with email {email}")
                return None
            
            # Check if user is active
            if not user.is_active:
                logger.info(f"Authentication failed: user {email} is not active")
                return None
            
            # Verify password
            if not user.verify_password(password):
                logger.info(f"Authentication failed: invalid password for user {email}")
                return None
            
            # Update last login timestamp
            user.update_last_login()
            self._db.commit()
            
            logger.info(f"User {email} authenticated successfully")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Error during authentication for {email}: {str(e)}")
            self._db.rollback()
            return None
    
    def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            user_id (uuid.UUID): ID of the user
            current_password (str): Current password for verification
            new_password (str): New password to set
            
        Returns:
            bool: True if successful, False if user not found or current password is invalid
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            # Verify current password
            if not user.verify_password(current_password):
                logger.info(f"Password change failed: invalid current password for user {user_id}")
                return False
            
            # Validate new password
            validate_password(new_password, "new_password")
            
            # Set new password
            user.set_password(new_password)
            self._db.commit()
            
            logger.info(f"Password changed for user {user_id}")
            return True
            
        except ValueError as e:
            logger.warning(f"Validation error in password change for user {user_id}: {str(e)}")
            self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error changing password for user {user_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def reset_password(self, user_id: uuid.UUID, new_password: str) -> bool:
        """
        Reset a user's password (administrative function).
        
        Args:
            user_id (uuid.UUID): ID of the user
            new_password (str): New password to set
            
        Returns:
            bool: True if successful, False if user not found
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            # Validate new password
            validate_password(new_password, "new_password")
            
            # Set new password
            user.set_password(new_password)
            self._db.commit()
            
            logger.info(f"Password reset for user {user_id}")
            return True
            
        except ValueError as e:
            logger.warning(f"Validation error in password reset for user {user_id}: {str(e)}")
            self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error resetting password for user {user_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def update_role(self, user_id: uuid.UUID, new_role: UserRole) -> Optional[User]:
        """
        Update a user's role.
        
        Args:
            user_id (uuid.UUID): ID of the user
            new_role (UserRole): New role to assign
            
        Returns:
            Optional[User]: Updated user if successful, None if user not found
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return None
            
            # Validate role
            validate_enum_value(new_role, UserRole, "new_role")
            
            # Update role
            user.role = new_role
            self._db.commit()
            
            logger.info(f"Updated role to {new_role} for user {user_id}")
            return user
            
        except ValueError as e:
            logger.warning(f"Validation error updating role for user {user_id}: {str(e)}")
            self._db.rollback()
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error updating role for user {user_id}: {str(e)}")
            self._db.rollback()
            return None
    
    def add_permission(self, user_id: uuid.UUID, permission: str) -> bool:
        """
        Add a permission to a user.
        
        Args:
            user_id (uuid.UUID): ID of the user
            permission (str): Permission to add
            
        Returns:
            bool: True if successful, False if user not found or permission already exists
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            # Add permission
            result = user.add_permission(permission)
            
            if result:
                self._db.commit()
                logger.info(f"Added permission '{permission}' to user {user_id}")
            else:
                logger.info(f"Permission '{permission}' already exists for user {user_id}")
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error adding permission for user {user_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def remove_permission(self, user_id: uuid.UUID, permission: str) -> bool:
        """
        Remove a permission from a user.
        
        Args:
            user_id (uuid.UUID): ID of the user
            permission (str): Permission to remove
            
        Returns:
            bool: True if successful, False if user not found or permission doesn't exist
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            # Remove permission
            result = user.remove_permission(permission)
            
            if result:
                self._db.commit()
                logger.info(f"Removed permission '{permission}' from user {user_id}")
            else:
                logger.info(f"Permission '{permission}' not found for user {user_id}")
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error removing permission for user {user_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def has_permission(self, user_id: uuid.UUID, permission: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id (uuid.UUID): ID of the user
            permission (str): Permission to check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            return user.has_permission(permission)
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking permission for user {user_id}: {str(e)}")
            return False
    
    def set_mfa_enabled(self, user_id: uuid.UUID, enabled: bool, 
                        mfa_secret: Optional[str] = None) -> bool:
        """
        Enable or disable multi-factor authentication for a user.
        
        Args:
            user_id (uuid.UUID): ID of the user
            enabled (bool): Whether to enable MFA
            mfa_secret (Optional[str]): MFA secret key (required when enabling)
            
        Returns:
            bool: True if successful, False if user not found or operation fails
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            if enabled:
                # Validate that secret is provided when enabling MFA
                if not mfa_secret:
                    raise ValueError("MFA secret is required when enabling MFA")
                
                user.enable_mfa(mfa_secret)
                logger.info(f"Enabled MFA for user {user_id}")
            else:
                user.disable_mfa()
                logger.info(f"Disabled MFA for user {user_id}")
            
            self._db.commit()
            return True
            
        except ValueError as e:
            logger.warning(f"Validation error setting MFA for user {user_id}: {str(e)}")
            self._db.rollback()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error setting MFA for user {user_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def set_active_status(self, user_id: uuid.UUID, is_active: bool) -> bool:
        """
        Activate or deactivate a user.
        
        Args:
            user_id (uuid.UUID): ID of the user
            is_active (bool): Whether to activate or deactivate the user
            
        Returns:
            bool: True if successful, False if user not found
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            if is_active:
                user.activate()
                logger.info(f"Activated user {user_id}")
            else:
                user.deactivate()
                logger.info(f"Deactivated user {user_id}")
            
            self._db.commit()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error setting active status for user {user_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def search(self, query: str, organization_id: Optional[uuid.UUID] = None, 
              limit: int = 100, offset: int = 0) -> List[User]:
        """
        Search for users by name or email.
        
        Args:
            query (str): Search query
            organization_id (Optional[uuid.UUID]): Optional organization ID to scope the search
            limit (int): Maximum number of users to return
            offset (int): Offset for pagination
            
        Returns:
            List[User]: List of users matching the search criteria
        """
        try:
            # Build search query
            search_term = f"%{query}%"
            db_query = self._db.query(User).filter(
                or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term)
                ),
                User.is_active == True,
                User.is_deleted == False
            )
            
            # Filter by organization if provided
            if organization_id:
                db_query = db_query.filter(User.organization_id == organization_id)
            
            # Apply pagination and return results
            return db_query.order_by(User.name).limit(limit).offset(offset).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching users with query '{query}': {str(e)}")
            return []
    
    def get_users_by_role(self, role: UserRole, organization_id: Optional[uuid.UUID] = None,
                         limit: int = 100, offset: int = 0) -> List[User]:
        """
        Get all users with a specific role.
        
        Args:
            role (UserRole): Role to filter by
            organization_id (Optional[uuid.UUID]): Optional organization ID to scope the search
            limit (int): Maximum number of users to return
            offset (int): Offset for pagination
            
        Returns:
            List[User]: List of users with the specified role
        """
        try:
            # Build query
            db_query = self._db.query(User).filter(
                User.role == role,
                User.is_active == True,
                User.is_deleted == False
            )
            
            # Filter by organization if provided
            if organization_id:
                db_query = db_query.filter(User.organization_id == organization_id)
            
            # Apply pagination and return results
            return db_query.order_by(User.name).limit(limit).offset(offset).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting users by role {role}: {str(e)}")
            return []
    
    def count_by_organization(self, organization_id: uuid.UUID, active_only: bool = True) -> int:
        """
        Count the number of users in an organization.
        
        Args:
            organization_id (uuid.UUID): The ID of the organization
            active_only (bool): If True, only count active users
            
        Returns:
            int: Number of users in the organization
        """
        try:
            query = self._db.query(func.count(User.id)).filter(
                User.organization_id == organization_id,
                User.is_deleted == False
            )
            
            if active_only:
                query = query.filter(User.is_active == True)
            
            return query.scalar() or 0
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting users for organization {organization_id}: {str(e)}")
            return 0
    
    def set_preference(self, user_id: uuid.UUID, key: str, value: Any) -> bool:
        """
        Set a user preference value.
        
        Args:
            user_id (uuid.UUID): ID of the user
            key (str): Preference key
            value (Any): Preference value
            
        Returns:
            bool: True if successful, False if user not found
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            user.set_preference(key, value)
            self._db.commit()
            
            logger.info(f"Set preference '{key}' for user {user_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error setting preference for user {user_id}: {str(e)}")
            self._db.rollback()
            return False
    
    def get_preference(self, user_id: uuid.UUID, key: str, default: Any = None) -> Any:
        """
        Get a user preference value.
        
        Args:
            user_id (uuid.UUID): ID of the user
            key (str): Preference key
            default (Any): Default value if preference not found
            
        Returns:
            Any: Preference value or default if not found
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return default
            
            return user.get_preference(key, default)
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting preference for user {user_id}: {str(e)}")
            return default