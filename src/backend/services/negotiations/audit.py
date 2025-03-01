"""Module for audit logging and tracking of negotiation-related activities in the Justice Bid system.
Provides comprehensive audit trail functionality for rate negotiations, ensuring compliance, transparency, and historical record-keeping."""

import json  # standard library
from datetime import datetime  # standard library
import typing  # standard library
import uuid  # standard library

# Internal imports
from src.backend.db.repositories.negotiation_repository import NegotiationRepository  # src/backend/db/repositories/negotiation_repository.py
from src.backend.db.repositories.rate_repository import RateRepository  # src/backend/db/repositories/rate_repository.py
from src.backend.utils.constants import NegotiationStatus  # src/backend/utils/constants.py
from src.backend.utils.event_tracking import track_negotiation_event, track_rate_event  # src/backend/utils/event_tracking.py
from src.backend.utils.logging import get_logger  # src/backend/utils/logging.py

logger = get_logger(__name__)
NEGOTIATION_STATES = ['REQUESTED', 'IN_PROGRESS', 'COMPLETED', 'REJECTED']


def log_negotiation_state_change(negotiation_id: str, previous_state: str, new_state: str,
                                 user_id: str, metadata: dict, track_analytics: bool) -> bool:
    """Logs a change in negotiation state with detailed metadata

    Args:
        negotiation_id: The ID of the negotiation
        previous_state: The previous state of the negotiation
        new_state: The new state of the negotiation
        user_id: The ID of the user who initiated the change
        metadata: Additional metadata about the state change
        track_analytics: Flag indicating whether to track the event for analytics

    Returns:
        Success status of the logging operation
    """
    # Validate that new_state is a valid negotiation state string
    if not validate_negotiation_state(new_state):
        logger.warning(f"Invalid negotiation state: {new_state}")
        return False

    try:
        # Retrieve the negotiation object using NegotiationRepository
        negotiation_repo = NegotiationRepository()
        negotiation = negotiation_repo.get_negotiation_by_id(negotiation_id)

        if not negotiation:
            logger.warning(f"Negotiation not found: {negotiation_id}")
            return False

        # Create an audit entry with state change information
        audit_entry = create_audit_entry(
            entity_type='negotiation',
            entity_id=negotiation_id,
            action_type='state_change',
            user_id=user_id,
            details={
                'previous_state': previous_state,
                'new_state': new_state
            },
            metadata=metadata
        )

        # Add the audit entry to the negotiation history
        negotiation.history = negotiation.history or []
        negotiation.history.append(audit_entry)

        # Log the state change at INFO level with relevant context
        logger.info(
            f"Negotiation {negotiation_id} state changed from {previous_state} to {new_state} by user {user_id}",
            extra={'additional_data': audit_entry}
        )

        # If track_analytics is True, send event to analytics tracking
        if track_analytics:
            track_negotiation_event(
                event_type='negotiation_state_changed',
                user_id=user_id,
                organization_id=str(negotiation.client_id),
                negotiation_id=negotiation_id,
                data={
                    'previous_state': previous_state,
                    'new_state': new_state
                },
                metadata=metadata
            )
        negotiation_repo.session.commit()
        # Return True if the operation was successful, False otherwise
        return True
    except Exception as e:
        logger.error(f"Error logging negotiation state change: {str(e)}")
        return False


