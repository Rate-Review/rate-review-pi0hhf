"""
API endpoints for managing messages in the Justice Bid Rate Negotiation System.
Provides routes for creating, retrieving, and managing secure messages between law firms and clients,
supporting hierarchical message threading and negotiation-specific communications.
"""
from typing import List

from flask import Blueprint, request, jsonify  # flask 2.2.0+
from flask_jwt_extended import jwt_required, get_jwt_identity  # flask_jwt_extended

from ..core.auth import require_permission  # src/backend/api/core/auth.py
from ..core.errors import APIError, ResourceNotFoundException, ValidationException  # src/backend/api/core/errors.py
from ..schemas.messages import MessageCreate, MessageResponse, MessageUpdate, MessageList, MessageThreadResponse, MessageFilterParams  # src/backend/api/schemas/messages.py
from ...db.repositories.message_repository import MessageRepository  # src/backend/db/repositories/message_repository.py
from ...services.messaging.thread import ThreadService  # src/backend/services/messaging/thread.py
from ...services.messaging.in_app import InAppMessageService  # src/backend/services/messaging/in_app.py
from ...services.messaging.notifications import NotificationManager  # src/backend/services/messaging/notifications.py
from ...utils.logging import get_logger  # src/backend/utils/logging.py

# Initialize Flask Blueprint for messages
messages_bp = Blueprint('messages', __name__)

# Initialize logger
logger = get_logger(__name__)

# Initialize data repositories and services
message_repository = MessageRepository()
thread_service = ThreadService()
in_app_service = InAppMessageService()
notification_manager = NotificationManager()


@messages_bp.route('', methods=['GET'])
@jwt_required()
@require_permission('messages:read')
def get_messages():
    """Get a list of messages with filtering options"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Parse query parameters for filtering
        thread_id = request.args.get('thread_id')
        related_entity_type = request.args.get('related_entity_type')
        related_entity_id = request.args.get('related_entity_id')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Construct filter parameters
        filter_params = {
            'thread_id': thread_id,
            'related_entity_type': related_entity_type,
            'related_entity_id': related_entity_id
        }

        # Validate filter parameters using MessageFilterParams schema
        validated_params = MessageFilterParams(**filter_params)

        # Query message repository for messages based on filters
        messages, total = message_repository.get_messages(
            user_id=user_id,
            thread_id=validated_params.thread_id,
            related_entity_type=validated_params.related_entity_type,
            related_entity_id=validated_params.related_entity_id,
            page=page,
            per_page=per_page
        )

        # Construct response using MessageList schema
        message_list = MessageList(
            items=[MessageResponse(**message.to_dict()) for message in messages],
            total=total,
            page=page,
            size=per_page,
            status="success"
        )

        # Return paginated message list
        return jsonify(message_list.dict()), 200

    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        return jsonify({'message': 'Failed to retrieve messages'}), 500


@messages_bp.route('', methods=['POST'])
@jwt_required()
@require_permission('messages:create')
def create_message():
    """Create a new message"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Validate request body using MessageCreate schema
        message_data = request.get_json()
        message_create = MessageCreate(**message_data)

        # Create message using message repository
        message = message_repository.create_message(
            sender_id=user_id,
            thread_id=message_create.thread_id,
            content=message_create.content,
            parent_id=message_create.parent_id,
            recipient_ids=message_create.recipient_ids,
            attachments=message_create.attachments,
            related_entity_type=message_create.related_entity_type,
            related_entity_id=message_create.related_entity_id
        )

        # Generate notifications for message recipients
        notification_manager.notify_message(message.id)

        # Construct response using MessageResponse schema
        message_response = MessageResponse(**message.to_dict())

        # Return created message
        return jsonify(message_response.dict()), 201

    except ValidationException as e:
        logger.warning(f"Validation error creating message: {e}")
        return jsonify({'message': 'Validation error', 'errors': e.errors}), 400
    except Exception as e:
        logger.error(f"Error creating message: {e}")
        return jsonify({'message': 'Failed to create message'}), 500


