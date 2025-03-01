"""
Initialization module for the repository package that exports all repository classes,
providing a convenient interface for database operations across the application.
"""

from .user_repository import UserRepository  # v1.0 - Repository for user database operations
from .organization_repository import OrganizationRepository  # v1.0 - Repository for organization database operations
from .attorney_repository import AttorneyRepository  # v1.0 - Repository for attorney database operations
from .staff_class_repository import StaffClassRepository  # v1.0 - Repository for staff class database operations
from .peer_group_repository import PeerGroupRepository  # v1.0 - Repository for peer group database operations
from .billing_repository import BillingRepository  # v1.0 - Repository for billing database operations
from .rate_repository import RateRepository  # v1.0 - Repository for rate database operations
from .message_repository import MessageRepository  # v1.0 - Repository for message database operations
from .document_repository import DocumentRepository  # v1.0 - Repository for document database operations
from .negotiation_repository import NegotiationRepository  # v1.0 - Repository for negotiation database operations
from .ocg_repository import OCGRepository  # v1.0 - Repository for Outside Counsel Guidelines database operations
from .approval_workflow_repository import ApprovalWorkflowRepository  # v1.0 - Repository for approval workflow database operations

__all__ = [
    "UserRepository",
    "OrganizationRepository",
    "AttorneyRepository",
    "StaffClassRepository",
    "PeerGroupRepository",
    "BillingRepository",
    "RateRepository",
    "MessageRepository",
    "DocumentRepository",
    "NegotiationRepository",
    "OCGRepository",
    "ApprovalWorkflowRepository",
]