def log_rate_change(rate_id: str, negotiation_id: str, previous_amount: float, new_amount: float,
                    currency: str, user_id: str, change_type: str, message: str, metadata: dict) -> bool:
    """Logs a change to a rate during negotiation process

    Args:
        rate_id: The ID of the rate
        negotiation_id: The ID of the negotiation
        previous_amount: The previous amount of the rate
        new_amount: The new amount of the rate
        currency: The currency of the rate
        user_id: The ID of the user who initiated the change
        change_type: The type of change (e.g., 'proposed', 'approved')
        message: A message describing the rate change
        metadata: Additional metadata about the rate change

    Returns:
        Success status of the logging operation
    """
    try:
        # Retrieve the rate object using RateRepository
        rate_repo = RateRepository()
        rate = rate_repo.get_by_id(rate_id)

        if not rate:
            logger.warning(f"Rate not found: {rate_id}")
            return False

        # Retrieve the negotiation object using NegotiationRepository
        negotiation_repo = NegotiationRepository()
        negotiation = negotiation_repo.get_negotiation_by_id(negotiation_id)

        if not negotiation:
            logger.warning(f"Negotiation not found: {negotiation_id}")
            return False

        # Create an audit entry with rate change information
        audit_entry = create_audit_entry(
            entity_type='rate',
            entity_id=rate_id,
            action_type=change_type,
            user_id=user_id,
            details={
                'previous_amount': previous_amount,
                'new_amount': new_amount,
                'currency': currency,
                'message': message
            },
            metadata=metadata
        )

        # Add the audit entry to both rate and negotiation history
        rate.history = rate.history or []
        rate.history.append(audit_entry)

        negotiation.history = negotiation.history or []
        negotiation.history.append(audit_entry)

        # Log the rate change at INFO level with context
        logger.info(
            f"Rate {rate_id} changed from {previous_amount} to {new_amount} by user {user_id}",
            extra={'additional_data': audit_entry}
        )

        # Track the rate event for analytics purposes
        track_rate_event(
            event_type='rate_changed',
            user_id=user_id,
            organization_id=str(rate.client_id),
            data={
                'rate_id': rate_id,
                'previous_amount': previous_amount,
                'new_amount': new_amount,
                'currency': currency
            },
            metadata=metadata
        )
        rate_repo.session.commit()
        # Return True if the operation was successful, False otherwise
        return True
    except Exception as e:
        logger.error(f"Error logging rate change: {str(e)}")
        return False


def log_counter_proposal(negotiation_id: str, user_id: str, counter_rates: dict, message: str,
                         metadata: dict) -> bool:
    """Logs a counter-proposal action in the negotiation

    Args:
        negotiation_id: The ID of the negotiation
        user_id: The ID of the user who initiated the counter-proposal
        counter_rates: A dictionary of rate IDs and their counter-proposed amounts
        message: A message describing the counter-proposal
        metadata: Additional metadata about the counter-proposal

    Returns:
        Success status of the logging operation
    """
    try:
        # Retrieve the negotiation object using NegotiationRepository
        negotiation_repo = NegotiationRepository()
        negotiation = negotiation_repo.get_negotiation_by_id(negotiation_id)

        if not negotiation:
            logger.warning(f"Negotiation not found: {negotiation_id}")
            return False

        # Create an audit entry with counter-proposal information
        audit_entry = create_audit_entry(
            entity_type='negotiation',
            entity_id=negotiation_id,
            action_type='counter_proposal',
            user_id=user_id,
            details={
                'counter_rates': counter_rates,
                'message': message
            },
            metadata=metadata
        )

        # Include summary of rate changes in the audit entry
        rate_changes = []
        for rate_id, new_amount in counter_rates.items():
            rate_changes.append(f"Rate {rate_id}: {new_amount}")
        audit_entry['details']['rate_changes'] = rate_changes

        # Add the audit entry to the negotiation history
        negotiation.history = negotiation.history or []
        negotiation.history.append(audit_entry)

        # Log the counter-proposal action at INFO level
        logger.info(
            f"Counter-proposal made in negotiation {negotiation_id} by user {user_id}",
            extra={'additional_data': audit_entry}
        )

        # Track the negotiation event for analytics purposes
        track_negotiation_event(
            event_type='negotiation_counter_proposed',
            user_id=user_id,
            organization_id=str(negotiation.client_id),
            negotiation_id=negotiation_id,
            data={
                'counter_rates': counter_rates,
                'message': message
            },
            metadata=metadata
        )
        negotiation_repo.session.commit()
        # Return True if the operation was successful, False otherwise
        return True
    except Exception as e:
        logger.error(f"Error logging counter-proposal: {str(e)}")
        return False


