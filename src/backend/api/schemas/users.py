"""
Pydantic models for user-related API operations in the Justice Bid Rate Negotiation System.

These schemas handle validation for user creation, authentication, profiles, and permission management,
providing a structured interface for the user-related API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator, EmailStr, constr

from ...utils.constants import (
    UserRole, 
    JWT_EXPIRATION_MINUTES, 
    REFRESH_TOKEN_EXPIRATION_DAYS,
    MFA_CODE_LENGTH,
    PASSWORD_MIN_LENGTH
)
from ...utils.validators import (
    validate_email,
    validate_password,
    validate_required
)
from .organizations import OrganizationOut


class UserBase(BaseModel):
    """Base schema for user data with common fields."""
    email: EmailStr
    name: str
    role: Optional[UserRole] = None
    
    @validator('email')
    def validate_email(cls, value):
        """Validate email format."""
        validate_email(value, "email")
        return value
    
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    organization_id: UUID
    password: str
    role: UserRole
    
    @validator('password')
    def validate_password(cls, value):
        """Validate password complexity."""
        validate_password(value, "password")
        return value


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    name: Optional[str] = None
    role: Optional[UserRole] = None
    permissions: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    class Config:
        orm_mode = True


class UserPasswordUpdate(BaseModel):
    """Schema for updating a user's password."""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, value):
        """Validate new password complexity."""
        validate_password(value, "new_password")
        return value


class UserInDB(UserBase):
    """Internal schema for user with database fields."""
    id: UUID
    organization_id: UUID
    password_hash: str
    is_active: bool
    last_login: Optional[datetime]
    mfa_enabled: bool
    mfa_secret: Optional[str]
    password_changed_at: Optional[datetime]
    permissions: Dict[str, Any]
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[UUID] = None
    
    class Config:
        orm_mode = True


class UserOut(UserBase):
    """Schema for user data in API responses."""
    id: UUID
    organization_id: UUID
    is_active: bool
    last_login: Optional[datetime]
    mfa_enabled: bool
    permissions: Dict[str, Any]
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    organization: Optional[OrganizationOut] = None
    
    class Config:
        orm_mode = True


class UserList(BaseModel):
    """Schema for paginated list of users."""
    items: List[UserOut]
    total: int
    page: int
    size: int
    pages: int


class LoginRequest(BaseModel):
    """Schema for user login requests."""
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False
    
    @validator('email')
    def validate_email(cls, value):
        """Validate email format."""
        validate_email(value, "email")
        return value
    
    class Config:
        orm_mode = True


class MFALoginRequest(BaseModel):
    """Schema for MFA verification during login."""
    temp_token: str
    mfa_code: str
    
    @validator('mfa_code')
    def validate_mfa_code(cls, value):
        """Validate MFA code format."""
        if not isinstance(value, str) or len(value) != MFA_CODE_LENGTH:
            raise ValueError(f"MFA code must be {MFA_CODE_LENGTH} digits")
        if not value.isdigit():
            raise ValueError("MFA code must contain only digits")
        return value
    
    class Config:
        orm_mode = True


class Token(BaseModel):
    """Schema for authentication token responses."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    user: Optional[UserOut] = None
    
    class Config:
        orm_mode = True


class RefreshRequest(BaseModel):
    """Schema for token refresh requests."""
    refresh_token: str
    
    class Config:
        orm_mode = True


class PasswordChangeRequest(BaseModel):
    """Schema for authenticated password change requests."""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, value):
        """Validate new password complexity."""
        validate_password(value, "new_password")
        return value
    
    class Config:
        orm_mode = True


class PasswordResetRequest(BaseModel):
    """Schema for password reset requests (forgot password)."""
    email: EmailStr
    
    @validator('email')
    def validate_email(cls, value):
        """Validate email format."""
        validate_email(value, "email")
        return value
    
    class Config:
        orm_mode = True


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset with token."""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, value):
        """Validate new password complexity."""
        validate_password(value, "new_password")
        return value
    
    class Config:
        orm_mode = True


class MFASetupRequest(BaseModel):
    """Schema for MFA setup requests."""
    enable: bool
    method: Optional[str] = None
    
    class Config:
        orm_mode = True


class MFAVerifyRequest(BaseModel):
    """Schema for MFA verification during setup."""
    code: str
    
    @validator('code')
    def validate_code(cls, value):
        """Validate MFA verification code format."""
        if not isinstance(value, str) or len(value) != MFA_CODE_LENGTH:
            raise ValueError(f"Code must be {MFA_CODE_LENGTH} digits")
        if not value.isdigit():
            raise ValueError("Code must contain only digits")
        return value
    
    class Config:
        orm_mode = True


class UserSearchParams(BaseModel):
    """Schema for user search parameters."""
    name: Optional[str] = None
    email: Optional[str] = None
    organization_id: Optional[UUID] = None
    role: Optional[UserRole] = None
    active_only: Optional[bool] = True
    page: int = 1
    page_size: int = 20
    
    class Config:
        orm_mode = True