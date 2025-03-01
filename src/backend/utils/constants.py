"""
System-wide constants used throughout the Justice Bid Rate Negotiation System backend.

This module defines constants, enumerations, and standardized values that are used
across multiple services within the system to ensure consistency.
"""

from enum import Enum

# API Configuration
API_VERSION = "v1"

# Pagination Settings
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Date and Time Formats
DEFAULT_DATE_FORMAT = "YYYY-MM-DD"
DEFAULT_DATETIME_FORMAT = "YYYY-MM-DDTHH:mm:ss.sssZ"

# Default Settings
DEFAULT_CURRENCY = "USD"

# File Upload Configuration
MAX_FILE_SIZE_MB = 10
SUPPORTED_FILE_FORMATS = ["xlsx", "csv"]

# Authentication and Security
JWT_EXPIRATION_MINUTES = 60
REFRESH_TOKEN_EXPIRATION_DAYS = 7
PASSWORD_MIN_LENGTH = 12
MFA_CODE_LENGTH = 6
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


class RateStatus(Enum):
    """Enumeration of possible rate statuses in the system."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    CLIENT_APPROVED = "client_approved"
    CLIENT_REJECTED = "client_rejected"
    CLIENT_COUNTER_PROPOSED = "client_counter_proposed"
    FIRM_ACCEPTED = "firm_accepted"
    FIRM_COUNTER_PROPOSED = "firm_counter_proposed"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    EXPORTED = "exported"
    ACTIVE = "active"
    EXPIRED = "expired"


class RateType(Enum):
    """Enumeration of possible rate types in the system."""
    STANDARD = "standard"
    APPROVED = "approved"
    PROPOSED = "proposed"
    COUNTER_PROPOSED = "counter_proposed"


class NegotiationStatus(Enum):
    """Enumeration of possible negotiation statuses in the system."""
    REQUESTED = "requested"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class ApprovalStatus(Enum):
    """Enumeration of possible approval workflow statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"


class OrganizationType(Enum):
    """Enumeration of organization types in the system."""
    LAW_FIRM = "law_firm"
    CLIENT = "client"
    ADMIN = "admin"


class OCGStatus(Enum):
    """Enumeration of possible Outside Counsel Guidelines statuses."""
    DRAFT = "draft"
    PUBLISHED = "published"
    NEGOTIATING = "negotiating"
    SIGNED = "signed"


class ExperienceType(Enum):
    """Enumeration of attorney experience metrics for staff classes."""
    GRADUATION_YEAR = "graduation_year"
    BAR_YEAR = "bar_year"
    YEARS_IN_ROLE = "years_in_role"


class ErrorCode(Enum):
    """Enumeration of API error codes."""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_CONFLICT = "resource_conflict"
    RATE_RULE_VIOLATION = "rate_rule_violation"
    INVALID_STATE_TRANSITION = "invalid_state_transition"
    INTEGRATION_ERROR = "integration_error"
    SYSTEM_ERROR = "system_error"


class UserRole(Enum):
    """Enumeration of user roles in the system."""
    SYSTEM_ADMINISTRATOR = "system_administrator"
    ORGANIZATION_ADMINISTRATOR = "organization_administrator"
    RATE_ADMINISTRATOR = "rate_administrator"
    APPROVER = "approver"
    ANALYST = "analyst"
    STANDARD_USER = "standard_user"