"""
Provides password management functionality for the Justice Bid Rate Negotiation System,
including password validation, reset, history tracking, and policy enforcement.
This service implements secure password handling practices and supports the authentication framework.
"""

import uuid
from typing import Optional, Tuple

from ...utils.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    generate_password_reset_token,
    verify_password_reset_token,
)
from ...db.repositories.user_repository import UserRepository
from ...utils.constants import PASSWORD_MIN_LENGTH
from ...utils.email import send_template_email
from ...utils.logging import get_logger
from datetime import datetime

# Initialize logger
logger = get_logger(__name__)

# Constants for password reset and history
PASSWORD_RESET_EXPIRY_MINUTES = 30
PASSWORD_HISTORY_SIZE = 10
PASSWORD_MAX_AGE_DAYS = 90
PASSWORD_LOCK_ATTEMPTS = 5
PASSWORD_LOCK_MINUTES = 15


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validates a password against security policies

    Args:
        password: The password to validate

    Returns:
        (bool, str) - Success flag and error message if validation fails
    """
    # Call validate_password_strength from security utils
    success, error_message = validate_password_strength(password)
    # Return the validation result (success flag and any error message)
    return success, error_message


def check_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against the stored hash

    Args:
        plain_password: The plain text password
        hashed_password: The stored password hash

    Returns:
        True if password matches, False otherwise
    """
    # Call verify_password from security utils
    is_valid = verify_password(plain_password, hashed_password)
    # Return the verification result
    return is_valid


def create_password_hash(password: str) -> str:
    """
    Creates a secure hash of a password

    Args:
        password: The password to hash

    Returns:
        Hashed password
    """
    # Call hash_password from security utils
    hashed_password = hash_password(password)
    # Return the hashed password
    return hashed_password


def is_password_expired(password_changed_at: datetime) -> bool:
    """
    Checks if a user's password has expired

    Args:
        password_changed_at: Datetime when the password was last changed

    Returns:
        True if password is expired, False otherwise
    """
    # Get current datetime
    now = datetime.now()
    # Calculate the expiration threshold (current time minus PASSWORD_MAX_AGE_DAYS)
    expiration_threshold = now - datetime.timedelta(days=PASSWORD_MAX_AGE_DAYS)
    # Compare password_changed_at with the threshold
    is_expired = password_changed_at < expiration_threshold
    # Return True if password_changed_at is older than the threshold
    return is_expired


def check_password_history(new_password: str, password_history: list) -> bool:
    """
    Verifies a new password doesn't match recent password history

    Args:
        new_password: The new password to check
        password_history: List of historical password hashes

    Returns:
        True if password is not in history, False if it matches a recent password
    """
    # For each password hash in password_history
    for historical_hash in password_history:
        # Call check_password to compare new_password with the historical hash
        if check_password(new_password, historical_hash):
            # If any match is found, return False
            return False
    # If no matches found, return True
    return True


def update_password(user_id: uuid.UUID, new_password: str, user_repository: UserRepository) -> bool:
    """
    Updates a user's password with proper history tracking

    Args:
        user_id: ID of the user to update
        new_password: The new password to set
        user_repository: Repository for accessing user data

    Returns:
        True if successful, False otherwise
    """
    try:
        # Retrieve user from repository
        user = user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return False

        # Validate the new password using validate_password
        success, error_message = validate_password(new_password)
        if not success:
            logger.warning(f"New password validation failed: {error_message}")
            return False

        # If user has password_history, check against history using check_password_history
        if user.password_history:
            if not check_password_history(new_password, user.password_history):
                logger.warning("New password matches recent password history")
                return False
        else:
            user.password_history = []

        # Hash the new password using create_password_hash
        hashed_password = create_password_hash(new_password)

        # Add current password to history (limiting to PASSWORD_HISTORY_SIZE entries)
        user.password_history.insert(0, user.password_hash)
        user.password_history = user.password_history[:PASSWORD_HISTORY_SIZE]

        # Update user with new password hash, history, and current timestamp for password_changed_at
        user.password_hash = hashed_password
        user.password_changed_at = datetime.now()

        # Reset failed login attempts counter
        user.failed_login_attempts = 0
        user.account_locked = False
        user.account_unlock_time = None

        # Commit changes to the database
        user_repository._db.commit()

        logger.info(f"Password updated successfully for user: {user_id}")
        # Return True if update successful
        return True
    except Exception as e:
        logger.error(f"Error updating password for user {user_id}: {str(e)}")
        user_repository._db.rollback()
        return False


