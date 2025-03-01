"""
Central notification management service that orchestrates notifications across multiple channels (email, in-app) for the Justice Bid Rate Negotiation System.
Handles notification preferences, delivery, and coordination for various system events like rate requests, submissions, approvals, and messages.
"""

import typing
import enum
from datetime import datetime
import uuid
from celery import current_app as celery_app  # Import Celery's current_app

from src.backend.utils.logging import get_logger  # Import logging functionality
from src.backend.services.messaging.in_app import InAppMessageService, NotificationType, NotificationPriority  # For creating and managing in-app notifications
from src.backend.services.messaging.email import send_email, send_email_async, send_rate_request_notification, send_rate_submission_notification, send_counter_proposal_notification, send_approval_notification, send_message_notification, send_ocg_negotiation_notification  # Functions for sending email notifications
from src.backend.db.repositories.user_repository import UserRepository  # Accessing user data and notification preferences
from src.backend.db.repositories.message_repository import MessageRepository  # Accessing message data for notifications
from src.backend.db.repositories.negotiation_repository import NegotiationRepository  # Accessing negotiation data for context in notifications
from src.backend.utils.event_tracking import track_event  # Track notification-related events
from src.backend.utils.constants import RateStatus, NegotiationStatus, ApprovalStatus, OCGStatus  # Status enums for different entity types

logger = get_logger(__name__)
NOTIFICATION_TASK_PATH = 'src.backend.tasks.notification_tasks'


def get_user_notification_preferences(user_id: uuid.UUID, event_type: str) -> dict:
    """
    Get user notification preferences for a specific event type
    
    Args:
        user_id (uuid.UUID): User ID
        event_type (str): Event type
    
    Returns:
        dict: User's notification preferences for the event type
    """
    # Validate user_id is valid UUID
    try:
        uuid.UUID(str(user_id))
    except ValueError:
        raise ValueError("Invalid user_id format")
    # Retrieve user notification preferences from UserRepository
    user_repository = UserRepository()
    preferences = user_repository.get_user_notification_preferences(user_id)
    # If no preferences found, return default preferences
    if not preferences:
        return {'email': True, 'in_app': True}
    # Return specific event type preferences or default preferences
    return preferences.get(event_type, {'email': True, 'in_app': True})


def update_user_notification_preferences(user_id: uuid.UUID, preferences: dict) -> bool:
    """
    Update a user's notification preferences
    
    Args:
        user_id (uuid.UUID): User ID
        preferences (dict): Preferences dictionary
    
    Returns:
        bool: Success status of the update operation
    """
    # Validate user_id is valid UUID
    try:
        uuid.UUID(str(user_id))
    except ValueError:
        raise ValueError("Invalid user_id format")
    # Validate preferences dictionary structure
    if not isinstance(preferences, dict):
        raise ValueError("Preferences must be a dictionary")
    # Update user preferences using UserRepository
    user_repository = UserRepository()
    user_repository.update_user_notification_preferences(user_id, preferences)
    # Track preference update event
    track_event(event_type='notification_preferences_updated', data=preferences, user_id=str(user_id))
    # Return success status
    return True


def should_send_notification(preferences: dict, event_type: str, channel: 'NotificationChannel', is_high_priority: bool) -> bool:
    """
    Determine if a notification should be sent based on user preferences
    
    Args:
        preferences (dict): User preferences
        event_type (str): Event type
        channel (NotificationChannel): Notification channel
        is_high_priority (bool): Whether notification is high priority
    
    Returns:
        bool: Whether notification should be sent
    """
    # Check if notifications are completely disabled for user
    if preferences.get('disable_all', False):
        return False
    # Get channel-specific preference for event type
    channel_preference = preferences.get(event_type, {}).get(channel.name.lower(), True)
    # If high priority, override user preferences
    if is_high_priority:
        return True
    # Return decision based on preferences and priority
    return channel_preference


def send_notification(user_id: uuid.UUID, event_type: str, title: str, content: str, context: dict, channels: list, is_high_priority: bool, action_url: str) -> dict:
    """
    Send a notification through specified channels based on user preferences
    
    Args:
        user_id (uuid.UUID): User ID
        event_type (str): Event type
        title (str): Notification title
        content (str): Notification content
        context (dict): Context data for notification
        channels (list): List of notification channels
        is_high_priority (bool): Whether notification is high priority
        action_url (str): URL for notification action
    
    Returns:
        dict: Results of notification delivery by channel
    """
    # Get user notification preferences
    preferences = get_user_notification_preferences(user_id, event_type)
    # Initialize results dictionary
    results = {}
    # If not real-time mode, queue notification task and return
    if not context.get('real_time', True):
        task_id = send_notification_async(user_id, event_type, title, content, context, channels, is_high_priority, action_url)
        return {'task_id': task_id}
    # For each channel in channels list:
    for channel in channels:
        # Check if notification should be sent using should_send_notification
        if should_send_notification(preferences, event_type, channel, is_high_priority):
            # Send to appropriate channel based on channel type
            if channel == NotificationChannel.EMAIL:
                results['email'] = send_email_async(user_id, event_type, title, content, context, channels, is_high_priority, action_url)
            elif channel == NotificationChannel.IN_APP:
                results['in_app'] = InAppMessageService.create_notification(user_id, event_type, title, content, NotificationPriority.HIGH if is_high_priority else NotificationPriority.MEDIUM, context, action_url)
    # Track notification sending event
    track_event(event_type='notification_sent', data=results, user_id=str(user_id))
    # Return results dictionary
    return results


