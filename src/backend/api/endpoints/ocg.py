"""
API endpoints for managing Outside Counsel Guidelines (OCGs).

This module defines RESTful API endpoints for creating, retrieving, updating, and deleting
Outside Counsel Guidelines (OCGs) in the Justice Bid Rate Negotiation System. These endpoints
enable clients to define rules and requirements for law firms, including negotiable sections
with alternative language options that have associated point values.
"""

from flask import Blueprint, request, jsonify
from uuid import UUID

from ...db.repositories.ocg_repository import OCGRepository
from ..schemas.ocg import validate_ocg_data
from ...utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create blueprint for OCG endpoints
OCG_BP = Blueprint('ocg', __name__)


@OCG_BP.route('/ocg', methods=['POST'])
def create_ocg_endpoint():
    """
    Create a new Outside Counsel Guideline (OCG).
    
    This endpoint processes POST requests to create a new OCG based on the provided data.
    The request must include client_id, name, and can optionally include version,
    total_points, and default_firm_point_budget.
    
    Returns:
        JSON response with the created OCG data and 201 status code on success,
        or an error message with appropriate status code on failure.
    """
    try:
        # Extract JSON payload from request
        ocg_data = request.get_json()
        
        # Validate OCG data
        validated_data = validate_ocg_data(ocg_data, 'create')
        
        # Initialize repository and create OCG
        ocg_repo = OCGRepository()
        new_ocg = ocg_repo.create(
            client_id=UUID(validated_data['client_id']),
            name=validated_data['name'],
            version=validated_data.get('version', 1),
            total_points=validated_data.get('total_points', 10),
            default_firm_point_budget=validated_data.get('default_firm_point_budget', 5),
            settings=validated_data.get('settings')
        )
        
        # Log success
        logger.info(
            f"Created new OCG '{new_ocg.name}' for client {new_ocg.client_id}",
            extra={"additional_data": {"ocg_id": str(new_ocg.id)}}
        )
        
        # Return created OCG with 201 status code
        return jsonify({
            'id': str(new_ocg.id),
            'client_id': str(new_ocg.client_id),
            'name': new_ocg.name,
            'version': new_ocg.version,
            'status': new_ocg.status.value,
            'total_points': new_ocg.total_points,
            'default_firm_point_budget': new_ocg.default_firm_point_budget,
            'created_at': new_ocg.created_at.isoformat(),
            'updated_at': new_ocg.updated_at.isoformat()
        }), 201
        
    except ValueError as e:
        # Log and return validation errors
        logger.warning(f"Validation error in OCG creation: {str(e)}")
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
        
    except Exception as e:
        # Log and return unexpected errors
        logger.error(f"Error creating OCG: {str(e)}")
        return jsonify({'error': 'Server error', 'message': 'Failed to create OCG'}), 500


@OCG_BP.route('/ocg/<string:ocg_id>', methods=['GET'])
def get_ocg_endpoint(ocg_id):
    """
    Retrieve an existing Outside Counsel Guideline (OCG) by ID.
    
    This endpoint processes GET requests to retrieve an OCG using its unique identifier.
    
    Args:
        ocg_id (str): Unique identifier of the OCG to retrieve
        
    Returns:
        JSON response with the OCG data if found, or an error message with 404 status code if not found.
    """
    try:
        # Initialize repository and get OCG by ID
        ocg_repo = OCGRepository()
        ocg = ocg_repo.get_by_id(UUID(ocg_id))
        
        if not ocg:
            # Log and return 404 if OCG not found
            logger.info(f"OCG with ID {ocg_id} not found")
            return jsonify({'error': 'Not found', 'message': 'OCG not found'}), 404
        
        # Return OCG data
        return jsonify({
            'id': str(ocg.id),
            'client_id': str(ocg.client_id),
            'name': ocg.name,
            'version': ocg.version,
            'status': ocg.status.value,
            'total_points': ocg.total_points,
            'default_firm_point_budget': ocg.default_firm_point_budget,
            'created_at': ocg.created_at.isoformat(),
            'updated_at': ocg.updated_at.isoformat(),
            'published_at': ocg.published_at.isoformat() if ocg.published_at else None,
            'signed_at': ocg.signed_at.isoformat() if ocg.signed_at else None
        }), 200
        
    except ValueError as e:
        # Log and return validation errors (e.g., invalid UUID)
        logger.warning(f"Invalid OCG ID format: {ocg_id}")
        return jsonify({'error': 'Validation error', 'message': 'Invalid OCG ID format'}), 400
        
    except Exception as e:
        # Log and return unexpected errors
        logger.error(f"Error retrieving OCG {ocg_id}: {str(e)}")
        return jsonify({'error': 'Server error', 'message': 'Failed to retrieve OCG'}), 500