def log_approval_action(negotiation_id: str, approver_id: str, action: str, comment: str,
                        metadata: dict) -> bool:
    """Logs an approval workflow action in the negotiation process

    Args:
        negotiation_id: The ID of the negotiation
        approver_id: The ID of the user who performed the approval action
        action: The approval action (e.g., 'approved', 'rejected')
        comment: A comment associated with the approval action
        metadata: Additional metadata about the approval action

    Returns:
        Success status of the logging operation
    """
    try:
        # Retrieve the negotiation object using NegotiationRepository
        negotiation_repo = NegotiationRepository()
        negotiation = negotiation_repo.get_negotiation_by_id(negotiation_id)

        if not negotiation:
            logger.warning(f"Negotiation not found: {negotiation_id}")
            return False

        # Create an audit entry with approval action information
        audit_entry = create_audit_entry(
            entity_type='negotiation',
            entity_id=negotiation_id,
            action_type=action,
            user_id=approver_id,
            details={
                'action': action,
                'comment': comment
            },
            metadata=metadata
        )

        # Add the audit entry to the negotiation history
        negotiation.history = negotiation.history or []
        negotiation.history.append(audit_entry)

        # Log the approval action at INFO level with context
        logger.info(
            f"Approval action '{action}' in negotiation {negotiation_id} by approver {approver_id}",
            extra={'additional_data': audit_entry}
        )

        # Track the negotiation event for analytics purposes
        track_negotiation_event(
            event_type='negotiation_approval_action',
            user_id=approver_id,
            organization_id=str(negotiation.client_id),
            negotiation_id=negotiation_id,
            data={
                'action': action,
                'comment': comment
            },
            metadata=metadata
        )
        negotiation_repo.session.commit()
        # Return True if the operation was successful, False otherwise
        return True
    except Exception as e:
        logger.error(f"Error logging approval action: {str(e)}")
        return False


def log_message_activity(negotiation_id: str, message_id: str, sender_id: str, recipient_ids: list,
                         activity_type: str, metadata: dict) -> bool:
    """Logs a messaging event related to a negotiation

    Args:
        negotiation_id: The ID of the negotiation
        message_id: The ID of the message
        sender_id: The ID of the user who sent the message
        recipient_ids: A list of IDs of the message recipients
        activity_type: The type of message activity (e.g., 'sent', 'read')
        metadata: Additional metadata about the message activity

    Returns:
        Success status of the logging operation
    """
    try:
        # Retrieve the negotiation object using NegotiationRepository
        negotiation_repo = NegotiationRepository()
        negotiation = negotiation_repo.get_negotiation_by_id(negotiation_id)

        if not negotiation:
            logger.warning(f"Negotiation not found: {negotiation_id}")
            return False

        # Create an audit entry with message activity information
        audit_entry = create_audit_entry(
            entity_type='negotiation',
            entity_id=negotiation_id,
            action_type=activity_type,
            user_id=sender_id,
            details={
                'message_id': message_id,
                'recipient_ids': recipient_ids
            },
            metadata=metadata
        )

        # Add the audit entry to the negotiation history
        negotiation.history = negotiation.history or []
        negotiation.history.append(audit_entry)

        # Log the message activity at INFO level
        logger.info(
            f"Message activity '{activity_type}' in negotiation {negotiation_id} by sender {sender_id}",
            extra={'additional_data': audit_entry}
        )

        # Track the negotiation event for analytics purposes
        track_negotiation_event(
            event_type='negotiation_message_activity',
            user_id=sender_id,
            organization_id=str(negotiation.client_id),
            negotiation_id=negotiation_id,
            data={
                'message_id': message_id,
                'recipient_ids': recipient_ids,
                'activity_type': activity_type
            },
            metadata=metadata
        )
        negotiation_repo.session.commit()
        # Return True if the operation was successful, False otherwise
        return True
    except Exception as e:
        logger.error(f"Error logging message activity: {str(e)}")
        return False


def get_negotiation_audit_trail(negotiation_id: str, filters: dict, limit: int, offset: int) -> list:
    """Retrieves the complete audit trail for a negotiation

    Args:
        negotiation_id: The ID of the negotiation
        filters: Filtering criteria for the audit trail
        limit: Maximum number of audit entries to return
        offset: Offset for pagination

    Returns:
        List of formatted audit entries for the negotiation
    """
    try:
        # Retrieve the negotiation object using NegotiationRepository
        negotiation_repo = NegotiationRepository()
        negotiation = negotiation_repo.get_negotiation_by_id(negotiation_id)

        if not negotiation:
            logger.warning(f"Negotiation not found: {negotiation_id}")
            return []

        # Extract the audit history from the negotiation
        audit_trail = negotiation.history or []

        # Apply any filtering criteria specified in filters
        filtered_audit_trail = filter_audit_trail(audit_trail, filters)

        # Apply pagination if limit and offset are provided
        if limit and offset:
            paginated_audit_trail = filtered_audit_trail[offset:offset + limit]
        else:
            paginated_audit_trail = filtered_audit_trail

        # Format each audit entry for consistent display
        formatted_audit_trail = [format_audit_entry(entry) for entry in paginated_audit_trail]

        # Return the formatted audit trail as a list
        return formatted_audit_trail
    except Exception as e:
        logger.error(f"Error retrieving negotiation audit trail: {str(e)}")
        return []


