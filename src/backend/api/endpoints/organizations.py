"""
API endpoints for managing organizations in the Justice Bid Rate Negotiation System. Provides endpoints for creating,
retrieving, updating, and deleting client and law firm organizations, as well as managing their offices, departments,
rate rules, and relationships. Enforces proper authorization and validation for all operations.
"""

import uuid
from typing import List, Optional

from flask import Blueprint, request, jsonify  # flask 2.3+
from pydantic import ValidationError  # pydantic ^1.10.0

from ..core.auth import require_auth, require_role, require_organization_access, get_current_user  # Importing authentication and authorization functions
from ..core.errors import validate_uuid, APIError, parse_query_params  # Importing validation and error handling functions
from ...services.organizations.client import ClientService  # Importing ClientService for client organization management
from ...services.organizations.firm import FirmService  # Importing FirmService for law firm organization management
from ...db.repositories.organization_repository import OrganizationRepository  # Importing OrganizationRepository for data access
from ...utils.constants import OrganizationType  # Importing OrganizationType enum
from ...db.session import get_db  # Importing database session management
from ..schemas.organizations import OrganizationCreate, OrganizationUpdate, OrganizationOut, OrganizationList, OrganizationSearchParams, OfficeCreate, DepartmentCreate, RateRulesUpdate, PeerGroupCreate  # Importing Pydantic schemas for request validation
from ...utils.logging import get_logger  # Importing logging utility

# Initialize Flask Blueprint for organization-related endpoints
organizations_blueprint = Blueprint('organizations', __name__, url_prefix='/api/v1/organizations')

# Initialize services and repositories
client_service = ClientService()
firm_service = FirmService()
organization_repository = OrganizationRepository(get_db())
logger = get_logger(__name__, 'api')


@organizations_blueprint.route('/', methods=['GET'])
@require_auth
@require_role('admin')
def get_organizations():
    """Get a paginated list of organizations with optional filtering"""
    try:
        search_params = OrganizationSearchParams(**parse_query_params(request.args))
    except ValidationError as e:
        raise APIError(message="Invalid query parameters", error_code="invalid_params", details=e.errors(), status_code=400)

    name = search_params.name
    org_type = search_params.type
    active_only = search_params.active_only
    page = search_params.page
    page_size = search_params.page_size

    organizations, total = organization_repository.search(query=name, type=org_type, limit=page_size, offset=(page - 1) * page_size)
    total_pages = (total + page_size - 1) // page_size

    organization_list = OrganizationList(
        items=[OrganizationOut.from_orm(org) for org in organizations],
        total=total,
        page=page,
        size=page_size,
        pages=total_pages
    )

    return jsonify(organization_list.dict()), 200


@organizations_blueprint.route('/<uuid:organization_id>', methods=['GET'])
@require_auth
@require_organization_access('organization_id')
def get_organization(organization_id: uuid.UUID):
    """Get a specific organization by ID"""
    validate_uuid(str(organization_id), "organization_id")

    organization = organization_repository.get_by_id(organization_id)
    if not organization:
        raise APIError(message="Organization not found", error_code="resource_not_found", status_code=404)

    return jsonify(OrganizationOut.from_orm(organization).dict()), 200


@organizations_blueprint.route('/', methods=['POST'])
@require_auth
@require_role('admin')
def create_organization():
    """Create a new organization (client or law firm)"""
    try:
        org_data = OrganizationCreate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    if org_data.type == OrganizationType.CLIENT:
        organization = client_service.create_client(name=org_data.name, domain=org_data.domain, settings=org_data.settings)
    elif org_data.type == OrganizationType.LAW_FIRM:
        organization = firm_service.create_firm(name=org_data.name, domain=org_data.domain, settings=org_data.settings)
    else:
        raise APIError(message="Invalid organization type", error_code="invalid_request", status_code=400)

    if not organization:
        raise APIError(message="Failed to create organization", error_code="resource_conflict", status_code=409)

    return jsonify(OrganizationOut(**organization).dict()), 201


@organizations_blueprint.route('/<uuid:organization_id>', methods=['PUT'])
@require_auth
@require_organization_access('organization_id')
def update_organization(organization_id: uuid.UUID):
    """Update an existing organization"""
    validate_uuid(str(organization_id), "organization_id")

    try:
        org_data = OrganizationUpdate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    update_data = org_data.dict(exclude_unset=True)

    organization = organization_repository.update(organization_id, update_data)
    if not organization:
        raise APIError(message="Organization not found", error_code="resource_not_found", status_code=404)

    return jsonify(OrganizationOut.from_orm(organization).dict()), 200