@OCG_BP.route('/ocg/<string:ocg_id>', methods=['PUT'])
def update_ocg_endpoint(ocg_id):
    """
    Update an existing Outside Counsel Guideline (OCG).
    
    This endpoint processes PUT requests to update an existing OCG identified by its unique ID.
    The request must include the updated OCG data in JSON format.
    
    Args:
        ocg_id (str): Unique identifier of the OCG to update
        
    Returns:
        JSON response with the updated OCG data if successful,
        or an error message with appropriate status code on failure.
    """
    try:
        # Extract JSON payload from request
        update_data = request.get_json()
        
        # Validate update data
        validated_data = validate_ocg_data(update_data, 'update')
        
        # Initialize repository and update OCG
        ocg_repo = OCGRepository()
        updated_ocg = ocg_repo.update(UUID(ocg_id), validated_data)
        
        if not updated_ocg:
            # Log and return 404 if OCG not found
            logger.info(f"OCG with ID {ocg_id} not found for update")
            return jsonify({'error': 'Not found', 'message': 'OCG not found'}), 404
        
        # Log success
        logger.info(
            f"Updated OCG '{updated_ocg.name}' (ID: {ocg_id})",
            extra={"additional_data": {"fields_updated": list(validated_data.keys())}}
        )
        
        # Return updated OCG
        return jsonify({
            'id': str(updated_ocg.id),
            'client_id': str(updated_ocg.client_id),
            'name': updated_ocg.name,
            'version': updated_ocg.version,
            'status': updated_ocg.status.value,
            'total_points': updated_ocg.total_points,
            'default_firm_point_budget': updated_ocg.default_firm_point_budget,
            'created_at': updated_ocg.created_at.isoformat(),
            'updated_at': updated_ocg.updated_at.isoformat()
        }), 200
        
    except ValueError as e:
        # Log and return validation errors
        logger.warning(f"Validation error in OCG update: {str(e)}")
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
        
    except Exception as e:
        # Log and return unexpected errors
        logger.error(f"Error updating OCG {ocg_id}: {str(e)}")
        return jsonify({'error': 'Server error', 'message': 'Failed to update OCG'}), 500


@OCG_BP.route('/ocg/<string:ocg_id>', methods=['DELETE'])
def delete_ocg_endpoint(ocg_id):
    """
    Delete an existing Outside Counsel Guideline (OCG).
    
    This endpoint processes DELETE requests to remove an OCG from the system.
    
    Args:
        ocg_id (str): Unique identifier of the OCG to delete
        
    Returns:
        JSON response confirming deletion with 200 status code if successful,
        or an error message with appropriate status code on failure.
    """
    try:
        # Initialize repository and delete OCG
        ocg_repo = OCGRepository()
        result = ocg_repo.delete(UUID(ocg_id))
        
        if not result:
            # Log and return 404 if OCG not found
            logger.info(f"OCG with ID {ocg_id} not found for deletion")
            return jsonify({'error': 'Not found', 'message': 'OCG not found'}), 404
        
        # Log success
        logger.info(f"Deleted OCG with ID {ocg_id}")
        
        # Return success message
        return jsonify({
            'message': 'OCG deleted successfully',
            'id': ocg_id
        }), 200
        
    except ValueError as e:
        # Log and return validation errors (e.g., invalid UUID)
        logger.warning(f"Invalid OCG ID format: {ocg_id}")
        return jsonify({'error': 'Validation error', 'message': 'Invalid OCG ID format'}), 400
        
    except Exception as e:
        # Log and return unexpected errors
        logger.error(f"Error deleting OCG {ocg_id}: {str(e)}")
        return jsonify({'error': 'Server error', 'message': 'Failed to delete OCG'}), 500


@OCG_BP.route('/ocg/<string:ocg_id>/publish', methods=['POST'])
def publish_ocg_endpoint(ocg_id):
    """
    Publish an OCG, changing its status from Draft to Published.
    
    This endpoint processes POST requests to publish an OCG, making it available for negotiation.
    
    Args:
        ocg_id (str): Unique identifier of the OCG to publish
        
    Returns:
        JSON response with the updated OCG data if successful,
        or an error message with appropriate status code on failure.
    """
    try:
        # Initialize repository
        ocg_repo = OCGRepository()
        
        # Get OCG and verify it exists
        ocg = ocg_repo.get_by_id(UUID(ocg_id))
        if not ocg:
            logger.info(f"OCG with ID {ocg_id} not found for publishing")
            return jsonify({'error': 'Not found', 'message': 'OCG not found'}), 404
        
        # Update OCG status to Published
        updated_ocg = ocg_repo.update_ocg_status(UUID(ocg_id), 'PUBLISHED')
        
        if not updated_ocg:
            logger.warning(f"Failed to publish OCG {ocg_id}")
            return jsonify({'error': 'Processing error', 'message': 'Failed to publish OCG'}), 422
        
        # Log success
        logger.info(f"Published OCG '{updated_ocg.name}' (ID: {ocg_id})")
        
        # Return updated OCG
        return jsonify({
            'id': str(updated_ocg.id),
            'client_id': str(updated_ocg.client_id),
            'name': updated_ocg.name,
            'version': updated_ocg.version,
            'status': updated_ocg.status.value,
            'published_at': updated_ocg.published_at.isoformat() if updated_ocg.published_at else None,
            'message': 'OCG published successfully'
        }), 200
        
    except ValueError as e:
        logger.warning(f"Validation error in OCG publishing: {str(e)}")
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
        
    except Exception as e:
        logger.error(f"Error publishing OCG {ocg_id}: {str(e)}")
        return jsonify({'error': 'Server error', 'message': 'Failed to publish OCG'}), 500