@messages_bp.route('/<uuid:message_id>', methods=['GET'])
@jwt_required()
@require_permission('messages:read')
def get_message(message_id: str):
    """Get a specific message by ID"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Retrieve message from repository
        message = message_repository.get_message_by_id(message_id)

        # Return 404 if message not found
        if not message:
            raise ResourceNotFoundException("Message", message_id)

        # Mark message as read for current user
        message_repository.mark_as_read(message_id, user_id)

        # Construct response using MessageResponse schema
        message_response = MessageResponse(**message.to_dict())

        # Return message details
        return jsonify(message_response.dict()), 200

    except ResourceNotFoundException as e:
        logger.warning(f"Message not found: {e}")
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Error retrieving message: {e}")
        return jsonify({'message': 'Failed to retrieve message'}), 500


@messages_bp.route('/<uuid:message_id>', methods=['PATCH'])
@jwt_required()
@require_permission('messages:update')
def update_message(message_id: str):
    """Update a message (typically marking as read)"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Validate request body using MessageUpdate schema
        update_data = request.get_json()
        message_update = MessageUpdate(**update_data)

        # Retrieve message from repository
        message = message_repository.get_message_by_id(message_id)

        # Return 404 if message not found
        if not message:
            raise ResourceNotFoundException("Message", message_id)

        # Update message (typically setting is_read flag)
        message = message_repository.update_message(message_id, message_update.dict())

        # Construct response using MessageResponse schema
        message_response = MessageResponse(**message.to_dict())

        # Return updated message
        return jsonify(message_response.dict()), 200

    except ResourceNotFoundException as e:
        logger.warning(f"Message not found: {e}")
        return jsonify({'message': str(e)}), 404
    except ValidationException as e:
        logger.warning(f"Validation error updating message: {e}")
        return jsonify({'message': 'Validation error', 'errors': e.errors}), 400
    except Exception as e:
        logger.error(f"Error updating message: {e}")
        return jsonify({'message': 'Failed to update message'}), 500


@messages_bp.route('/<uuid:message_id>', methods=['DELETE'])
@jwt_required()
@require_permission('messages:delete')
def delete_message(message_id: str):
    """Delete a message (soft delete)"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Delete message using message repository
        success = message_repository.delete_message(message_id)

        # Return 404 if message not found
        if not success:
            raise ResourceNotFoundException("Message", message_id)

        # Return success message
        return jsonify({'message': 'Message deleted successfully'}), 200

    except ResourceNotFoundException as e:
        logger.warning(f"Message not found: {e}")
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        return jsonify({'message': 'Failed to delete message'}), 500


@messages_bp.route('/thread/<uuid:thread_id>', methods=['GET'])
@jwt_required()
@require_permission('messages:read')
def get_thread_messages(thread_id: str):
    """Get messages in a specific thread with hierarchical structure"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Get messages from thread using thread service
        thread_data = thread_service.get_thread_messages(thread_id, user_id, page, per_page)

        # Construct response using MessageThreadResponse schema
        message_thread_response = MessageThreadResponse(**thread_data)

        # Return thread with messages
        return jsonify(message_thread_response.dict()), 200

    except Exception as e:
        logger.error(f"Error retrieving thread messages: {e}")
        return jsonify({'message': 'Failed to retrieve thread messages'}), 500


@messages_bp.route('/thread/<uuid:thread_id>', methods=['POST'])
@jwt_required()
@require_permission('messages:create')
def add_thread_message(thread_id: str):
    """Add a new message to an existing thread"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Validate request body using MessageCreate schema
        message_data = request.get_json()
        message_create = MessageCreate(**message_data)

        # Add message to thread using thread service
        message = thread_service.add_message_to_thread(
            thread_id=thread_id,
            sender_id=user_id,
            content=message_create.content,
            parent_id=message_create.parent_id,
            attachments=message_create.attachments,
            related_entity_type=message_create.related_entity_type,
            related_entity_id=message_create.related_entity_id
        )

        # Construct response using MessageResponse schema
        message_response = MessageResponse(**message)

        # Return created message
        return jsonify(message_response.dict()), 201

    except ValidationException as e:
        logger.warning(f"Validation error adding message to thread: {e}")
        return jsonify({'message': 'Validation error', 'errors': e.errors}), 400
    except Exception as e:
        logger.error(f"Error adding message to thread: {e}")
        return jsonify({'message': 'Failed to add message to thread'}), 500


@messages_bp.route('/thread/<uuid:thread_id>/read', methods=['POST'])
@jwt_required()
@require_permission('messages:update')
def mark_thread_read(thread_id: str):
    """Mark all messages in a thread as read"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Mark thread as read using thread service
        success = thread_service.mark_thread_read(thread_id, user_id)

        # Return 404 if thread not found
        if not success:
            raise ResourceNotFoundException("Thread", thread_id)

        # Return success message
        return jsonify({'message': 'Thread marked as read'}), 200

    except ResourceNotFoundException as e:
        logger.warning(f"Thread not found: {e}")
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Error marking thread as read: {e}")
        return jsonify({'message': 'Failed to mark thread as read'}), 500


