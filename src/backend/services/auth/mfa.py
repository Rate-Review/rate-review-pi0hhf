"""
Service for handling Multi-Factor Authentication (MFA) including TOTP and Email OTP methods, and MFA management flows.
"""

import logging
import pyotp  # version 2.8.0
import qrcode  # version 7.4.2
import io
import base64
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..db.models.user import User
from ..utils.email import send_email
from ..utils.security import hash_data, verify_hash
from ..utils.constants import MFA_EMAIL_EXPIRY_MINUTES

# Configure logger
logger = logging.getLogger(__name__)


def generate_totp_secret() -> str:
    """
    Generates a new TOTP secret for a user

    Returns:
        str: Base32 encoded secret key
    """
    return pyotp.random_base32()


def generate_totp_qr_code(secret: str, user_email: str, issuer_name: str) -> str:
    """
    Generates a QR code for TOTP setup in authenticator apps

    Args:
        secret: The TOTP secret key
        user_email: User's email address for identification
        issuer_name: Name of the issuer for the authenticator app

    Returns:
        str: Base64 encoded QR code image
    """
    # Create a TOTP provisioning URI
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(user_email, issuer_name=issuer_name)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer)
    img_str = base64.b64encode(buffer.getvalue()).decode('ascii')
    
    return f"data:image/png;base64,{img_str}"


