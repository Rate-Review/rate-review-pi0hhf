"""
API endpoints for peer group management in the Justice Bid Rate Negotiation System.
Provides routes for creating, retrieving, updating, and deleting peer groups, as well as managing peer group membership.
Supports filtering and searching capabilities for analytics and benchmarking purposes.
"""
import typing
import uuid  # standard library
from typing import List

from flask import Blueprint, request, jsonify  # ^2.0.0
from pydantic import ValidationError  # ^1.10.0

from ...services.organizations.peer_groups import PeerGroupService  # PeerGroupService: Service layer for peer group operations
from ..schemas.peer_groups import (  # Pydantic schemas for request/response validation
    PeerGroupBase,
    PeerGroupCreate,
    PeerGroupUpdate,
    PeerGroupOut,
    PeerGroupWithMembers,
    PeerGroupList,
    PeerGroupSearchParams,
    PeerGroupMemberAdd,
    PeerGroupMemberRemove,
    PeerGroupMembersList,
    CriteriaUpdate
)
from ..core.auth import require_auth, require_permission, require_organization_access, require_entity_access  # Authentication and authorization decorators
from ..core.errors import (  # Exception classes for API error handling
    ValidationException,
    ResourceNotFoundException,
    ResourceConflictException,
    AuthorizationException
)
from ...utils.logging import get_logger  # Logging utility for endpoint operations

# Initialize logger
logger = get_logger(__name__)

# Create Flask Blueprint
router = Blueprint('peer_groups', __name__)

# Initialize PeerGroupService
peer_group_service = PeerGroupService()