@organizations_blueprint.route('/<uuid:organization_id>/activate', methods=['POST'])
@require_auth
@require_role('admin')
def activate_organization(organization_id: uuid.UUID):
    """Activate an organization"""
    validate_uuid(str(organization_id), "organization_id")

    success = organization_repository.set_active_status(organization_id, True)
    if not success:
        raise APIError(message="Organization not found", error_code="resource_not_found", status_code=404)

    return jsonify({'message': 'Organization activated'}), 200


@organizations_blueprint.route('/<uuid:organization_id>/deactivate', methods=['POST'])
@require_auth
@require_role('admin')
def deactivate_organization(organization_id: uuid.UUID):
    """Deactivate an organization"""
    validate_uuid(str(organization_id), "organization_id")

    success = organization_repository.set_active_status(organization_id, False)
    if not success:
        raise APIError(message="Organization not found", error_code="resource_not_found", status_code=404)

    return jsonify({'message': 'Organization deactivated'}), 200


@organizations_blueprint.route('/clients', methods=['GET'])
@require_auth
def get_clients():
    """Get a paginated list of client organizations"""
    try:
        search_params = OrganizationSearchParams(**parse_query_params(request.args))
    except ValidationError as e:
        raise APIError(message="Invalid query parameters", error_code="invalid_params", details=e.errors(), status_code=400)

    active_only = search_params.active_only
    page = search_params.page
    page_size = search_params.page_size

    clients = client_service.get_all_clients(active_only=active_only, limit=page_size, offset=(page - 1) * page_size)

    return jsonify([OrganizationOut.from_orm(client).dict() for client in clients]), 200


@organizations_blueprint.route('/firms', methods=['GET'])
@require_auth
def get_law_firms():
    """Get a paginated list of law firm organizations"""
    try:
        search_params = OrganizationSearchParams(**parse_query_params(request.args))
    except ValidationError as e:
        raise APIError(message="Invalid query parameters", error_code="invalid_params", details=e.errors(), status_code=400)

    active_only = search_params.active_only
    page = search_params.page
    page_size = search_params.page_size

    firms = firm_service.get_all_firms(active_only=active_only, limit=page_size, offset=(page - 1) * page_size)

    return jsonify([OrganizationOut.from_orm(firm).dict() for firm in firms]), 200


@organizations_blueprint.route('/clients/<uuid:client_id>', methods=['GET'])
@require_auth
@require_organization_access('client_id')
def get_client(client_id: uuid.UUID):
    """Get a specific client organization by ID"""
    validate_uuid(str(client_id), "client_id")

    client = client_service.get_client_by_id(client_id)
    if not client:
        raise APIError(message="Client not found", error_code="resource_not_found", status_code=404)

    return jsonify(OrganizationOut.from_orm(client).dict()), 200


@organizations_blueprint.route('/clients', methods=['POST'])
@require_auth
@require_role('admin')
def create_client():
    """Create a new client organization"""
    try:
        org_data = OrganizationCreate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    client = client_service.create_client(name=org_data.name, domain=org_data.domain, settings=org_data.settings)
    if not client:
        raise APIError(message="Failed to create client", error_code="resource_conflict", status_code=409)

    return jsonify(OrganizationOut(**client).dict()), 201


@organizations_blueprint.route('/clients/<uuid:client_id>', methods=['PUT'])
@require_auth
@require_organization_access('client_id')
def update_client(client_id: uuid.UUID):
    """Update an existing client organization"""
    validate_uuid(str(client_id), "client_id")

    try:
        org_data = OrganizationUpdate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    update_data = org_data.dict(exclude_unset=True)

    client = client_service.update_client(client_id, update_data)
    if not client:
        raise APIError(message="Client not found", error_code="resource_not_found", status_code=404)

    return jsonify(OrganizationOut.from_orm(client).dict()), 200