def verify_totp_code(secret: str, code: str) -> bool:
    """
    Verifies a TOTP code provided by the user

    Args:
        secret: The TOTP secret key
        code: The code provided by the user

    Returns:
        bool: True if code is valid, False otherwise
    """
    if not secret or not code:
        return False
    
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def generate_email_otp(length: int = 6) -> str:
    """
    Generates a random OTP code for email-based MFA

    Args:
        length: Length of the OTP code (default: 6)

    Returns:
        str: Random OTP code
    """
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def send_otp_email(email: str, otp_code: str) -> bool:
    """
    Sends an email with OTP code to the user

    Args:
        email: Recipient email address
        otp_code: The OTP code to send

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "Your Justice Bid Verification Code"
    body = f"""
    <html>
    <body>
        <h2>Justice Bid Verification Code</h2>
        <p>Your verification code is: <strong>{otp_code}</strong></p>
        <p>This code will expire in {MFA_EMAIL_EXPIRY_MINUTES} minutes.</p>
        <p>If you did not request this code, please ignore this email.</p>
    </body>
    </html>
    """
    
    return send_email(
        to_email=email,
        subject=subject,
        body=body,
        html=True
    )


def store_email_otp(db_session: Session, user: User, otp_code: str) -> datetime:
    """
    Stores a hashed email OTP code in the database

    Args:
        db_session: Database session
        user: User object
        otp_code: The OTP code to store

    Returns:
        datetime: Expiration timestamp for the OTP
    """
    # Hash the OTP code
    hashed_otp = hash_data(otp_code)
    
    # Calculate expiration time
    expiration = datetime.utcnow() + timedelta(minutes=MFA_EMAIL_EXPIRY_MINUTES)
    
    # Store in user's preferences
    if user.preferences is None:
        user.preferences = {}
    
    if 'mfa' not in user.preferences:
        user.preferences['mfa'] = {}
    
    user.preferences['mfa']['email_otp_hash'] = hashed_otp
    user.preferences['mfa']['email_otp_expires'] = expiration.isoformat()
    
    # Commit the changes
    db_session.commit()
    
    return expiration


def verify_email_otp(db_session: Session, user: User, otp_code: str) -> bool:
    """
    Verifies an email OTP code provided by the user

    Args:
        db_session: Database session
        user: User object
        otp_code: The OTP code to verify

    Returns:
        bool: True if code is valid and not expired, False otherwise
    """
    # Check if user has mfa preferences with email OTP information
    if (user.preferences is None or 'mfa' not in user.preferences or 
            'email_otp_hash' not in user.preferences['mfa']):
        logger.warning(f"No email OTP hash found for user {user.id}")
        return False
    
    # Get the stored hash and expiration
    stored_hash = user.preferences['mfa'].get('email_otp_hash')
    expiration_str = user.preferences['mfa'].get('email_otp_expires')
    
    if not stored_hash or not expiration_str:
        logger.warning(f"Missing email OTP data for user {user.id}")
        return False
    
    # Parse expiration timestamp
    try:
        expiration = datetime.fromisoformat(expiration_str)
    except ValueError:
        logger.error(f"Invalid expiration timestamp format for user {user.id}")
        return False
    
    # Check if expired
    if datetime.utcnow() > expiration:
        logger.info(f"Email OTP expired for user {user.id}")
        return False
    
    # Verify the OTP code
    is_valid = verify_hash(otp_code, stored_hash)
    
    # Clear the OTP data if valid (one-time use)
    if is_valid:
        if 'email_otp_hash' in user.preferences['mfa']:
            del user.preferences['mfa']['email_otp_hash']
        if 'email_otp_expires' in user.preferences['mfa']:
            del user.preferences['mfa']['email_otp_expires']
        db_session.commit()
    
    return is_valid


def is_mfa_required(user: User) -> bool:
    """
    Determines if MFA is required for a user based on their role and organization settings

    Args:
        user: User object

    Returns:
        bool: True if MFA is required, False otherwise
    """
    # Check if user has an administrative role
    if user.is_administrator():
        return True
    
    # Check if user has approval authority
    if user.role == 'approver' or user.has_permission('approve_rates'):
        return True
    
    # Check if user's organization requires MFA for all users
    # This assumes organization has this setting stored in preferences
    if (hasattr(user.organization, 'preferences') and 
            user.organization.preferences and 
            user.organization.preferences.get('requires_mfa')):
        return True
    
    return False


def enable_totp_mfa(db_session: Session, user: User, secret: str, verification_code: str) -> bool:
    """
    Enables TOTP-based MFA for a user

    Args:
        db_session: Database session
        user: User object
        secret: TOTP secret key
        verification_code: Code provided by the user to verify setup

    Returns:
        bool: True if MFA was enabled successfully, False otherwise
    """
    # Verify the code to ensure the user has set up their authenticator correctly
    if not verify_totp_code(secret, verification_code):
        logger.warning(f"Failed to verify TOTP code during MFA setup for user {user.id}")
        return False
    
    # Store the secret and update MFA settings
    user.mfa_secret = secret
    
    # Store method in preferences
    if user.preferences is None:
        user.preferences = {}
    if 'mfa' not in user.preferences:
        user.preferences['mfa'] = {}
    
    user.preferences['mfa']['method'] = 'totp'
    user.mfa_enabled = True
    
    # Commit the changes
    db_session.commit()
    
    logger.info(f"TOTP MFA enabled for user {user.id}")
    return True


def enable_email_mfa(db_session: Session, user: User) -> bool:
    """
    Enables email-based MFA for a user

    Args:
        db_session: Database session
        user: User object

    Returns:
        bool: True if MFA setup was initiated successfully, False otherwise
    """
    # Generate OTP code
    otp_code = generate_email_otp()
    
    # Send OTP email
    email_sent = send_otp_email(user.email, otp_code)
    if not email_sent:
        logger.error(f"Failed to send OTP email to user {user.id}")
        return False
    
    # Store OTP in database
    store_email_otp(db_session, user, otp_code)
    
    logger.info(f"Email OTP sent for MFA setup to user {user.id}")
    return True


def confirm_email_mfa(db_session: Session, user: User, otp_code: str) -> bool:
    """
    Confirms email-based MFA setup using the provided OTP code

    Args:
        db_session: Database session
        user: User object
        otp_code: The OTP code to verify

    Returns:
        bool: True if MFA was confirmed successfully, False otherwise
    """
    # Verify the OTP code
    if not verify_email_otp(db_session, user, otp_code):
        logger.warning(f"Failed to verify email OTP during MFA setup for user {user.id}")
        return False
    
    # Update MFA settings
    if user.preferences is None:
        user.preferences = {}
    if 'mfa' not in user.preferences:
        user.preferences['mfa'] = {}
    
    user.preferences['mfa']['method'] = 'email'
    user.mfa_enabled = True
    
    # Commit the changes
    db_session.commit()
    
    logger.info(f"Email MFA enabled for user {user.id}")
    return True


def disable_mfa(db_session: Session, user: User) -> bool:
    """
    Disables MFA for a user

    Args:
        db_session: Database session
        user: User object

    Returns:
        bool: True if MFA was disabled successfully, False otherwise
    """
    # Check if MFA is required for this user
    if is_mfa_required(user):
        logger.warning(f"Attempted to disable required MFA for user {user.id}")
        return False
    
    # Clear MFA settings
    user.mfa_secret = None
    
    # Clear method from preferences
    if user.preferences and 'mfa' in user.preferences:
        if 'method' in user.preferences['mfa']:
            del user.preferences['mfa']['method']
    
    user.mfa_enabled = False
    
    # Commit the changes
    db_session.commit()
    
    logger.info(f"MFA disabled for user {user.id}")
    return True


def change_mfa_method(db_session: Session, user: User, new_method: str) -> dict:
    """
    Changes the MFA method for a user

    Args:
        db_session: Database session
        user: User object
        new_method: The new MFA method ('totp' or 'email')

    Returns:
        Dict[str, Any]: Result of initiating the change process
    """
    if new_method not in ['totp', 'email']:
        return {'success': False, 'message': 'Invalid MFA method'}
    
    if new_method == 'totp':
        # Generate a new TOTP secret and QR code
        secret = generate_totp_secret()
        qr_code = generate_totp_qr_code(secret, user.email, "Justice Bid")
        
        # Store temporarily (will be confirmed with verification code)
        if user.preferences is None:
            user.preferences = {}
        if 'mfa' not in user.preferences:
            user.preferences['mfa'] = {}
        
        user.preferences['mfa']['temp_secret'] = secret
        db_session.commit()
        
        return {
            'success': True,
            'method': 'totp',
            'secret': secret,
            'qr_code': qr_code,
            'message': 'Scan the QR code with your authenticator app and enter the verification code'
        }
    
    elif new_method == 'email':
        # Initiate email OTP verification
        success = enable_email_mfa(db_session, user)
        
        return {
            'success': success,
            'method': 'email',
            'message': 'A verification code has been sent to your email address'
        }


def initiate_mfa_verification(db_session: Session, user: User) -> dict:
    """
    Initiates MFA verification based on the user's configured method

    Args:
        db_session: Database session
        user: User object

    Returns:
        Dict[str, Any]: Information needed for the verification process
    """
    if not user.mfa_enabled:
        return {
            'success': False,
            'message': 'MFA is not enabled for this user'
        }
    
    # Get MFA method from preferences
    mfa_method = None
    if user.preferences and 'mfa' in user.preferences:
        mfa_method = user.preferences['mfa'].get('method')
    
    if mfa_method == 'totp':
        return {
            'success': True,
            'method': 'totp',
            'message': 'Please enter the code from your authenticator app'
        }
    
    elif mfa_method == 'email':
        # Generate and send OTP
        otp_code = generate_email_otp()
        email_sent = send_otp_email(user.email, otp_code)
        
        if not email_sent:
            logger.error(f"Failed to send OTP email to user {user.id}")
            return {
                'success': False,
                'message': 'Failed to send verification code'
            }
        
        # Store OTP
        store_email_otp(db_session, user, otp_code)
        
        return {
            'success': True,
            'method': 'email',
            'message': 'A verification code has been sent to your email address'
        }
    
    else:
        logger.error(f"Unknown or missing MFA method for user {user.id}")
        return {
            'success': False,
            'message': 'Unknown MFA method configured'
        }


def complete_mfa_verification(db_session: Session, user: User, code: str) -> bool:
    """
    Completes MFA verification using the provided code

    Args:
        db_session: Database session
        user: User object
        code: Verification code provided by the user

    Returns:
        bool: True if verification was successful, False otherwise
    """
    if not user.mfa_enabled:
        logger.warning(f"MFA verification attempted for user {user.id} but MFA is not enabled")
        return False
    
    # Get MFA method from preferences
    mfa_method = None
    if user.preferences and 'mfa' in user.preferences:
        mfa_method = user.preferences['mfa'].get('method')
    
    if mfa_method == 'totp':
        # Verify TOTP code
        return verify_totp_code(user.mfa_secret, code)
    
    elif mfa_method == 'email':
        # Verify email OTP
        return verify_email_otp(db_session, user, code)
    
    else:
        logger.error(f"Unknown or missing MFA method for user {user.id}")
        return False


def initiate_recovery(db_session: Session, user: User) -> dict:
    """
    Initiates MFA recovery process for a user who lost their MFA device

    Args:
        db_session: Database session
        user: User object

    Returns:
        Dict[str, Any]: Information about the recovery process
    """
    # Generate a recovery token
    recovery_token = secrets.token_urlsafe(32)
    
    # Hash the token for storage
    hashed_token = hash_data(recovery_token)
    
    # Set expiration (24 hours)
    expiration = datetime.utcnow() + timedelta(hours=24)
    
    # Store in user's preferences
    if user.preferences is None:
        user.preferences = {}
    if 'mfa' not in user.preferences:
        user.preferences['mfa'] = {}
    
    user.preferences['mfa']['recovery_token_hash'] = hashed_token
    user.preferences['mfa']['recovery_token_expires'] = expiration.isoformat()
    
    # Commit changes
    db_session.commit()
    
    # Send recovery email
    subject = "Justice Bid MFA Recovery"
    body = f"""
    <html>
    <body>
        <h2>Justice Bid MFA Recovery</h2>
        <p>You've requested to recover your multi-factor authentication settings.</p>
        <p>Your recovery token is: <strong>{recovery_token}</strong></p>
        <p>This token will expire in 24 hours.</p>
        <p>If you did not request this recovery, please contact support immediately.</p>
    </body>
    </html>
    """
    
    email_sent = send_email(
        to_email=user.email,
        subject=subject,
        body=body,
        html=True
    )
    
    if not email_sent:
        logger.error(f"Failed to send MFA recovery email to user {user.id}")
        return {
            'success': False,
            'message': 'Failed to send recovery instructions'
        }
    
    return {
        'success': True,
        'message': 'Recovery instructions have been sent to your email address'
    }


def complete_recovery(db_session: Session, user: User, recovery_token: str) -> dict:
    """
    Completes MFA recovery process using the provided recovery token

    Args:
        db_session: Database session
        user: User object
        recovery_token: Recovery token provided by the user

    Returns:
        Dict[str, Any]: Result of the recovery process
    """
    # Check if user has recovery token data in preferences
    if (user.preferences is None or 'mfa' not in user.preferences or 
            'recovery_token_hash' not in user.preferences['mfa']):
        logger.warning(f"No recovery token found for user {user.id}")
        return {
            'success': False,
            'message': 'Invalid or expired recovery token'
        }
    
    # Get the stored hash and expiration
    stored_hash = user.preferences['mfa'].get('recovery_token_hash')
    expiration_str = user.preferences['mfa'].get('recovery_token_expires')
    
    if not stored_hash or not expiration_str:
        logger.warning(f"Missing recovery token data for user {user.id}")
        return {
            'success': False,
            'message': 'Invalid or expired recovery token'
        }
    
    # Parse expiration timestamp
    try:
        expiration = datetime.fromisoformat(expiration_str)
    except ValueError:
        logger.error(f"Invalid expiration timestamp format for user {user.id}")
        return {
            'success': False,
            'message': 'Invalid or expired recovery token'
        }
    
    # Check if expired
    if datetime.utcnow() > expiration:
        logger.info(f"Recovery token expired for user {user.id}")
        return {
            'success': False,
            'message': 'Recovery token has expired'
        }
    
    # Verify the token
    is_valid = verify_hash(recovery_token, stored_hash)
    
    if not is_valid:
        logger.warning(f"Invalid recovery token provided for user {user.id}")
        return {
            'success': False,
            'message': 'Invalid recovery token'
        }
    
    # Reset MFA settings
    user.mfa_secret = None
    user.mfa_enabled = False
    
    # Clean up recovery data
    if 'recovery_token_hash' in user.preferences['mfa']:
        del user.preferences['mfa']['recovery_token_hash']
    if 'recovery_token_expires' in user.preferences['mfa']:
        del user.preferences['mfa']['recovery_token_expires']
    if 'method' in user.preferences['mfa']:
        del user.preferences['mfa']['method']
    
    # Commit changes
    db_session.commit()
    
    logger.info(f"MFA reset completed for user {user.id} via recovery process")
    
    return {
        'success': True,
        'message': 'MFA has been reset successfully. You can now set up MFA again.'
    }


def admin_reset_mfa(db_session: Session, admin_user: User, target_user: User) -> bool:
    """
    Allows an administrator to reset MFA for a user

    Args:
        db_session: Database session
        admin_user: Administrator user performing the reset
        target_user: User whose MFA is being reset

    Returns:
        bool: True if reset was successful, False otherwise
    """
    # Verify admin has permission
    if not admin_user.is_administrator():
        logger.warning(f"Non-admin user {admin_user.id} attempted to reset MFA for user {target_user.id}")
        return False
    
    # Reset MFA settings
    target_user.mfa_secret = None
    target_user.mfa_enabled = False
    
    # Clean up MFA data in preferences
    if target_user.preferences and 'mfa' in target_user.preferences:
        if 'method' in target_user.preferences['mfa']:
            del target_user.preferences['mfa']['method']
    
    # Commit changes
    db_session.commit()
    
    # Log the action
    logger.info(f"Admin {admin_user.id} reset MFA for user {target_user.id}")
    
    return True