@router.route('/<uuid:peer_group_id>', methods=['GET'])
@require_auth
@require_entity_access('peer_group', 'peer_group_id', 'read')
def get_peer_group(peer_group_id: uuid.UUID):
    """Get a peer group by ID

    Args:
        peer_group_id (uuid.UUID): peer_group_id

    Returns:
        flask.Response: JSON response with peer group data
    """
    try:
        # Get peer group by ID from service layer
        peer_group = peer_group_service.get_peer_group_by_id(peer_group_id)

        # If peer group not found, raise ResourceNotFoundException
        if not peer_group:
            raise ResourceNotFoundException("Peer Group", str(peer_group_id))

        # Return peer group data as JSON response
        return jsonify(peer_group), 200
    except ResourceNotFoundException as e:
        logger.error(f"Peer group not found: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        logger.exception(f"Error getting peer group: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/', methods=['GET'])
@require_auth
@require_organization_access('organization_id')
def list_peer_groups():
    """List peer groups for an organization

    Returns:
        flask.Response: JSON response with paginated list of peer groups
    """
    try:
        # Parse query parameters (organization_id, active_only, page, page_size)
        organization_id = request.args.get('organization_id')
        active_only = request.args.get('active_only', default=True, type=lambda v: v.lower() == 'true')
        page = request.args.get('page', default=1, type=int)
        page_size = request.args.get('page_size', default=20, type=int)

        # Validate parameters using PeerGroupSearchParams
        search_params = PeerGroupSearchParams(
            organization_id=organization_id,
            active_only=active_only,
            page=page,
            page_size=page_size
        )

        # Get peer groups from service layer
        peer_groups = peer_group_service.get_peer_groups_for_organization(
            organization_id=search_params.organization_id,
            active_only=search_params.active_only
        )

        # Calculate pagination metadata
        total = len(peer_groups)
        pages = (total + search_params.page_size - 1) // search_params.page_size
        start = (search_params.page - 1) * search_params.page_size
        end = start + search_params.page_size
        paged_peer_groups = peer_groups[start:end]

        # Return paginated list as JSON response
        return jsonify({
            "items": paged_peer_groups,
            "total": total,
            "page": search_params.page,
            "size": search_params.page_size,
            "pages": pages
        }), 200
    except ValidationError as e:
        logger.error(f"Validation error listing peer groups: {str(e)}")
        return jsonify(ValidationException(message="Invalid parameters", errors=e.errors()).to_dict()), 400
    except Exception as e:
        logger.exception(f"Error listing peer groups: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/', methods=['POST'])
@require_auth
@require_permission('peer_groups:create')
@require_organization_access('organization_id')
def create_peer_group():
    """Create a new peer group

    Returns:
        flask.Response: JSON response with created peer group data
    """
    try:
        # Parse request JSON data
        data = request.get_json()

        # Validate data using PeerGroupCreate schema
        peer_group_create = PeerGroupCreate(**data)

        # Create peer group using service layer
        peer_group = peer_group_service.create_peer_group(
            organization_id=peer_group_create.organization_id,
            name=peer_group_create.name,
            criteria=peer_group_create.criteria
        )

        # If creation fails due to duplicate name, raise ResourceConflictException
        if not peer_group:
            raise ResourceConflictException("Peer group with this name already exists")

        # If creation succeeds, return peer group data with 201 status code
        return jsonify(peer_group), 201
    except ValidationError as e:
        logger.error(f"Validation error creating peer group: {str(e)}")
        return jsonify(ValidationException(message="Invalid input", errors=e.errors()).to_dict()), 400
    except ResourceConflictException as e:
        logger.error(f"Conflict creating peer group: {e.message}")
        return jsonify(e.to_dict()), 409
    except Exception as e:
        logger.exception(f"Error creating peer group: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/<uuid:peer_group_id>', methods=['PUT'])
@require_auth
@require_entity_access('peer_group', 'peer_group_id', 'update')
def update_peer_group(peer_group_id: uuid.UUID):
    """Update an existing peer group

    Args:
        peer_group_id (uuid.UUID): peer_group_id

    Returns:
        flask.Response: JSON response with updated peer group data
    """
    try:
        # Parse request JSON data
        data = request.get_json()

        # Validate data using PeerGroupUpdate schema
        peer_group_update = PeerGroupUpdate(**data)

        # Update peer group using service layer
        peer_group = peer_group_service.update_peer_group(
            peer_group_id=peer_group_id,
            update_data=peer_group_update.dict(exclude_unset=True)
        )

        # If peer group not found, raise ResourceNotFoundException
        if not peer_group:
            raise ResourceNotFoundException("Peer Group", str(peer_group_id))

        # If update fails due to duplicate name, raise ResourceConflictException
        # If update succeeds, return updated peer group data
        return jsonify(peer_group), 200
    except ValidationError as e:
        logger.error(f"Validation error updating peer group: {str(e)}")
        return jsonify(ValidationException(message="Invalid input", errors=e.errors()).to_dict()), 400
    except ResourceNotFoundException as e:
        logger.error(f"Peer group not found: {e.message}")
        return jsonify(e.to_dict()), 404
    except ResourceConflictException as e:
        logger.error(f"Conflict updating peer group: {e.message}")
        return jsonify(e.to_dict()), 409
    except Exception as e:
        logger.exception(f"Error updating peer group: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/<uuid:peer_group_id>', methods=['DELETE'])
@require_auth
@require_entity_access('peer_group', 'peer_group_id', 'delete')
def delete_peer_group(peer_group_id: uuid.UUID):
    """Delete a peer group

    Args:
        peer_group_id (uuid.UUID): peer_group_id

    Returns:
        flask.Response: JSON response with deletion status
    """
    try:
        # Delete peer group using service layer
        deleted = peer_group_service.delete_peer_group(peer_group_id)

        # If peer group not found, raise ResourceNotFoundException
        if not deleted:
            raise ResourceNotFoundException("Peer Group", str(peer_group_id))

        # If deletion succeeds, return success message with 200 status code
        return jsonify({"message": "Peer group deleted successfully"}), 200
    except ResourceNotFoundException as e:
        logger.error(f"Peer group not found: {e.message}")
        return jsonify(e.to_dict()), 404
    except Exception as e:
        logger.exception(f"Error deleting peer group: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/<uuid:peer_group_id>/status', methods=['PATCH'])
@require_auth
@require_entity_access('peer_group', 'peer_group_id', 'update')
def set_active_status(peer_group_id: uuid.UUID):
    """Activate or deactivate a peer group

    Args:
        peer_group_id (uuid.UUID): peer_group_id

    Returns:
        flask.Response: JSON response with updated active status
    """
    try:
        # Parse request JSON data for is_active boolean
        data = request.get_json()
        is_active = data.get('is_active')

        # Update peer group active status using service layer
        updated = peer_group_service.set_peer_group_active_status(peer_group_id, is_active)

        # If peer group not found, raise ResourceNotFoundException
        if not updated:
            raise ResourceNotFoundException("Peer Group", str(peer_group_id))

        # If update succeeds, return success message with updated status
        return jsonify({"message": f"Peer group active status set to {is_active}"}), 200
    except ResourceNotFoundException as e:
        logger.error(f"Peer group not found: {e.message}")
        return jsonify(e.to_dict()), 404
    except Exception as e:
        logger.exception(f"Error setting active status for peer group: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/members', methods=['POST'])
@require_auth
@require_permission('peer_groups:manage_members')
def add_member():
    """Add an organization to a peer group

    Returns:
        flask.Response: JSON response with membership addition status
    """
    try:
        # Parse request JSON data
        data = request.get_json()

        # Validate data using PeerGroupMemberAdd schema
        member_add = PeerGroupMemberAdd(**data)

        # Add organization to peer group using service layer
        added = peer_group_service.add_organization_to_peer_group(
            peer_group_id=member_add.peer_group_id,
            organization_id=member_add.organization_id
        )

        # If peer group not found, raise ResourceNotFoundException
        # If organization not found, raise ResourceNotFoundException
        # If organization is already a member, raise ResourceConflictException
        if not added:
            raise ResourceNotFoundException("Peer Group or Organization", f"{member_add.peer_group_id} or {member_add.organization_id}")

        # If addition succeeds, return success message
        return jsonify({"message": "Organization added to peer group successfully"}), 200
    except ValidationError as e:
        logger.error(f"Validation error adding member to peer group: {str(e)}")
        return jsonify(ValidationException(message="Invalid input", errors=e.errors()).to_dict()), 400
    except ResourceNotFoundException as e:
        logger.error(f"Peer group or organization not found: {e.message}")
        return jsonify(e.to_dict()), 404
    except ResourceConflictException as e:
        logger.error(f"Conflict adding member to peer group: {e.message}")
        return jsonify(e.to_dict()), 409
    except Exception as e:
        logger.exception(f"Error adding member to peer group: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/members', methods=['DELETE'])
@require_auth
@require_permission('peer_groups:manage_members')
def remove_member():
    """Remove an organization from a peer group

    Returns:
        flask.Response: JSON response with membership removal status
    """
    try:
        # Parse request JSON data
        data = request.get_json()

        # Validate data using PeerGroupMemberRemove schema
        member_remove = PeerGroupMemberRemove(**data)

        # Remove organization from peer group using service layer
        removed = peer_group_service.remove_organization_from_peer_group(
            peer_group_id=member_remove.peer_group_id,
            organization_id=member_remove.organization_id
        )

        # If peer group not found, raise ResourceNotFoundException
        if not removed:
            raise ResourceNotFoundException("Peer Group or Organization", f"{member_remove.peer_group_id} or {member_remove.organization_id}")

        # If organization is not a member, return appropriate message
        # If removal succeeds, return success message
        return jsonify({"message": "Organization removed from peer group successfully"}), 200
    except ValidationError as e:
        logger.error(f"Validation error removing member from peer group: {str(e)}")
        return jsonify(ValidationException(message="Invalid input", errors=e.errors()).to_dict()), 400
    except ResourceNotFoundException as e:
        logger.error(f"Peer group or organization not found: {e.message}")
        return jsonify(e.to_dict()), 404
    except Exception as e:
        logger.exception(f"Error removing member from peer group: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/<uuid:peer_group_id>/members', methods=['GET'])
@require_auth
@require_entity_access('peer_group', 'peer_group_id', 'read')
def get_members(peer_group_id: uuid.UUID):
    """Get all members of a peer group

    Args:
        peer_group_id (uuid.UUID): peer_group_id

    Returns:
        flask.Response: JSON response with list of peer group members
    """
    try:
        # Get peer group members using service layer
        members = peer_group_service.get_peer_group_members(peer_group_id)

        # If peer group not found, raise ResourceNotFoundException
        if not members:
            raise ResourceNotFoundException("Peer Group", str(peer_group_id))

        # Return list of members as JSON response
        return jsonify(members), 200
    except ResourceNotFoundException as e:
        logger.error(f"Peer group not found: {e.message}")
        return jsonify(e.to_dict()), 404
    except Exception as e:
        logger.exception(f"Error getting members of peer group: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/<uuid:peer_group_id>/members/<uuid:organization_id>', methods=['GET'])
@require_auth
@require_entity_access('peer_group', 'peer_group_id', 'read')
def check_membership(peer_group_id: uuid.UUID, organization_id: uuid.UUID):
    """Check if an organization is a member of a peer group

    Args:
        peer_group_id (uuid.UUID): peer_group_id
        organization_id (uuid.UUID): organization_id

    Returns:
        flask.Response: JSON response with membership status
    """
    try:
        # Check organization membership using service layer
        is_member = peer_group_service.check_organization_in_peer_group(peer_group_id, organization_id)

        # If peer group not found, raise ResourceNotFoundException
        if not is_member:
            raise ResourceNotFoundException("Peer Group", str(peer_group_id))

        # Return membership status as JSON response
        return jsonify({"is_member": is_member}), 200
    except ResourceNotFoundException as e:
        logger.error(f"Peer group not found: {e.message}")
        return jsonify(e.to_dict()), 404
    except Exception as e:
        logger.exception(f"Error checking membership of peer group: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/criteria', methods=['PATCH'])
@require_auth
@require_permission('peer_groups:update')
def update_criteria():
    """Update criteria for a peer group

    Returns:
        flask.Response: JSON response with updated peer group data
    """
    try:
        # Parse request JSON data
        data = request.get_json()

        # Validate data using CriteriaUpdate schema
        criteria_update = CriteriaUpdate(**data)

        # Extract peer_group_id, key, and value from request
        peer_group_id = criteria_update.peer_group_id
        key = criteria_update.key
        value = criteria_update.value

        # Get existing peer group
        peer_group = peer_group_service.get_peer_group_by_id(peer_group_id)
        if not peer_group:
            raise ResourceNotFoundException("Peer Group", str(peer_group_id))

        # Check if user has permission to update this peer group
        # Update criteria at the specified key with the new value
        criteria = peer_group.get("criteria", {})
        criteria[key] = value

        # Update peer group using service layer
        peer_group = peer_group_service.update_peer_group_criteria(peer_group_id, criteria)

        # Return updated peer group data
        return jsonify(peer_group), 200

    except ValidationError as e:
        logger.error(f"Validation error updating peer group criteria: {str(e)}")
        return jsonify(ValidationException(message="Invalid input", errors=e.errors()).to_dict()), 400
    except ResourceNotFoundException as e:
        logger.error(f"Peer group not found: {e.message}")
        return jsonify(e.to_dict()), 404
    except Exception as e:
        logger.exception(f"Error updating peer group criteria: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/search', methods=['GET'])
@require_auth
@require_organization_access('organization_id')
def search_peer_groups():
    """Search for peer groups by name

    Returns:
        flask.Response: JSON response with search results
    """
    try:
        # Parse query parameters (organization_id, query, limit, offset)
        organization_id = request.args.get('organization_id')
        query = request.args.get('query')
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)

        # Search peer groups using service layer
        peer_groups = peer_group_service.search_peer_groups(
            organization_id=organization_id,
            query=query,
            limit=limit,
            offset=offset
        )

        # Return search results as JSON response
        return jsonify(peer_groups), 200
    except Exception as e:
        logger.exception(f"Error searching peer groups: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@router.route('/organizations/<uuid:organization_id>', methods=['GET'])
@require_auth
@require_organization_access('organization_id')
def get_peer_groups_for_member(organization_id: uuid.UUID):
    """Get all peer groups an organization is a member of

    Args:
        organization_id (uuid.UUID): organization_id

    Returns:
        flask.Response: JSON response with list of peer groups
    """
    try:
        # Parse query parameter for active_only
        active_only = request.args.get('active_only', default=True, type=lambda v: v.lower() == 'true')

        # Get peer groups for member organization using service layer
        peer_groups = peer_group_service.get_peer_groups_for_member(
            organization_id=organization_id,
            active_only=active_only
        )

        # Return list of peer groups as JSON response
        return jsonify(peer_groups), 200
    except Exception as e:
        logger.exception(f"Error getting peer groups for member organization: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500