@OCG_BP.route('/ocg/<string:ocg_id>/sections', methods=['GET'])
def get_ocg_sections_endpoint(ocg_id):
    """
    Retrieve all sections for an OCG.
    
    This endpoint processes GET requests to retrieve the sections of an OCG,
    including negotiable sections and their alternatives.
    
    Args:
        ocg_id (str): Unique identifier of the OCG
        
    Returns:
        JSON response with the OCG sections if found,
        or an error message with appropriate status code on failure.
    """
    try:
        # Initialize repository
        ocg_repo = OCGRepository()
        
        # Get OCG sections hierarchy
        sections = ocg_repo.get_section_hierarchy(UUID(ocg_id))
        
        if sections is None:
            logger.info(f"OCG with ID {ocg_id} not found")
            return jsonify({'error': 'Not found', 'message': 'OCG not found'}), 404
        
        # Format sections for response
        formatted_sections = []
        for section in sections:
            section_data = {
                'id': str(section.id),
                'title': section.title,
                'content': section.content,
                'is_negotiable': section.is_negotiable,
                'order': section.order,
                'alternatives': [],
                'subsections': []
            }
            
            # Add alternatives if section is negotiable
            if section.is_negotiable:
                for alt in section.alternatives:
                    section_data['alternatives'].append({
                        'id': str(alt.id),
                        'title': alt.title,
                        'content': alt.content,
                        'points': alt.points,
                        'is_default': alt.is_default,
                        'order': alt.order
                    })
            
            # Add subsections recursively
            for subsection in section.subsections:
                subsection_data = {
                    'id': str(subsection.id),
                    'title': subsection.title,
                    'content': subsection.content,
                    'is_negotiable': subsection.is_negotiable,
                    'order': subsection.order,
                    'alternatives': [],
                    'parent_id': str(section.id)
                }
                
                # Add alternatives for subsection
                if subsection.is_negotiable:
                    for alt in subsection.alternatives:
                        subsection_data['alternatives'].append({
                            'id': str(alt.id),
                            'title': alt.title,
                            'content': alt.content,
                            'points': alt.points,
                            'is_default': alt.is_default,
                            'order': alt.order
                        })
                
                section_data['subsections'].append(subsection_data)
            
            formatted_sections.append(section_data)
        
        return jsonify({
            'ocg_id': ocg_id,
            'sections': formatted_sections
        }), 200
        
    except ValueError as e:
        logger.warning(f"Invalid OCG ID format: {ocg_id}")
        return jsonify({'error': 'Validation error', 'message': 'Invalid OCG ID format'}), 400
        
    except Exception as e:
        logger.error(f"Error retrieving OCG sections for {ocg_id}: {str(e)}")
        return jsonify({'error': 'Server error', 'message': 'Failed to retrieve OCG sections'}), 500


@OCG_BP.route('/ocg/client/<string:client_id>', methods=['GET'])
def get_client_ocgs_endpoint(client_id):
    """
    Retrieve all OCGs for a specific client.
    
    This endpoint processes GET requests to retrieve all OCGs belonging to a client,
    with optional pagination parameters.
    
    Args:
        client_id (str): Unique identifier of the client
        
    Query Parameters:
        limit (int, optional): Maximum number of OCGs to return
        offset (int, optional): Number of OCGs to skip
        
    Returns:
        JSON response with the client's OCGs if found,
        or an error message with appropriate status code on failure.
    """
    try:
        # Get pagination parameters from query string
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Initialize repository and get OCGs
        ocg_repo = OCGRepository()
        ocgs = ocg_repo.get_by_client(UUID(client_id), limit, offset)
        
        # Format OCGs for response
        formatted_ocgs = []
        for ocg in ocgs:
            formatted_ocgs.append({
                'id': str(ocg.id),
                'name': ocg.name,
                'version': ocg.version,
                'status': ocg.status.value,
                'total_points': ocg.total_points,
                'default_firm_point_budget': ocg.default_firm_point_budget,
                'created_at': ocg.created_at.isoformat(),
                'updated_at': ocg.updated_at.isoformat(),
                'published_at': ocg.published_at.isoformat() if ocg.published_at else None,
                'signed_at': ocg.signed_at.isoformat() if ocg.signed_at else None
            })
        
        return jsonify({
            'client_id': client_id,
            'ocgs': formatted_ocgs,
            'limit': limit,
            'offset': offset,
            'total': len(formatted_ocgs)  # Ideally this would be a separate count query
        }), 200
        
    except ValueError as e:
        logger.warning(f"Invalid client ID format: {client_id}")
        return jsonify({'error': 'Validation error', 'message': 'Invalid client ID format'}), 400
        
    except Exception as e:
        logger.error(f"Error retrieving OCGs for client {client_id}: {str(e)}")
        return jsonify({'error': 'Server error', 'message': 'Failed to retrieve client OCGs'}), 500