def send_notification_async(user_id: uuid.UUID, event_type: str, title: str, content: str, context: dict, channels: list, is_high_priority: bool, action_url: str) -> str:
    """
    Queue a notification to be sent asynchronously via Celery
    
    Args:
        user_id (uuid.UUID): User ID
        event_type (str): Event type
        title (str): Notification title
        content (str): Notification content
        context (dict): Context data for notification
        channels (list): List of notification channels
        is_high_priority (bool): Whether notification is high priority
        action_url (str): URL for notification action
    
    Returns:
        str: Task ID of the queued notification
    """
    # Import Celery's current_app
    # Create a task signature using the task path string NOTIFICATION_TASK_PATH
    task = celery_app.signature(f'{NOTIFICATION_TASK_PATH}.send_notification')
    # Set task arguments with all the notification parameters
    task_args = (user_id, event_type, title, content, context, channels, is_high_priority, action_url)
    # Call task.delay() to execute task asynchronously
    result = task.delay(*task_args)
    # Return task ID as string
    return str(result.id)


def send_batch_notification(user_ids: list, event_type: str, title: str, content: str, context: dict, channels: list, is_high_priority: bool, action_url: str) -> dict:
    """
    Send the same notification to multiple users
    
    Args:
        user_ids (list): List of User IDs
        event_type (str): Event type
        title (str): Notification title
        content (str): Notification content
        context (dict): Context data for notification
        channels (list): List of notification channels
        is_high_priority (bool): Whether notification is high priority
        action_url (str): URL for notification action
    
    Returns:
        dict: Results of batch notification with success and failure counts
    """
    # Initialize success and failure counters
    success_count = 0
    failure_count = 0
    # If not real-time mode, queue batch notification task and return
    if not context.get('real_time', True):
        task_id = send_batch_notification_async(user_ids, event_type, title, content, context, channels, is_high_priority, action_url)
        return {'task_id': task_id}
    # For each user_id in the batch:
    for user_id in user_ids:
        # Attempt to send individual notification
        try:
            send_notification(user_id, event_type, title, content, context, channels, is_high_priority, action_url)
            success_count += 1
        # Update success or failure counter based on result
        except Exception:
            failure_count += 1
    # Track batch notification event
    track_event(event_type='batch_notification_sent', data={'success_count': success_count, 'failure_count': failure_count}, user_id=str(user_id))
    # Return dictionary with success and failure counts
    return {'success_count': success_count, 'failure_count': failure_count}


def send_batch_notification_async(user_ids: list, event_type: str, title: str, content: str, context: dict, channels: list, is_high_priority: bool, action_url: str) -> str:
    """
    Queue a batch notification to be sent asynchronously via Celery
    
    Args:
        user_ids (list): List of User IDs
        event_type (str): Event type
        title (str): Notification title
        content (str): Notification content
        context (dict): Context data for notification
        channels (list): List of notification channels
        is_high_priority (bool): Whether notification is high priority
        action_url (str): URL for notification action
    
    Returns:
        str: Task ID of the queued batch notification
    """
    # Import Celery's current_app
    # Create a task signature using the batch task path string
    task = celery_app.signature(f'{NOTIFICATION_TASK_PATH}.send_batch_notification')
    # Set task arguments with all the batch notification parameters
    task_args = (user_ids, event_type, title, content, context, channels, is_high_priority, action_url)
    # Call task.delay() to execute task asynchronously
    result = task.delay(*task_args)
    # Return task ID as string
    return str(result.id)


class NotificationChannel(enum.Enum):
    """Enum defining the available notification channels"""
    @enum.unique
    class NotificationChannel(enum.Enum):
        EMAIL = "email"
        IN_APP = "in_app"
        BOTH = "both"
        NONE = "none"


class NotificationTemplateType(enum.Enum):
    """Enum defining the types of notification templates"""
    @enum.unique
    class NotificationTemplateType(enum.Enum):
        RATE_REQUEST = "rate_request"
        RATE_SUBMISSION = "rate_submission"
        RATE_COUNTER_PROPOSAL = "rate_counter_proposal"
        RATE_APPROVAL = "rate_approval"
        RATE_REJECTION = "rate_rejection"
        APPROVAL_REQUEST = "approval_request"
        APPROVAL_RESULT = "approval_result"
        OCG_UPDATE = "ocg_update"
        MESSAGE = "message"