def change_password(user_id: uuid.UUID, current_password: str, new_password: str, user_repository: UserRepository) -> Tuple[bool, str]:
    """
    Changes a user's password after verifying the current password

    Args:
        user_id: ID of the user to update
        current_password: The user's current password
        new_password: The new password to set
        user_repository: Repository for accessing user data

    Returns:
        (bool, str) - Success flag and error message if any
    """
    try:
        # Retrieve user from repository
        user = user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return False, "User not found"

        # Verify current_password using check_password
        if not check_password(current_password, user.password_hash):
            logger.warning("Current password verification failed")
            return False, "Current password is incorrect"

        # Validate the new password using validate_password
        success, error_message = validate_password(new_password)
        if not success:
            logger.warning(f"New password validation failed: {error_message}")
            return False, error_message

        # Check new password against history using check_password_history
        if user.password_history and not check_password_history(new_password, user.password_history):
            logger.warning("New password matches recent password history")
            return False, "Password has been used recently"

        # Update password using update_password
        if not update_password(user_id, new_password, user_repository):
            logger.error("Password update failed")
            return False, "Password update failed"

        # Return (True, '') if successful
        return True, ""
    except Exception as e:
        logger.error(f"Error changing password for user {user_id}: {str(e)}")
        return False, "An unexpected error occurred"


def create_reset_token(user_id: uuid.UUID) -> str:
    """
    Creates a password reset token for a user

    Args:
        user_id: ID of the user requesting reset

    Returns:
        Password reset token
    """
    # Generate password reset token using generate_password_reset_token
    reset_token = generate_password_reset_token(user_id, expiry_minutes=PASSWORD_RESET_EXPIRY_MINUTES)
    # Return the generated token
    return reset_token


def verify_reset_token(token: str) -> Optional[uuid.UUID]:
    """
    Verifies a password reset token

    Args:
        token: The token to verify

    Returns:
        User ID if token is valid, None otherwise
    """
    # Verify token using verify_password_reset_token
    user_id = verify_password_reset_token(token)
    # Return the user ID if token is valid, None otherwise
    return user_id


def initiate_password_reset(email: str, user_repository: UserRepository) -> bool:
    """
    Initiates the password reset process for a user

    Args:
        email: Email address of the user requesting reset
        user_repository: Repository for accessing user data

    Returns:
        True if reset initiated, False if user not found
    """
    try:
        # Retrieve user by email from repository
        user = user_repository.get_by_email(email)
        if not user:
            logger.warning(f"No user found with email: {email}")
            return False

        # Generate reset token using create_reset_token
        reset_token = create_reset_token(user.id)

        # Create context for email template with token and user info
        context = {
            "user_name": user.name,
            "reset_url": f"/reset-password?token={reset_token}"  # TODO: Replace with actual reset URL
        }

        # Send password reset email using send_template_email
        send_template_email(
            to_email=user.email,
            subject="Password Reset Request",
            template_name="password_reset",
            context=context
        )

        logger.info(f"Password reset initiated for user with email: {email}")
        # Return True
        return True
    except Exception as e:
        logger.error(f"Error initiating password reset for email {email}: {str(e)}")
        return False


def complete_password_reset(token: str, new_password: str, user_repository: UserRepository) -> Tuple[bool, str]:
    """
    Completes the password reset process

    Args:
        token: Password reset token
        new_password: The new password to set
        user_repository: Repository for accessing user data

    Returns:
        (bool, str) - Success flag and error message if any
    """
    try:
        # Verify token using verify_reset_token
        user_id = verify_reset_token(token)
        if not user_id:
            logger.warning("Invalid or expired token")
            return False, "Invalid or expired token"

        # Validate the new password using validate_password
        success, error_message = validate_password(new_password)
        if not success:
            logger.warning(f"New password validation failed: {error_message}")
            return False, error_message

        # Update password using update_password
        if not update_password(user_id, new_password, user_repository):
            logger.error("Password update failed")
            return False, "Password update failed"

        logger.info("Password reset successful")
        # Return (True, 'Password reset successful')
        return True, "Password reset successful"
    except Exception as e:
        logger.error(f"Error completing password reset: {str(e)}")
        return False, "An unexpected error occurred"


