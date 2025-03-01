import uuid
from typing import List, Dict, Any, Optional

from pydantic import ValidationError
from flask import Blueprint, request, jsonify, g

from ...db.models.attorney import Attorney
from ...db.repositories.attorney_repository import AttorneyRepository
from ...api.schemas.attorneys import AttorneyCreate, AttorneyUpdate, AttorneySearchParams, AttorneyList, AttorneyOut, AttorneyWithRatesOut, UniCourtAttorneyMapping, TimekeeperIdUpdate, StaffClassAssignment, UniCourtSearchParams as AttorneyUniCourtSearchParams
from ...db.session import get_db, Session
from ...api.core.auth import require_auth, require_role, require_permission, require_organization_access, require_entity_access
from ...api.core.errors import ResourceNotFoundException, ValidationException, IntegrationException
from ...services.organizations.firm import FirmService
from ...integrations.unicourt.client import UniCourtClient
from ...utils.logging import get_logger
from ...utils.validators import validate_uuid

# Blueprint for organizing attorney-related routes
attorneys_bp = Blueprint('attorneys', __name__, url_prefix='/api/v1/attorneys')

# Initialize logger
logger = get_logger(__name__)

# Global variables for dependencies (initialized in initialize_dependencies)
attorney_repository = None
firm_service = None
unicourt_client = None


def initialize_dependencies(db_session: Session):
    """Initialize repository and service dependencies"""
    global attorney_repository, firm_service, unicourt_client
    attorney_repository = AttorneyRepository(db_session)
    firm_service = FirmService(attorney_repository=attorney_repository)
    unicourt_client = UniCourtClient(api_key='')  # TODO: Replace with actual API key
    logger.info("Dependencies initialized for attorney endpoints")


def handle_validation_error(error: ValidationError):
    """Handles pydantic validation errors and returns appropriate response"""
    exc = ValidationException(message="Invalid request data", errors=error.errors())
    return jsonify(exc.to_dict()), 400


@attorneys_bp.before_request
def before_request():
    """Initialize dependencies before each request"""
    db_session = get_db()
    g.db = db_session  # Store the database session in Flask's 'g' object
    initialize_dependencies(db_session)


@attorneys_bp.after_request
def after_request(response):
    """Clean up resources after each request"""
    if hasattr(g, 'db'):
        g.db.close()
    return response


@attorneys_bp.route('/', methods=['GET'])
@require_auth
@require_permission('attorneys:read')
def list_attorneys():
    """List attorneys with optional filtering"""
    try:
        # Parse query parameters into AttorneySearchParams
        search_params = AttorneySearchParams(**request.args)

        # Call attorney_repository.search with validated parameters
        attorneys, total = attorney_repository.search(search_params.dict(), page=search_params.page, page_size=search_params.page_size)

        # Format AttorneyList response
        attorneys_list = [AttorneyOut.from_orm(attorney).dict() for attorney in attorneys]
        result = AttorneyList(items=attorneys_list, total=total, page=search_params.page, size=search_params.page_size)

        return jsonify(result.dict())
    except ValidationError as e:
        return handle_validation_error(e)
    except Exception as e:
        logger.exception("Error listing attorneys")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/<attorney_id>', methods=['GET'])
@require_auth
@require_permission('attorneys:read')
@require_entity_access('attorney', 'attorney_id', 'read')
def get_attorney(attorney_id):
    """Get a specific attorney by ID"""
    try:
        # Call attorney_repository.get_by_id with attorney_id
        attorney = attorney_repository.get_by_id(attorney_id)

        # If attorney not found, raise ResourceNotFoundException
        if not attorney:
            raise ResourceNotFoundException(resource_type="Attorney", resource_id=attorney_id)

        # Return formatted AttorneyOut response
        result = AttorneyOut.from_orm(attorney)
        return jsonify(result.dict())
    except ValueError:
        return jsonify({'message': 'Invalid attorney_id format'}), 400
    except ResourceNotFoundException as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        logger.exception(f"Error getting attorney with ID {attorney_id}")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/', methods=['POST'])
