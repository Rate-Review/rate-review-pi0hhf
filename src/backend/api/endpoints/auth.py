"""
API endpoints for authentication and authorization in the Justice Bid Rate Negotiation System.
Provides routes for user login, logout, token management, password operations, MFA, and SSO integration.
"""

from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session  # sqlalchemy 2.0+

from ..core.auth import (
    login_user,
    complete_mfa_login,
    refresh_auth_token,
    logout_user,
    get_current_user,
    request_password_reset,
    reset_password,
    change_password,
    require_auth,
    MFARequiredError
)
from ..schemas.users import (
    LoginRequest,
    MFALoginRequest,
    Token,
    RefreshRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    MFASetupRequest,
    MFAVerifyRequest
)
from ...services.auth.mfa import (
    generate_totp_secret,
    verify_totp_code,
    generate_totp_qr_code,
    enable_totp_mfa,
    enable_email_mfa,
    confirm_email_mfa,
    disable_mfa,
    change_mfa_method
)
from ...services.auth.sso import (
    process_saml_login,
    process_saml_callback,
    process_oauth_login,
    process_oauth_callback,
    get_sso_provider
)
from ...db.repositories.user_repository import UserRepository
from ..schemas.users import UserOut
from ..core.dependencies import get_db
from ...utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Define API router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user with email and password"""
    try:
        token_data = login_user(request.email, request.password, db)
        return token_data
    except MFARequiredError as e:
        return e.challenge
    except Exception as e:
        logger.error(f"Login failed for user {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/mfa-login", response_model=Token)
def complete_mfa(request: MFALoginRequest, db: Session = Depends(get_db)):
    """Complete MFA verification during login"""
    try:
        token_data = complete_mfa_login(request.temp_token, request.mfa_code, db)
        return token_data
    except Exception as e:
        logger.error(f"MFA verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token"""
    try:
        token_data = refresh_auth_token(request.refresh_token, db)
        return token_data
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    """Log out a user by invalidating their token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization header is required",
        )
    token = auth_header.split(" ")[1]
    success = logout_user(token, db)
    if success:
        return {"message": "Logout successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )


@router.post("/password-reset/request")
def request_reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request a password reset email"""
    try:
        request_password_reset(request.email, db)
        return {"message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Password reset request failed for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email",
        )


@router.post("/password-reset/confirm")
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password using a valid reset token"""
    try:
        reset_password(request.token, request.new_password, db)
        return {"message": "Password reset successful"}
    except Exception as e:
        logger.error(f"Password reset failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/password-change", dependencies=[Depends(require_auth)])
def change_password(request: PasswordChangeRequest, db: Session = Depends(get_db)):
    """Change password for the authenticated user"""
    user = get_current_user()
    try:
        change_password(user.id, request.current_password, request.new_password, db)
        return {"message": "Password change successful"}
    except Exception as e:
        logger.error(f"Password change failed for user {user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/me", response_model=UserOut, dependencies=[Depends(require_auth)])
def me(db: Session = Depends(get_db)):
    """Get the current authenticated user's profile"""
    user = get_current_user()
    user_repo = UserRepository(db)
    user_db = user_repo.get_by_id(user.id)
    return user_db


@router.post("/mfa/setup", dependencies=[Depends(require_auth)])
def setup_mfa(request: MFASetupRequest, db: Session = Depends(get_db)):
    """Setup Multi-Factor Authentication for a user"""
    user = get_current_user()
    try:
        if request.enable is False:
            success = disable_mfa(db, user)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to disable MFA",
                )
            return {"message": "MFA disabled"}

        if request.method == "totp":
            secret = generate_totp_secret()
            qr_code = generate_totp_qr_code(secret, user.email, "Justice Bid")
            return {"method": "totp", "secret": secret, "qr_code": qr_code}
        elif request.method == "email":
            success = enable_email_mfa(db, user)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to initiate email MFA setup",
                )
            return {"method": "email", "message": "Verification code sent to email"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA method",
            )
    except Exception as e:
        logger.error(f"MFA setup failed for user {user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/mfa/verify", dependencies=[Depends(require_auth)])
def verify_mfa(request: MFAVerifyRequest, db: Session = Depends(get_db)):
    """Verify MFA setup with verification code"""
    user = get_current_user()
    try:
        if user.preferences and 'mfa' in user.preferences and user.preferences['mfa'].get('method') == 'totp':
            if verify_totp_code(user.mfa_secret, request.code):
                enable_totp_mfa(db, user, user.mfa_secret, request.code)
                return {"message": "MFA setup verified"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification code",
                )
        elif user.preferences and 'mfa' in user.preferences and user.preferences['mfa'].get('method') == 'email':
            if confirm_email_mfa(db, user, request.code):
                return {"message": "MFA setup verified"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification code",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA method not set up",
            )
    except Exception as e:
        logger.error(f"MFA verification failed for user {user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/sso/saml/{provider_id}")
def initiate_saml_login(provider_id: str, request: Request, db: Session = Depends(get_db)):
    """Initiate SAML authentication flow"""
    try:
        # Construct the return URL
        return_to = str(request.url_for("complete_saml_login", provider_id=provider_id))
        saml_data = process_saml_login(provider_id, return_to)
        return saml_data
    except Exception as e:
        logger.error(f"SAML login initiation failed for provider {provider_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/sso/saml/{provider_id}/callback", response_model=Token)
def complete_saml_login(provider_id: str, request: Request, db: Session = Depends(get_db)):
    """Complete SAML authentication after IdP callback"""
    try:
        form_data = await request.form()
        token_data = process_saml_callback(provider_id, form_data)
        return token_data
    except Exception as e:
        logger.error(f"SAML login completion failed for provider {provider_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/sso/oauth/{provider_id}")
def initiate_oauth_login(provider_id: str, request: Request, db: Session = Depends(get_db)):
    """Initiate OAuth authentication flow"""
    try:
        # Construct the redirect URI
        redirect_uri = str(request.url_for("complete_oauth_login", provider_id=provider_id))
        oauth_data = process_oauth_login(provider_id, redirect_uri)
        return oauth_data
    except Exception as e:
        logger.error(f"OAuth login initiation failed for provider {provider_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/sso/oauth/{provider_id}/callback", response_model=Token)
async def complete_oauth_login(provider_id: str, request: Request, db: Session = Depends(get_db)):
    """Complete OAuth authentication after provider callback"""
    try:
        query_params = dict(request.query_params)
        token_data = process_oauth_callback(provider_id, query_params)
        return token_data
    except Exception as e:
        logger.error(f"OAuth login completion failed for provider {provider_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )