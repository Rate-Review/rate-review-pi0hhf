"""Defines and registers all API v1 routes for the Justice Bid Rate Negotiation System.
Creates a Flask Blueprint for versioned API endpoints and registers all endpoint routers with appropriate prefixes and middleware."""
from flask import Blueprint # flask==2.0.1
from flask import jsonify
from flask_cors import CORS  # flask-cors==3.0.10

from api.core.config import API_V1_STR  # src/backend/api/core/config.py
from api.core.auth import jwt_required  # src/backend/api/core/auth.py
from api.core.errors import error_handler  # src/backend/api/core/errors.py
from api.endpoints.health import router as health_router  # src/backend/api/endpoints/health.py
from api.endpoints.auth import router as auth_router  # src/backend/api/endpoints/auth.py
from api.endpoints.users import router as users_router  # src/backend/api/endpoints/users.py
from api.endpoints.organizations import router as organizations_router  # src/backend/api/endpoints/organizations.py
from api.endpoints.attorneys import router as attorneys_router  # src/backend/api/endpoints/attorneys.py
from api.endpoints.staff_classes import router as staff_classes_router  # src/backend/api/endpoints/staff_classes.py
from api.endpoints.peer_groups import router as peer_groups_router  # src/backend/api/endpoints/peer_groups.py
from api.endpoints.billing import router as billing_router  # src/backend/api/endpoints/billing.py
from api.endpoints.rates import router as rates_router  # src/backend/api/endpoints/rates.py
from api.endpoints.messages import router as messages_router  # src/backend/api/endpoints/messages.py
from api.endpoints.documents import router as documents_router  # src/backend/api/endpoints/documents.py
from api.endpoints.negotiations import router as negotiations_router  # src/backend/api/endpoints/negotiations.py
from api.endpoints.ocg import router as ocg_router  # src/backend/api/endpoints/ocg.py
from api.endpoints.integrations import router as integrations_router  # src/backend/api/endpoints/integrations.py
from api.endpoints.analytics import router as analytics_router  # src/backend/api/endpoints/analytics.py

api_v1_bp = Blueprint('api_v1', __name__)

def create_api_v1_router():
    """Creates and configures the v1 API Blueprint with all routes and middleware"""
    # Create a Flask Blueprint for API v1 endpoints
    api_v1_bp = Blueprint('api_v1', __name__)

    # Register public endpoints without authentication
    api_v1_bp.register_blueprint(health_router)
    api_v1_bp.register_blueprint(auth_router)

    # Apply error handling middleware to Blueprint
    api_v1_bp.register_error_handler(Exception, error_handler)

    # Apply CORS middleware to allow cross-origin requests
    CORS(api_v1_bp)

    # Register protected endpoints with JWT authentication
    api_v1_bp.before_request(jwt_required)
    api_v1_bp.register_blueprint(users_router)
    api_v1_bp.register_blueprint(organizations_router)
    api_v1_bp.register_blueprint(attorneys_router)
    api_v1_bp.register_blueprint(staff_classes_router)
    api_v1_bp.register_blueprint(peer_groups_router)
    api_v1_bp.register_blueprint(billing_router)
    api_v1_bp.register_blueprint(rates_router)
    api_v1_bp.register_blueprint(messages_router)
    api_v1_bp.register_blueprint(documents_router)
    api_v1_bp.register_blueprint(negotiations_router)
    api_v1_bp.register_blueprint(ocg_router)
    api_v1_bp.register_blueprint(integrations_router)
    api_v1_bp.register_blueprint(analytics_router)

    # Return the configured Blueprint
    return api_v1_bp

def register_routes(app):
    """Registers all API v1 routes with the main Flask application"""
    # Create the API v1 router using create_api_v1_router()
    api_v1_bp = create_api_v1_router()

    # Register the Blueprint with the Flask app using the API_V1_STR prefix
    app.register_blueprint(api_v1_bp, url_prefix=API_V1_STR)