@organizations_blueprint.route('/firms/<uuid:firm_id>', methods=['GET'])
@require_auth
@require_organization_access('firm_id')
def get_law_firm(firm_id: uuid.UUID):
    """Get a specific law firm organization by ID"""
    validate_uuid(str(firm_id), "firm_id")

    firm = firm_service.get_firm_by_id(firm_id)
    if not firm:
        raise APIError(message="Law firm not found", error_code="resource_not_found", status_code=404)

    return jsonify(OrganizationOut.from_orm(firm).dict()), 200


@organizations_blueprint.route('/firms', methods=['POST'])
@require_auth
@require_role('admin')
def create_law_firm():
    """Create a new law firm organization"""
    try:
        org_data = OrganizationCreate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    firm = firm_service.create_firm(name=org_data.name, domain=org_data.domain, settings=org_data.settings)
    if not firm:
        raise APIError(message="Failed to create law firm", error_code="resource_conflict", status_code=409)

    return jsonify(OrganizationOut(**firm).dict()), 201


@organizations_blueprint.route('/firms/<uuid:firm_id>', methods=['PUT'])
@require_auth
@require_organization_access('firm_id')
def update_law_firm(firm_id: uuid.UUID):
    """Update an existing law firm organization"""
    validate_uuid(str(firm_id), "firm_id")

    try:
        org_data = OrganizationUpdate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    update_data = org_data.dict(exclude_unset=True)

    firm = firm_service.update_firm(firm_id, update_data)
    if not firm:
        raise APIError(message="Law firm not found", error_code="resource_not_found", status_code=404)

    return jsonify(OrganizationOut.from_orm(firm).dict()), 200


@organizations_blueprint.route('/clients/<uuid:client_id>/offices', methods=['POST'])
@require_auth
@require_organization_access('client_id')
def add_client_office(client_id: uuid.UUID):
    """Add a new office to a client organization"""
    validate_uuid(str(client_id), "client_id")

    try:
        office_data = OfficeCreate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    office = client_service.add_client_office(client_id, office_data.name, office_data.city, office_data.country, office_data.state, office_data.region)
    if not office:
        raise APIError(message="Failed to add office", error_code="resource_conflict", status_code=409)

    return jsonify(OfficeOut(**office).dict()), 201


@organizations_blueprint.route('/firms/<uuid:firm_id>/offices', methods=['POST'])
@require_auth
@require_organization_access('firm_id')
def add_firm_office(firm_id: uuid.UUID):
    """Add a new office to a law firm organization"""
    validate_uuid(str(firm_id), "firm_id")

    try:
        office_data = OfficeCreate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    office = firm_service.add_firm_office(firm_id, office_data.name, office_data.city, office_data.country, office_data.state, office_data.region)
    if not office:
        raise APIError(message="Failed to add office", error_code="resource_conflict", status_code=409)

    return jsonify(OfficeOut(**office).dict()), 201


@organizations_blueprint.route('/clients/<uuid:client_id>/departments', methods=['POST'])
@require_auth
@require_organization_access('client_id')
def add_client_department(client_id: uuid.UUID):
    """Add a new department to a client organization"""
    validate_uuid(str(client_id), "client_id")

    try:
        dept_data = DepartmentCreate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    department = client_service.add_client_department(client_id, dept_data.name, dept_data.metadata)
    if not department:
        raise APIError(message="Failed to add department", error_code="resource_conflict", status_code=409)

    return jsonify(DepartmentOut(**department).dict()), 201


@organizations_blueprint.route('/firms/<uuid:firm_id>/departments', methods=['POST'])
@require_auth
@require_organization_access('firm_id')
def add_firm_department(firm_id: uuid.UUID):
    """Add a new department to a law firm organization"""
    validate_uuid(str(firm_id), "firm_id")

    try:
        dept_data = DepartmentCreate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    department = firm_service.add_firm_department(firm_id, dept_data.name)
    if not department:
        raise APIError(message="Failed to add department", error_code="resource_conflict", status_code=409)

    return jsonify(DepartmentOut(**department).dict()), 201


@organizations_blueprint.route('/clients/<uuid:client_id>/rate-rules', methods=['GET'])
@require_auth
@require_organization_access('client_id')
def get_client_rate_rules(client_id: uuid.UUID):
    """Get rate rules for a client organization"""
    validate_uuid(str(client_id), "client_id")

    rate_rules = client_service.get_rate_rules(client_id)
    return jsonify(rate_rules), 200