def get_rate_audit_trail(rate_id: str, filters: dict, limit: int, offset: int) -> list:
    """Retrieves the audit trail for a specific rate

    Args:
        rate_id: The ID of the rate
        filters: Filtering criteria for the audit trail
        limit: Maximum number of audit entries to return
        offset: Offset for pagination

    Returns:
        List of formatted audit entries for the rate
    """
    try:
        # Retrieve the rate object using RateRepository
        rate_repo = RateRepository()
        rate = rate_repo.get_by_id(rate_id)

        if not rate:
            logger.warning(f"Rate not found: {rate_id}")
            return []

        # Extract the audit history from the rate
        audit_trail = rate.history or []

        # Apply any filtering criteria specified in filters
        filtered_audit_trail = filter_audit_trail(audit_trail, filters)

        # Apply pagination if limit and offset are provided
        if limit and offset:
            paginated_audit_trail = filtered_audit_trail[offset:offset + limit]
        else:
            paginated_audit_trail = filtered_audit_trail

        # Format each audit entry for consistent display
        formatted_audit_trail = [format_audit_entry(entry) for entry in paginated_audit_trail]

        # Return the formatted audit trail as a list
        return formatted_audit_trail
    except Exception as e:
        logger.error(f"Error retrieving rate audit trail: {str(e)}")
        return []


def create_audit_entry(entity_type: str, entity_id: str, action_type: str, user_id: str,
                       details: dict, metadata: dict) -> dict:
    """Creates a standardized audit entry structure

    Args:
        entity_type: The type of entity being audited (e.g., 'negotiation', 'rate')
        entity_id: The ID of the entity being audited
        action_type: The type of action performed (e.g., 'state_change', 'counter_proposal')
        user_id: The ID of the user who performed the action
        details: Detailed information about the action
        metadata: Additional metadata about the action

    Returns:
        Standardized audit entry dictionary
    """
    # Generate a unique audit ID using UUID
    audit_id = uuid.uuid4()

    # Get the current timestamp in ISO format
    timestamp = datetime.utcnow().isoformat()

    # Construct a standardized audit entry dictionary with all provided parameters
    audit_entry = {
        'audit_id': str(audit_id),
        'timestamp': timestamp,
        'entity_type': entity_type,
        'entity_id': entity_id,
        'action_type': action_type,
        'user_id': user_id,
        'details': details,
        'metadata': metadata
    }

    # Return the completed audit entry dictionary
    return audit_entry


def format_audit_entry(audit_entry: dict) -> dict:
    """Formats a raw audit entry for display or API response

    Args:
        audit_entry: The raw audit entry

    Returns:
        Formatted audit entry
    """
    # Format the timestamp in a standardized, readable format
    timestamp = audit_entry.get('timestamp')
    if timestamp:
        try:
            audit_entry['timestamp'] = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        except ValueError:
            logger.warning(f"Invalid timestamp format: {timestamp}")

    # Resolve user ID to display name if possible (omitted for brevity)

    # Format any monetary values with proper currency symbols (omitted for brevity)

    # Restructure the entry for better readability (omitted for brevity)

    # Return the formatted audit entry
    return audit_entry


def filter_audit_trail(audit_trail: list, filters: dict) -> list:
    """Filters an audit trail based on provided criteria

    Args:
        audit_trail: The list of audit entries
        filters: A dictionary of filter criteria

    Returns:
        Filtered list of audit entries
    """
    # Initialize empty result list
    result = []

    # For each audit entry in the audit trail
    for entry in audit_trail:
        # Check if the entry matches all filter criteria
        match = True
        for key, value in filters.items():
            if key not in entry or entry[key] != value:
                match = False
                break

        # If it matches, add it to the result list
        if match:
            result.append(entry)

    # Return the filtered result list
    return result


def validate_negotiation_state(state: str) -> bool:
    """Validates that a given state string is a valid negotiation state

    Args:
        state: The state string to validate

    Returns:
        True if valid, False if invalid
    """
    # Check if the state string is in the list of valid negotiation states
    return state in NEGOTIATION_STATES