class NotificationManager:
    """Central service for managing notifications across multiple channels"""

    def __init__(self, email_service, in_app_service: InAppMessageService, user_repository: UserRepository, message_repository: MessageRepository, negotiation_repository: NegotiationRepository):
        """Initialize the notification manager with required services"""
        self._email_service = email_service
        self._in_app_service = in_app_service
        self._user_repository = user_repository
        self._message_repository = message_repository
        self._negotiation_repository = negotiation_repository

    def get_user_notification_preferences(self, user_id: uuid.UUID, event_type: str) -> dict:
        """Get a user's notification preferences"""
        # Call the user repository to get preferences
        preferences = self._user_repository.get_user_notification_preferences(user_id, event_type)
        # Apply default preferences for any missing settings
        default_preferences = {'email': True, 'in_app': True}
        combined_preferences = default_preferences.copy()
        combined_preferences.update(preferences)
        # Return the combined preferences
        return combined_preferences

    def notify_rate_request(self, request_id: uuid.UUID, action: str, recipient_ids: list, message: str) -> dict:
        """Notify users about a rate request"""
        # Get rate request data
        # Determine notification type, title, and priority based on action
        if action == "request":
            notification_type = NotificationType.RATE_REQUEST
            title = "New Rate Request"
            priority = NotificationPriority.MEDIUM
        else:
            raise ValueError(f"Invalid action type: {action}")
        # Prepare notification content using message and context
        # Send in-app notifications using _in_app_service
        # Send email notifications using _email_service
        # Return results dictionary
        return {}

    def notify_rate_submission(self, negotiation_id: uuid.UUID, recipient_ids: list, message: str, summary: dict) -> dict:
        """Notify users about a rate submission"""
        # Get negotiation data
        # Prepare notification content with submission details
        # Send in-app notifications using _in_app_service
        # Send email notifications using _email_service
        # Return results dictionary
        return {}

    def notify_rate_negotiation(self, negotiation_id: uuid.UUID, recipient_ids: list, status: RateStatus, message: str, summary: dict) -> dict:
        """Notify users about rate negotiation updates (counter-proposals, approvals, rejections)"""
        # Get negotiation data
        # Determine notification type, title, and priority based on status
        # Prepare notification content with negotiation details
        # Send in-app notifications using _in_app_service
        # Send email notifications using _email_service
        # Return results dictionary
        return {}

    def notify_approval_request(self, negotiation_id: uuid.UUID, approver_ids: list, context_data: dict) -> dict:
        """Notify approvers about a pending approval request"""
        # Get negotiation data
        # Prepare notification content with approval context
        # Send in-app notifications using _in_app_service
        # Send email notifications using _email_service
        # Set high priority flag for approval requests
        # Return results dictionary
        return {}

    def notify_approval_result(self, negotiation_id: uuid.UUID, recipient_ids: list, status: ApprovalStatus, comment: str) -> dict:
        """Notify users about an approval decision"""
        # Get negotiation data
        # Determine notification type, title, and priority based on status
        # Prepare notification content with approval decision
        # Send in-app notifications using _in_app_service
        # Send email notifications using _email_service
        # Return results dictionary
        return {}

    def notify_ocg_update(self, ocg_id: uuid.UUID, recipient_ids: list, status: OCGStatus, message: str) -> dict:
        """Notify users about OCG updates"""
        # Get OCG data
        # Determine notification title and content based on status
        # Send in-app notifications using _in_app_service
        # Send email notifications using _email_service
        # Return results dictionary
        return {}

    def notify_message(self, message_id: uuid.UUID) -> dict:
        """Notify users about a new message"""
        # Get message data from repository
        # Extract recipients from message
        # Generate message preview
        # Send in-app notifications using _in_app_service
        # Send email notifications using _email_service
        # Return results dictionary
        return {}

    def send_system_notification(self, user_ids: list, title: str, content: str, priority: NotificationPriority = NotificationPriority.MEDIUM) -> dict:
        """Send a system-level notification to users"""
        # Send in-app notifications using _in_app_service
        # For high priority, send email notifications
        # Return results dictionary
        return {}

    def send_welcome_notification(self, user_id: uuid.UUID, organization_name: str) -> dict:
        """Send welcome notification to a new user"""
        # Prepare welcome notification content
        # Send in-app welcome notification
        # Send welcome email
        # Return results dictionary
        return {}

    def _get_notification_template(self, template_type: NotificationTemplateType, context: dict) -> typing.Tuple[str, str, NotificationPriority]:
        """Get appropriate notification template based on type"""
        # Match template_type to predefined templates
        # Apply context variables to templates
        # Determine appropriate priority level
        # Return tuple of (title, content, priority)
        return "", "", NotificationPriority.MEDIUM