@require_auth
@require_permission('attorneys:create')
@require_organization_access('organization_id')
def create_attorney():
    """Create a new attorney"""
    try:
        # Parse and validate request body using AttorneyCreate schema
        attorney_data = AttorneyCreate(**request.get_json())

        # Call attorney_repository.create with validated data
        attorney = attorney_repository.create(attorney_data.dict())

        # Return created attorney with 201 status code
        result = AttorneyOut.from_orm(attorney)
        return jsonify(result.dict()), 201
    except ValidationError as e:
        return handle_validation_error(e)
    except Exception as e:
        logger.exception("Error creating attorney")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/<attorney_id>', methods=['PUT'])
@require_auth
@require_permission('attorneys:update')
@require_entity_access('attorney', 'attorney_id', 'update')
def update_attorney(attorney_id):
    """Update an existing attorney"""
    try:
        # Parse and validate request body using AttorneyUpdate schema
        update_data = AttorneyUpdate(**request.get_json())

        # Call attorney_repository.update with attorney_id and validated data
        attorney = attorney_repository.update(attorney_id, update_data.dict(exclude_unset=True))

        # If attorney not found, raise ResourceNotFoundException
        if not attorney:
            raise ResourceNotFoundException(resource_type="Attorney", resource_id=attorney_id)

        # Return updated attorney
        result = AttorneyOut.from_orm(attorney)
        return jsonify(result.dict())
    except ValueError:
        return jsonify({'message': 'Invalid attorney_id format'}), 400
    except ResourceNotFoundException as e:
        return jsonify(e.to_dict()), e.status_code
    except ValidationError as e:
        return handle_validation_error(e)
    except Exception as e:
        logger.exception(f"Error updating attorney with ID {attorney_id}")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/<attorney_id>', methods=['DELETE'])
@require_auth
@require_permission('attorneys:delete')
@require_entity_access('attorney', 'attorney_id', 'delete')
def delete_attorney(attorney_id):
    """Delete an attorney"""
    try:
        # Call attorney_repository.delete with attorney_id
        deleted = attorney_repository.delete(attorney_id)

        # If attorney not found, raise ResourceNotFoundException
        if not deleted:
            raise ResourceNotFoundException(resource_type="Attorney", resource_id=attorney_id)

        # Return success message
        return jsonify({'message': 'Attorney deleted successfully'})
    except ValueError:
        return jsonify({'message': 'Invalid attorney_id format'}), 400
    except ResourceNotFoundException as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        logger.exception(f"Error deleting attorney with ID {attorney_id}")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/<attorney_id>/rates', methods=['GET'])
@require_auth
@require_permission('rates:read')
@require_entity_access('attorney', 'attorney_id', 'read')
def get_attorney_rates(attorney_id):
    """Get rates for a specific attorney"""
    try:
        client_id = request.args.get('client_id')
        if client_id:
            validate_uuid(client_id, "client_id")

        # Call attorney_repository.get_with_rates with attorney_id and client_id
        attorney, rates = attorney_repository.get_with_rates(attorney_id, client_id)

        # If attorney not found, raise ResourceNotFoundException
        if not attorney:
            raise ResourceNotFoundException(resource_type="Attorney", resource_id=attorney_id)

        # Return formatted AttorneyWithRatesOut response
        result = AttorneyWithRatesOut(attorney=AttorneyOut.from_orm(attorney), rates=[rate.to_dict() for rate in rates])
        return jsonify(result.dict())
    except ValueError:
        return jsonify({'message': 'Invalid attorney_id or client_id format'}), 400
    except ResourceNotFoundException as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        logger.exception(f"Error getting rates for attorney with ID {attorney_id}")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/timekeeper-id', methods=['POST'])
@require_auth
@require_permission('attorneys:update')
@require_entity_access('attorney', 'attorney_id', 'update')
def update_timekeeper_id():
    """Add a client-specific timekeeper ID for an attorney"""
    try:
        # Parse and validate request body using TimekeeperIdUpdate schema
        timekeeper_data = TimekeeperIdUpdate(**request.get_json())

        # Call attorney_repository.add_timekeeper_id with validated data
        attorney = attorney_repository.add_timekeeper_id(timekeeper_data.attorney_id, timekeeper_data.client_id, timekeeper_data.timekeeper_id)

        # If attorney not found, raise ResourceNotFoundException
        if not attorney:
            raise ResourceNotFoundException(resource_type="Attorney", resource_id=timekeeper_data.attorney_id)

        # Return updated attorney
        result = AttorneyOut.from_orm(attorney)
        return jsonify(result.dict())
    except ValueError:
        return jsonify({'message': 'Invalid attorney_id or client_id format'}), 400
    except ResourceNotFoundException as e:
        return jsonify(e.to_dict()), e.status_code
    except ValidationError as e:
        return handle_validation_error(e)
    except Exception as e:
        logger.exception("Error updating timekeeper ID")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/staff-class', methods=['POST'])
