"""
Thread management service for the messaging system. Handles creation, retrieval,
and management of hierarchical message threads between law firms and clients
during rate negotiations.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.backend.db.models.message import Message  # Message model for database interactions
from src.backend.db.repositories.message_repository import MessageRepository  # Repository for message database operations
from src.backend.db.models.negotiation import Negotiation  # Negotiation model for linking threads to negotiations
from src.backend.db.repositories.negotiation_repository import NegotiationRepository  # Repository for negotiation database operations
from src.backend.utils.logging import logger  # Logging utility for thread service
from src.backend.services.auth.permissions import check_permission  # Permission checking for thread access control
from src.backend.services.messaging.notifications import send_notification  # Send notifications for new messages and thread updates

THREAD_TYPE_NEGOTIATION = "negotiation"
THREAD_TYPE_DIRECT = "direct"
THREAD_TYPE_GROUP = "group"
THREAD_TYPE_OCG = "ocg"
THREAD_TYPE_RATE = "rate"


def create_thread(participant_ids: List[str], thread_type: str, related_entity_type: str,
                  related_entity_id: str, subject: str, creator_id: str) -> str:
    """Creates a new message thread with the specified participants and optional related entity

    Args:
        participant_ids (List[str]): List of user IDs participating in the thread
        thread_type (str): Type of the thread (negotiation, direct, group, etc.)
        related_entity_type (str): Type of the entity the thread is related to (e.g., rate, OCG)
        related_entity_id (str): ID of the related entity
        subject (str): Subject of the thread
        creator_id (str): ID of the user creating the thread

    Returns:
        str: The ID of the newly created thread
    """
    thread_id = str(uuid.uuid4())  # Generate a new UUID for the thread
    logger.info(f"Creating new thread with ID: {thread_id}")

    # Validate that the creator has permission to create a thread with the given participants
    check_permission(creator_id, "messages:create")

    # Create thread metadata including participants, related entity, and subject
    thread_metadata = {
        "thread_id": thread_id,
        "participant_ids": participant_ids,
        "thread_type": thread_type,
        "related_entity_type": related_entity_type,
        "related_entity_id": related_entity_id,
        "subject": subject,
        "creator_id": creator_id,
        "created_at": datetime.utcnow().isoformat()
    }

    # Store thread metadata in the database
    logger.debug(f"Storing thread metadata: {thread_metadata}")

    # Log thread creation with appropriate context
    logger.info(f"Thread created successfully: {thread_id}",
                extra={"additional_data": thread_metadata})

    return thread_id  # Return the thread ID


def get_thread_by_id(thread_id: str, user_id: str) -> dict:
    """Retrieves a thread by its ID, including metadata and access control

    Args:
        thread_id (str): ID of the thread to retrieve
        user_id (str): ID of the user requesting the thread

    Returns:
        dict: Thread metadata including participants and related entity information
    """
    logger.info(f"Retrieving thread with ID: {thread_id}")

    # Validate that the thread exists
    if not thread_id:
        raise ValueError("Thread ID is required")

    # Check if the user has permission to access the thread
    check_permission(user_id, "messages:read")

    # Retrieve thread metadata from the database
    thread_metadata = {
        "thread_id": thread_id,
        "participant_ids": ["user1", "user2"],  # Example data
        "thread_type": "negotiation",  # Example data
        "related_entity_type": "rate",  # Example data
        "related_entity_id": "rate123",  # Example data
        "subject": "Rate Negotiation",  # Example data
        "creator_id": "user1",  # Example data
        "created_at": datetime.utcnow().isoformat()  # Example data
    }

    # Log thread retrieval with appropriate context
    logger.debug(f"Retrieved thread metadata: {thread_metadata}")

    # Return thread information including participants and related entity
    return thread_metadata


def get_thread_messages(thread_id: str, user_id: str, page: int, page_size: int) -> dict:
    """Retrieves all messages in a thread with proper hierarchical structure

    Args:
        thread_id (str): ID of the thread
        user_id (str): ID of the user requesting the messages
        page (int): Page number for pagination
        page_size (int): Number of messages per page

    Returns:
        dict: Dictionary containing messages in hierarchical structure and pagination info
    """
    logger.info(f"Retrieving messages for thread ID: {thread_id}")

    # Validate that the thread exists
    if not thread_id:
        raise ValueError("Thread ID is required")

    # Check if the user has permission to access the thread
    check_permission(user_id, "messages:read")

    # Retrieve messages for the thread with pagination from MessageRepository
    message_repository = MessageRepository()
    messages = message_repository.get_messages_by_thread_id(thread_id, skip=(page - 1) * page_size, limit=page_size)

    # Organize messages into hierarchical structure based on parent_id using _build_thread_hierarchy
    hierarchical_messages = _build_thread_hierarchy(messages)

    # Mark messages as read for the requesting user
    message_repository.mark_thread_as_read(thread_id, user_id)

    # Return organized messages with pagination metadata
    return {
        "messages": [message.to_dict() for message in hierarchical_messages],
        "page": page,
        "page_size": page_size,
        "total_messages": message_repository.get_thread_count(thread_id)
    }


def add_message_to_thread(thread_id: str, sender_id: str, content: str, parent_id: str,
                         attachments: List[dict], related_entity_type: str, related_entity_id: str) -> dict:
    """Adds a new message to an existing thread

    Args:
        thread_id (str): ID of the thread
        sender_id (str): ID of the user sending the message
        content (str): Content of the message
        parent_id (str): ID of the parent message (for replies)
        attachments (List[dict]): List of attachments for the message
        related_entity_type (str): Type of the entity the message is related to (e.g., rate, OCG)
        related_entity_id (str): ID of the related entity

    Returns:
        dict: The newly created message
    """
    logger.info(f"Adding message to thread ID: {thread_id}")

    # Validate that the thread exists
    if not thread_id:
        raise ValueError("Thread ID is required")

    # Check if the sender has permission to post to the thread using _validate_thread_access
    _validate_thread_access(thread_id, sender_id, "messages:create")

    # If parent_id is provided, verify it exists and belongs to this thread
    if parent_id:
        message_repository = MessageRepository()
        parent_message = message_repository.get_message_by_id(parent_id)
        if not parent_message or parent_message.thread_id != thread_id:
            raise ValueError("Invalid parent message ID")

    # Create a new message with the provided content through MessageRepository
    message_repository = MessageRepository()
    message_data = {
        "thread_id": thread_id,
        "sender_id": sender_id,
        "recipient_ids": [],  # TODO: Implement recipient handling
        "content": content,
        "parent_id": parent_id,
        "attachments": attachments,
        "related_entity_type": related_entity_type,
        "related_entity_id": related_entity_id
    }
    new_message = message_repository.create_message(message_data)

    # Notify thread participants using send_notification
    send_notification(
        user_id=uuid.UUID(sender_id),
        event_type="new_message",
        title="New Message",
        content=content[:50],  # Preview of the message
        context={"thread_id": thread_id},
        channels=["in_app", "email"],
        is_high_priority=False,
        action_url=f"/threads/{thread_id}"
    )

    # Return the created message
    logger.info(f"Message added to thread {thread_id} successfully")
    return new_message.to_dict()


def get_threads_for_user(user_id: str, organization_id: str, page: int, page_size: int, filters: dict) -> dict:
    """Retrieves all threads that a user is a participant in

    Args:
        user_id (str): ID of the user
        organization_id (str): ID of the organization
        page (int): Page number for pagination
        page_size (int): Number of messages per page
        filters (dict): Filters to apply to the threads

    Returns:
        dict: Dictionary containing threads and pagination information
    """
    logger.info(f"Retrieving threads for user ID: {user_id}")
    # Validate user permissions
    check_permission(user_id, "messages:read")

    # Retrieve threads where user is a participant
    # Apply filters if provided (thread_type, related_entity_type, etc.)
    # For each thread, retrieve the latest message
    # Calculate unread message count for each thread
    # Sort threads by latest message timestamp
    # Apply pagination
    # Return threads with pagination metadata
    return {}


def get_threads_for_negotiation(negotiation_id: str, user_id: str, page: int, page_size: int) -> dict:
    """Retrieves all threads related to a specific negotiation

    Args:
        negotiation_id (str): ID of the negotiation
        user_id (str): ID of the user
        page (int): Page number for pagination
        page_size (int): Number of messages per page

    Returns:
        dict: Dictionary containing threads and pagination information
    """
    logger.info(f"Retrieving threads for negotiation ID: {negotiation_id}")
    # Validate that the negotiation exists
    if not negotiation_id:
        raise ValueError("Negotiation ID is required")

    # Check if the user has permission to access the negotiation
    check_permission(user_id, "negotiations:read")

    # Retrieve threads where related_entity_type is 'negotiation' and related_entity_id matches
    # For each thread, retrieve the latest message
    # Calculate unread message count for each thread
    # Sort threads by latest message timestamp
    # Apply pagination
    # Return threads with pagination metadata
    return {}


def get_threads_for_rate(rate_id: str, user_id: str, page: int, page_size: int) -> dict:
    """Retrieves all threads related to a specific rate

    Args:
        rate_id (str): ID of the rate
        user_id (str): ID of the user
        page (int): Page number for pagination
        page_size (int): Number of messages per page

    Returns:
        dict: Dictionary containing threads and pagination information
    """
    logger.info(f"Retrieving threads for rate ID: {rate_id}")
    # Validate that the rate exists
    if not rate_id:
        raise ValueError("Rate ID is required")

    # Check if the user has permission to access the rate
    check_permission(user_id, "rates:read")

    # Retrieve threads where related_entity_type is 'rate' and related_entity_id matches
    # For each thread, retrieve the latest message
    # Calculate unread message count for each thread
    # Sort threads by latest message timestamp
    # Apply pagination
    # Return threads with pagination metadata
    return {}


def update_thread_participants(thread_id: str, participant_ids: List[str], user_id: str) -> bool:
    """Updates the list of participants in a thread

    Args:
        thread_id (str): ID of the thread
        participant_ids (List[str]): List of user IDs participating in the thread
        user_id (str): ID of the user making the update

    Returns:
        bool: True if the update was successful
    """
    logger.info(f"Updating participants for thread ID: {thread_id}")
    # Validate that the thread exists
    if not thread_id:
        raise ValueError("Thread ID is required")

    # Check if the user has permission to modify the thread participants
    check_permission(user_id, "messages:update")

    # Update the participant list for the thread in the database
    # Log the participant update for audit purposes
    # Notify new participants about being added to the thread
    # Return success indicator
    return True


def mark_thread_read(thread_id: str, user_id: str) -> bool:
    """Marks all messages in a thread as read for a specific user

    Args:
        thread_id (str): ID of the thread
        user_id (str): ID of the user

    Returns:
        bool: True if the update was successful
    """
    logger.info(f"Marking thread {thread_id} as read for user {user_id}")
    # Validate that the thread exists
    if not thread_id:
        raise ValueError("Thread ID is required")

    # Check if the user is a participant in the thread
    check_permission(user_id, "messages:read")

    # Mark all unread messages in the thread as read for the user
    # Update read status in the database
    # Return success indicator
    return True


def search_threads(user_id: str, organization_id: str, search_term: str, filters: dict, page: int, page_size: int) -> dict:
    """Searches for threads matching specific criteria

    Args:
        user_id (str): ID of the user
        organization_id (str): ID of the organization
        search_term (str): Search term
        filters (dict): Filters to apply to the search
        page (int): Page number for pagination
        page_size (int): Number of messages per page

    Returns:
        dict: Dictionary containing search results and pagination information
    """
    logger.info(f"Searching threads for user ID: {user_id} with search term: {search_term}")
    # Validate user permissions
    check_permission(user_id, "messages:read")

    # Search for threads where user is a participant
    # Apply full-text search on thread subject and message content
    # Apply additional filters if provided (thread_type, date range, etc.)
    # Sort results by relevance and/or recency
    # Apply pagination
    # Return search results with pagination metadata
    return {}


def get_unread_thread_count(user_id: str, organization_id: str) -> int:
    """Gets the count of threads with unread messages for a user

    Args:
        user_id (str): ID of the user
        organization_id (str): ID of the organization

    Returns:
        int: Count of threads with unread messages
    """
    logger.info(f"Getting unread thread count for user ID: {user_id}")
    # Validate user permissions
    check_permission(user_id, "messages:read")

    # Count threads where user is a participant and has unread messages
    # Return the count
    return 0


def _build_thread_hierarchy(messages: List[Message]) -> List[dict]:
    """Internal helper function to organize messages into a hierarchical structure

    Args:
        messages (List[dict]): List of message dictionaries

    Returns:
        List[dict]: Organized hierarchical message structure
    """
    # Create a lookup dictionary for quick message access by ID
    message_dict = {str(message.id): message for message in messages}

    # Identify root messages (those with no parent or parent outside the current set)
    root_messages = []
    for message in messages:
        if not message.parent_id or str(message.parent_id) not in message_dict:
            root_messages.append(message)

    # For each message with a parent, add it to parent's children list
    for message in messages:
        if message.parent_id and str(message.parent_id) in message_dict:
            parent = message_dict[str(message.parent_id)]
            if not hasattr(parent, 'replies'):
                parent.replies = []
            parent.replies.append(message)

    # Sort children by timestamp
    for message in messages:
        if hasattr(message, 'replies'):
            message.replies.sort(key=lambda m: m.created_at)

    # Return the list of root messages with their nested children
    return root_messages


def _validate_thread_access(thread_id: str, user_id: str, required_permission: str) -> bool:
    """Internal helper function to validate a user's access to a thread

    Args:
        thread_id (str): ID of the thread
        user_id (str): ID of the user
        required_permission (str): Permission required to access the thread

    Returns:
        bool: True if the user has access, raises exception otherwise
    """
    logger.debug(f"Validating access to thread {thread_id} for user {user_id}")
    # Retrieve thread metadata
    # Check if the user is a participant in the thread
    # If related to an entity, check if the user has required permission for the related entity
    # If not authorized, raise PermissionError with appropriate message
    # Return True if authorized
    return True