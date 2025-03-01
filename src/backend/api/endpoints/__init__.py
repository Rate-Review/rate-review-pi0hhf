"""
Initialization file for the API endpoints package that imports and exposes all endpoint routers for registration with the main API router
"""

from fastapi import APIRouter

from .health import health_router  # Import health check endpoints
from .auth import auth_router  # Import authentication endpoints
from .users import user_router  # Import user management endpoints
from .organizations import organization_router  # Import organization management endpoints
from .attorneys import attorney_router  # Import attorney management endpoints
from .staff_classes import staff_class_router  # Import staff class management endpoints
from .peer_groups import peer_group_router  # Import peer group management endpoints
from .billing import billing_router  # Import billing data endpoints
from .rates import rate_router  # Import rate management endpoints
from .messages import message_router  # Import messaging endpoints
from .documents import document_router  # Import document management endpoints
from .negotiations import negotiation_router  # Import negotiation management endpoints
from .ocg import ocg_router  # Import Outside Counsel Guidelines endpoints
from .integrations import integration_router  # Import integration endpoints for external systems
from .analytics import analytics_router  # Import analytics endpoints for data analysis

__all__ = [
    "health_router",
    "auth_router",
    "user_router",
    "organization_router",
    "attorney_router",
    "staff_class_router",
    "peer_group_router",
    "billing_router",
    "rate_router",
    "message_router",
    "document_router",
    "negotiation_router",
    "ocg_router",
    "integration_router",
    "analytics_router"
]