@organizations_blueprint.route('/clients/<uuid:client_id>/rate-rules', methods=['PUT'])
@require_auth
@require_organization_access('client_id')
def update_client_rate_rules(client_id: uuid.UUID):
    """Update rate rules for a client organization"""
    validate_uuid(str(client_id), "client_id")

    try:
        rate_rules_data = RateRulesUpdate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    rate_rules = client_service.update_rate_rules(client_id, rate_rules_data.dict(exclude_unset=True))
    if not rate_rules:
        raise APIError(message="Client not found", error_code="resource_not_found", status_code=404)

    return jsonify(rate_rules), 200


@organizations_blueprint.route('/clients/<uuid:client_id>/law-firms', methods=['GET'])
@require_auth
@require_organization_access('client_id')
def get_client_law_firms(client_id: uuid.UUID):
    """Get all law firms associated with a client"""
    validate_uuid(str(client_id), "client_id")

    law_firms = client_service.get_law_firm_relationships(client_id)
    return jsonify(law_firms), 200


@organizations_blueprint.route('/clients/<uuid:client_id>/law-firms', methods=['POST'])
@require_auth
@require_organization_access('client_id')
def add_client_law_firm_relationship(client_id: uuid.UUID):
    """Add a relationship between a client and a law firm"""
    validate_uuid(str(client_id), "client_id")

    try:
        data = request.get_json()
        firm_id = data.get('firm_id')
        relationship_settings = data.get('relationship_settings')
        validate_uuid(str(firm_id), "firm_id")
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    relationship = client_service.add_law_firm_relationship(client_id, firm_id, relationship_settings)
    if not relationship:
        raise APIError(message="Failed to add relationship", error_code="resource_conflict", status_code=409)

    return jsonify(relationship), 201


@organizations_blueprint.route('/firms/<uuid:firm_id>/clients', methods=['GET'])
@require_auth
@require_organization_access('firm_id')
def get_law_firm_clients(firm_id: uuid.UUID):
    """Get all clients associated with a law firm"""
    validate_uuid(str(firm_id), "firm_id")

    clients = firm_service.get_client_relationships(firm_id)
    return jsonify(clients), 200


@organizations_blueprint.route('/clients/<uuid:client_id>/peer-groups', methods=['POST'])
@require_auth
@require_organization_access('client_id')
def create_client_peer_group(client_id: uuid.UUID):
    """Create a new peer group for a client organization"""
    validate_uuid(str(client_id), "client_id")

    try:
        peer_group_data = PeerGroupCreate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    peer_group = client_service.create_peer_group(client_id, peer_group_data.name, peer_group_data.criteria)
    if not peer_group:
        raise APIError(message="Failed to create peer group", error_code="resource_conflict", status_code=409)

    return jsonify(peer_group), 201


@organizations_blueprint.route('/clients/<uuid:client_id>/peer-groups', methods=['GET'])
@require_auth
@require_organization_access('client_id')
def get_client_peer_groups(client_id: uuid.UUID):
    """Get all peer groups for a client organization"""
    validate_uuid(str(client_id), "client_id")

    peer_groups = client_service.get_peer_groups(client_id)
    return jsonify(peer_groups), 200


@organizations_blueprint.route('/firms/<uuid:firm_id>/peer-groups', methods=['POST'])
@require_auth
@require_organization_access('firm_id')
def create_firm_peer_group(firm_id: uuid.UUID):
    """Create a new peer group for a law firm organization"""
    validate_uuid(str(firm_id), "firm_id")

    try:
        peer_group_data = PeerGroupCreate(**request.get_json())
    except ValidationError as e:
        raise APIError(message="Invalid request body", error_code="invalid_request", details=e.errors(), status_code=400)

    peer_group = firm_service.create_peer_group(firm_id, peer_group_data.name, peer_group_data.criteria)
    if not peer_group:
        raise APIError(message="Failed to create peer group", error_code="resource_conflict", status_code=409)

    return jsonify(peer_group), 201


@organizations_blueprint.route('/firms/<uuid:firm_id>/peer-groups', methods=['GET'])
@require_auth
@require_organization_access('firm_id')
def get_firm_peer_groups(firm_id: uuid.UUID):
    """Get all peer groups for a law firm organization"""
    validate_uuid(str(firm_id), "firm_id")

    peer_groups = firm_service.get_peer_groups(firm_id)
    return jsonify(peer_groups), 200