@require_auth
@require_permission('attorneys:update')
@require_entity_access('attorney', 'attorney_id', 'update')
def assign_staff_class():
    """Assign a staff class to an attorney"""
    try:
        # Parse and validate request body using StaffClassAssignment schema
        staff_class_data = StaffClassAssignment(**request.get_json())

        # Call attorney_repository.assign_staff_class with validated data
        attorney = attorney_repository.assign_staff_class(staff_class_data.attorney_id, staff_class_data.staff_class_id)

        # If attorney or staff class not found, raise ResourceNotFoundException
        if not attorney:
            raise ResourceNotFoundException(resource_type="Attorney", resource_id=staff_class_data.attorney_id)

        # Return updated attorney
        result = AttorneyOut.from_orm(attorney)
        return jsonify(result.dict())
    except ValueError:
        return jsonify({'message': 'Invalid attorney_id or staff_class_id format'}), 400
    except ResourceNotFoundException as e:
        return jsonify(e.to_dict()), e.status_code
    except ValidationError as e:
        return handle_validation_error(e)
    except Exception as e:
        logger.exception("Error assigning staff class")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/without-staff-class', methods=['GET'])
@require_auth
@require_permission('attorneys:read')
@require_organization_access('organization_id')
def get_attorneys_without_staff_class():
    """Get attorneys without assigned staff classes"""
    try:
        organization_id = request.args.get('organization_id')
        if not organization_id:
            return jsonify({'message': 'organization_id is required'}), 400
        validate_uuid(organization_id, "organization_id")

        # Call attorney_repository.get_without_staff_class with organization_id
        attorneys = attorney_repository.get_without_staff_class(organization_id)

        # Return list of attorneys
        result = [AttorneyOut.from_orm(attorney).dict() for attorney in attorneys]
        return jsonify(result)
    except ValueError:
        return jsonify({'message': 'Invalid organization_id format'}), 400
    except Exception as e:
        logger.exception("Error getting attorneys without staff class")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/<attorney_id>/auto-assign-staff-class', methods=['POST'])
@require_auth
@require_permission('attorneys:update')
@require_entity_access('attorney', 'attorney_id', 'update')
def auto_assign_staff_class(attorney_id):
    """Automatically find and assign an eligible staff class to an attorney"""
    try:
        organization_id = request.args.get('organization_id')
        if not organization_id:
            return jsonify({'message': 'organization_id is required'}), 400
        validate_uuid(attorney_id, "attorney_id")
        validate_uuid(organization_id, "organization_id")

        # Call attorney_repository.find_eligible_staff_class with attorney_id and organization_id
        staff_class = attorney_repository.find_eligible_staff_class(attorney_id, organization_id)

        if not staff_class:
            return jsonify({'message': 'No eligible staff class found'}), 404

        # Assign staff class to attorney
        attorney = attorney_repository.assign_staff_class(attorney_id, staff_class.id)

        # Return updated attorney
        result = AttorneyOut.from_orm(attorney)
        return jsonify(result.dict())
    except ValueError:
        return jsonify({'message': 'Invalid attorney_id or organization_id format'}), 400
    except ResourceNotFoundException as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        logger.exception("Error auto-assigning staff class")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/unicourt/search', methods=['POST'])
@require_auth
@require_permission('integrations:unicourt')
def search_unicourt_attorneys():
    """Search for attorneys in UniCourt"""
    try:
        # Parse and validate request body using UniCourtSearchParams schema
        search_params = AttorneyUniCourtSearchParams(**request.get_json())

        # Call unicourt_client.search_attorneys with search parameters
        attorneys = unicourt_client.search_attorneys(name=search_params.name, bar_number=search_params.bar_number, state=search_params.state, additional_params={'limit': search_params.limit})

        # Return search results
        return jsonify(attorneys)
    except ValidationError as e:
        return handle_validation_error(e)
    except IntegrationException as e:
        return jsonify({'message': str(e)}), 500
    except Exception as e:
        logger.exception("Error searching UniCourt attorneys")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/unicourt/<unicourt_id>', methods=['GET'])