def record_failed_login(user_id: uuid.UUID, user_repository: UserRepository) -> Tuple[bool, Optional[datetime]]:
    """
    Records a failed login attempt and handles account lockout

    Args:
        user_id: ID of the user attempting login
        user_repository: Repository for accessing user data

    Returns:
        (bool, datetime) - Locked status and unlock time if locked
    """
    try:
        # Retrieve user from repository
        user = user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return False, None

        # Increment failed login attempts counter
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

        # If attempts >= PASSWORD_LOCK_ATTEMPTS
        if user.failed_login_attempts >= PASSWORD_LOCK_ATTEMPTS:
            # Set account locked flag
            user.account_locked = True
            # Calculate unlock time (current time + PASSWORD_LOCK_MINUTES)
            unlock_time = datetime.now() + datetime.timedelta(minutes=PASSWORD_LOCK_MINUTES)
            user.account_unlock_time = unlock_time
            logger.warning(f"Account locked for user {user_id} until {unlock_time}")
            # Update user with locked status and unlock time
            user_repository._db.commit()
            # Return (True, unlock_time)
            return True, unlock_time
        else:
            # Update user with incremented attempts
            user_repository._db.commit()
            logger.info(f"Failed login attempt recorded for user {user_id}, attempts: {user.failed_login_attempts}")
            # Return (False, None)
            return False, None
    except Exception as e:
        logger.error(f"Error recording failed login for user {user_id}: {str(e)}")
        user_repository._db.rollback()
        return False, None


def clear_failed_logins(user_id: uuid.UUID, user_repository: UserRepository) -> bool:
    """
    Resets failed login counter after successful login

    Args:
        user_id: ID of the user logging in
        user_repository: Repository for accessing user data

    Returns:
        True if successful
    """
    try:
        # Retrieve user from repository
        user = user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return False

        # Reset failed login attempts counter to 0
        user.failed_login_attempts = 0
        # Clear any account lock status
        user.account_locked = False
        user.account_unlock_time = None

        # Update user with cleared status
        user_repository._db.commit()
        logger.info(f"Failed login attempts cleared for user {user_id}")
        # Return True if successful
        return True
    except Exception as e:
        logger.error(f"Error clearing failed logins for user {user_id}: {str(e)}")
        user_repository._db.rollback()
        return False


def check_account_lockout(user_id: uuid.UUID, user_repository: UserRepository) -> Tuple[bool, Optional[datetime]]:
    """
    Checks if a user account is currently locked out

    Args:
        user_id: ID of the user to check
        user_repository: Repository for accessing user data

    Returns:
        (bool, Optional[datetime]) - Locked status and unlock time if locked
    """
    try:
        # Retrieve user from repository
        user = user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return False, None

        # If user is locked
        if user.account_locked:
            # Get current time
            now = datetime.now()
            # If current time > unlock time
            if now > user.account_unlock_time:
                # Reset lock status and failed attempts
                user.account_locked = False
                user.account_unlock_time = None
                user.failed_login_attempts = 0
                # Update user and return (False, None)
                user_repository._db.commit()
                logger.info(f"Account unlocked for user {user_id}")
                return False, None
            # Else
            else:
                logger.warning(f"Account locked for user {user_id} until {user.account_unlock_time}")
                # Return (True, unlock_time)
                return True, user.account_unlock_time
        # Else
        else:
            # Return (False, None)
            return False, None
    except Exception as e:
        logger.error(f"Error checking account lockout for user {user_id}: {str(e)}")
        return False, None