@messages_bp.route('/threads', methods=['GET'])
@jwt_required()
@require_permission('messages:read')
def get_user_threads():
    """Get message threads for the current user"""
    try:
        # Extract user ID and organization ID from JWT token
        user_id = get_jwt_identity()
        organization_id = get_jwt_identity()['organization_id']

        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Parse filter parameters for threads
        filters = {}  # TODO: Implement thread filtering

        # Get threads for user using thread service
        threads = thread_service.get_threads_for_user(user_id, organization_id, page, per_page, filters)

        # Construct response using MessageThreadList schema
        message_thread_list = MessageThreadList(**threads)

        # Return paginated thread list
        return jsonify(message_thread_list.dict()), 200

    except Exception as e:
        logger.error(f"Error retrieving user threads: {e}")
        return jsonify({'message': 'Failed to retrieve user threads'}), 500


@messages_bp.route('/negotiation/<uuid:negotiation_id>/threads', methods=['GET'])
@jwt_required()
@require_permission('messages:read')
def get_negotiation_threads(negotiation_id: str):
    """Get message threads related to a specific negotiation"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Get threads for negotiation using thread service
        threads = thread_service.get_threads_for_negotiation(negotiation_id, user_id, page, per_page)

        # Construct response using MessageThreadList schema
        message_thread_list = MessageThreadList(**threads)

        # Return paginated thread list
        return jsonify(message_thread_list.dict()), 200

    except Exception as e:
        logger.error(f"Error retrieving negotiation threads: {e}")
        return jsonify({'message': 'Failed to retrieve negotiation threads'}), 500


@messages_bp.route('/negotiation/<uuid:negotiation_id>', methods=['GET'])
@jwt_required()
@require_permission('messages:read')
def get_negotiation_messages(negotiation_id: str):
    """Get messages related to a specific negotiation"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Get messages for negotiation using message repository
        messages, total = message_repository.get_messages_by_negotiation_id(negotiation_id, page, per_page)

        # Construct response using MessageList schema
        message_list = MessageList(
            items=[MessageResponse(**message.to_dict()) for message in messages],
            total=total,
            page=page,
            size=per_page,
            status="success"
        )

        # Return paginated message list
        return jsonify(message_list.dict()), 200

    except Exception as e:
        logger.error(f"Error retrieving negotiation messages: {e}")
        return jsonify({'message': 'Failed to retrieve negotiation messages'}), 500


@messages_bp.route('/search', methods=['GET'])
@jwt_required()
@require_permission('messages:read')
def search_messages():
    """Search messages using free text search"""
    try:
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Parse search term from query parameters
        search_term = request.args.get('q', '')

        # Parse pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Parse additional filter parameters
        filters = {}  # TODO: Implement message filtering

        # Search messages using message repository
        messages, total = message_repository.search_messages(search_term, filters, page, per_page)

        # Construct response using MessageList schema
        message_list = MessageList(
            items=[MessageResponse(**message.to_dict()) for message in messages],
            total=total,
            page=page,
            size=per_page,
            status="success"
        )

        # Return paginated search results
        return jsonify(message_list.dict()), 200

    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        return jsonify({'message': 'Failed to search messages'}), 500


# Export the blueprint for use in the main application
messages_bp = messages_bp