@require_auth
@require_permission('integrations:unicourt')
def get_unicourt_attorney(unicourt_id):
    """Get attorney details from UniCourt"""
    try:
        # Call unicourt_client.get_attorney_details with unicourt_id
        attorney = unicourt_client.get_attorney_details(unicourt_id)

        # Return attorney details
        return jsonify(attorney)
    except IntegrationException as e:
        return jsonify({'message': str(e)}), 500
    except Exception as e:
        logger.exception("Error getting UniCourt attorney details")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/unicourt/<unicourt_id>/performance', methods=['GET'])
@require_auth
@require_permission('integrations:unicourt')
def get_unicourt_attorney_performance(unicourt_id):
    """Get attorney performance data from UniCourt"""
    try:
        # Call unicourt_client.get_attorney_performance with unicourt_id
        performance = unicourt_client.get_attorney_performance(unicourt_id)

        # Return performance data
        return jsonify(performance)
    except IntegrationException as e:
        return jsonify({'message': str(e)}), 500
    except Exception as e:
        logger.exception("Error getting UniCourt attorney performance data")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/unicourt/map', methods=['POST'])
@require_auth
@require_permission('integrations:unicourt')
@require_entity_access('attorney', 'attorney_id', 'update')
def map_unicourt_attorney():
    """Map a Justice Bid attorney to a UniCourt attorney"""
    try:
        # Parse and validate request body using UniCourtAttorneyMapping schema
        mapping_data = UniCourtAttorneyMapping(**request.get_json())

        # Update attorney with UniCourt data
        if mapping_data.fetch_performance_data:
            attorney = unicourt_client.sync_attorney_data(mapping_data.attorney_id, mapping_data.unicourt_id)
        else:
            attorney = attorney_repository.update_unicourt_data(mapping_data.attorney_id, mapping_data.unicourt_id, {})

        # Return updated attorney
        result = AttorneyOut.from_orm(attorney)
        return jsonify(result.dict())
    except ValueError:
        return jsonify({'message': 'Invalid attorney_id or unicourt_id format'}), 400
    except ResourceNotFoundException as e:
        return jsonify(e.to_dict()), e.status_code
    except ValidationError as e:
        return handle_validation_error(e)
    except IntegrationException as e:
        return jsonify({'message': str(e)}), 500
    except Exception as e:
        logger.exception("Error mapping UniCourt attorney")
        return jsonify({'message': 'Internal server error'}), 500


@attorneys_bp.route('/bulk-import', methods=['POST'])
@require_auth
@require_permission('attorneys:create')
@require_organization_access('organization_id')
def bulk_import_attorneys():
    """Bulk import attorneys for an organization"""
    try:
        organization_id = request.args.get('organization_id')
        if not organization_id:
            return jsonify({'message': 'organization_id is required'}), 400
        validate_uuid(organization_id, "organization_id")

        auto_assign_staff_class = request.args.get('auto_assign_staff_class', 'True').lower() == 'true'

        # Parse request body as a list of attorney data
        attorneys_data = request.get_json()
        if not isinstance(attorneys_data, list):
            return jsonify({'message': 'Request body must be a list of attorney data'}), 400

        # Call attorney_repository.bulk_import with data and organization_id
        imported_attorneys, error_records = attorney_repository.bulk_import(attorneys_data, organization_id, auto_assign_staff_class)

        # Construct import summary
        result = {
            'total': len(attorneys_data),
            'successful': len(imported_attorneys),
            'failed': len(error_records),
            'errors': error_records
        }

        # Return import summary
        return jsonify(result)
    except ValueError:
        return jsonify({'message': 'Invalid organization_id format'}), 400
    except Exception as e:
        logger.exception("Error during bulk import of attorneys")
        return jsonify({'message': 'Internal server error'}), 500

exports = [attorneys_bp]