def force_password_reset(user_id: uuid.UUID, user_repository: UserRepository) -> bool:
    """
    Forces a user to reset their password on next login

    Args:
        user_id: ID of the user to force reset
        user_repository: Repository for accessing user data

    Returns:
        True if successful
    """
    try:
        # Retrieve user from repository
        user = user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return False

        # Set password_reset_required flag to True
        user.password_reset_required = True

        # Update user in repository
        user_repository._db.commit()
        logger.info(f"Password reset forced for user {user_id}")
        # Return True if successful
        return True
    except Exception as e:
        logger.error(f"Error forcing password reset for user {user_id}: {str(e)}")
        user_repository._db.rollback()
        return False

class PasswordService:
    """
    Service class that encapsulates password management functionality
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the PasswordService with dependencies

        Args:
            user_repository: Repository for accessing user data
        """
        # Store user_repository as instance variable
        self._user_repository = user_repository

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """
        Validates a password against security policies

        Args:
            password: The password to validate

        Returns:
            (bool, str) - Success flag and error message
        """
        # Call the validate_password function
        return validate_password(password)

    def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Changes a user's password

        Args:
            user_id: ID of the user to update
            current_password: The user's current password
            new_password: The new password to set

        Returns:
            (bool, str) - Success flag and error message
        """
        # Call the change_password function with user_repository
        return change_password(user_id, current_password, new_password, self._user_repository)

    def initiate_password_reset(self, email: str) -> bool:
        """
        Initiates the password reset process

        Args:
            email: Email address of the user requesting reset

        Returns:
            True if reset initiated, False if user not found
        """
        # Call the initiate_password_reset function with user_repository
        return initiate_password_reset(email, self._user_repository)

    def complete_password_reset(self, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Completes the password reset process

        Args:
            token: Password reset token
            new_password: The new password to set

        Returns:
            (bool, str) - Success flag and error message
        """
        # Call the complete_password_reset function with user_repository
        return complete_password_reset(token, new_password, self._user_repository)

    def check_password_expired(self, user_id: uuid.UUID) -> bool:
        """
        Checks if a user's password has expired

        Args:
            user_id: ID of the user to check

        Returns:
            True if password is expired, False otherwise
        """
        # Retrieve user from repository
        user = self._user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return False

        # Call is_password_expired with user's password_changed_at
        return is_password_expired(user.password_changed_at)

    def record_failed_login(self, user_id: uuid.UUID) -> Tuple[bool, Optional[datetime]]:
        """
        Records a failed login attempt

        Args:
            user_id: ID of the user attempting login

        Returns:
            (bool, Optional[datetime]) - Locked status and unlock time
        """
        # Call the record_failed_login function with user_repository
        return record_failed_login(user_id, self._user_repository)

    def clear_failed_logins(self, user_id: uuid.UUID) -> bool:
        """
        Resets failed login counter

        Args:
            user_id: ID of the user logging in

        Returns:
            True if successful
        """
        # Call the clear_failed_logins function with user_repository
        return clear_failed_logins(user_id, self._user_repository)

    def check_account_lockout(self, user_id: uuid.UUID) -> Tuple[bool, Optional[datetime]]:
        """
        Checks if an account is locked out

        Args:
            user_id: ID of the user to check

        Returns:
            (bool, Optional[datetime]) - Locked status and unlock time
        """
        # Call the check_account_lockout function with user_repository
        return check_account_lockout(user_id, self._user_repository)

    def force_password_reset(self, user_id: uuid.UUID) -> bool:
        """
        Forces a user to reset their password on next login

        Args:
            user_id: ID of the user to force reset

        Returns:
            True if successful
        """
        # Call the force_password_reset function with user_repository
        return force_password_reset(user_id, self._user_repository)

# Export functions for use in other modules
def validate_password(password: str) -> Tuple[bool, str]:
    return validate_password_strength(password)

def check_password(plain_password: str, hashed_password: str) -> bool:
    return verify_password(plain_password, hashed_password)

def create_password_hash(password: str) -> str:
    return hash_password(password)

def is_password_expired(password_changed_at: datetime) -> bool:
    return is_password_expired(password_changed_at)

def initiate_password_reset(email: str, user_repository: UserRepository) -> bool:
    return initiate_password_reset(email, user_repository)

def complete_password_reset(token: str, new_password: str, user_repository: UserRepository) -> Tuple[bool, str]:
    return complete_password_reset(token, new_password, user_repository)