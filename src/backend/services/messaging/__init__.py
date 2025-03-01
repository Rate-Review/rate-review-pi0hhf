"""
Initializes the messaging service package and provides a unified API for all messaging functionality
including email notifications, in-app messages, message threads, and notification management
"""

from .email import EmailService  # Import EmailService class for email notifications
from .in_app import InAppMessageService  # Import InAppMessageService class for in-app messages
from .thread import ThreadService  # Import ThreadService class for message thread management
from .notifications import NotificationService  # Import NotificationService class for notification coordination
from typing import List, Dict, Any, Optional
import uuid

class MessagingService:
    """Unified service that coordinates all messaging and notification functionality"""

    def __init__(self):
        """Initializes the messaging service with all required subservices"""
        self.email_service = EmailService()  # Initialize email_service with EmailService()
        self.in_app_service = InAppMessageService()  # Initialize in_app_service with InAppMessageService()
        self.thread_service = ThreadService()  # Initialize thread_service with ThreadService()
        self.notification_service = NotificationService()  # Initialize notification_service with NotificationService()

    def send_message(self, sender_id: str, recipient_ids: List[str], content: str, thread_id: str = None, parent_id: str = None,
                     related_entity_type: str = None, related_entity_id: str = None, attachments: List = None) -> dict:
        """Sends a message to one or more recipients with optional related entity

        Args:
            sender_id (str): ID of the message sender
            recipient_ids (List[str]): List of recipient IDs
            content (str): Content of the message
            thread_id (str): ID of the message thread
            parent_id (str): ID of the parent message (for replies)
            related_entity_type (str): Type of the entity the message is related to (e.g., rate, OCG)
            related_entity_id (str): ID of the related entity
            attachments (List): List of attachments for the message

        Returns:
            dict: Created message data with ID and timestamp
        """
        # Validate sender_id and recipient_ids
        if not sender_id or not recipient_ids:
            raise ValueError("Sender and recipient IDs are required")

        # Create the message using thread_service
        message_data = self.thread_service.create_message(
            sender_id=sender_id,
            recipient_ids=recipient_ids,
            content=content,
            thread_id=thread_id,
            parent_id=parent_id,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            attachments=attachments
        )

        # Send in-app notifications for all recipients using in_app_service
        self.in_app_service.notify_from_message(message_data['id'])

        # Return the created message data
        return message_data

    def get_thread_messages(self, thread_id: str, user_id: str, pagination: dict) -> dict:
        """Retrieves all messages in a thread with hierarchical structure

        Args:
            thread_id (str): ID of the thread
            user_id (str): ID of the user requesting the messages
            pagination (dict): Pagination parameters

        Returns:
            dict: Messages in thread with hierarchical structure and pagination info
        """
        # Validate user access to thread
        self.thread_service.validate_thread_access(thread_id, user_id)

        # Retrieve messages using thread_service.get_messages_by_thread
        messages = self.thread_service.get_messages_by_thread(thread_id, pagination['page'], pagination['page_size'])

        # Mark messages as read for user_id using in_app_service
        self.in_app_service.mark_thread_as_read(thread_id, user_id)

        # Return the organized thread messages
        return messages

    def send_notification(self, notification_type: str, recipient_ids: List[str], context: dict, channels: List[str]) -> dict:
        """Sends a notification to recipients through configured channels

        Args:
            notification_type (str): Type of notification
            recipient_ids (List[str]): List of recipient IDs
            context (dict): Context data for notification
            channels (List[str]): List of notification channels

        Returns:
            dict: Notification delivery status for each recipient and channel
        """
        # Validate notification_type and recipient_ids
        if not notification_type or not recipient_ids:
            raise ValueError("Notification type and recipient IDs are required")

        # Process notification delivery using notification_service
        delivery_status = self.notification_service.process_notification(
            notification_type=notification_type,
            recipient_ids=recipient_ids,
            context=context,
            channels=channels
        )

        # Return delivery status for all recipients and channels
        return delivery_status

    def search_messages(self, user_id: str, filters: dict, pagination: dict) -> dict:
        """Searches messages with filtering options

        Args:
            user_id (str): ID of the user performing the search
            filters (dict): Filters to apply to the search
            pagination (dict): Pagination parameters

        Returns:
            dict: Matching messages with pagination info
        """
        # Validate user_id and filters
        if not user_id:
            raise ValueError("User ID is required")

        # Perform message search using thread_service
        search_results = self.thread_service.search_messages(
            user_id=user_id,
            filters=filters,
            page=pagination['page'],
            page_size=pagination['page_size']
        )

        # Filter messages based on user permissions
        filtered_messages = self.thread_service.filter_messages_by_permissions(search_results['messages'], user_id)

        # Return search results with pagination information
        return {
            "messages": filtered_messages,
            "page": pagination['page'],
            "page_size": pagination['page_size'],
            "total_results": search_results['total_results']
        }

    def get_user_notifications(self, user_id: str, include_read: bool, pagination: dict) -> dict:
        """Retrieves notifications for a specific user

        Args:
            user_id (str): ID of the user
            include_read (bool): Whether to include read notifications
            pagination (dict): Pagination parameters

        Returns:
            dict: User notifications with pagination info
        """
        # Validate user_id
        if not user_id:
            raise ValueError("User ID is required")

        # Retrieve notifications using in_app_service
        notifications = self.in_app_service.get_user_notifications(
            user_id=user_id,
            include_read=include_read,
            page=pagination['page'],
            page_size=pagination['page_size']
        )

        # Filter and sort notifications based on parameters
        filtered_notifications = self.in_app_service.filter_notifications(notifications, include_read)

        # Return notifications with pagination information
        return {
            "notifications": filtered_notifications,
            "page": pagination['page'],
            "page_size": pagination['page_size'],
            "total_notifications": len(filtered_notifications)
        }

    def mark_notifications_read(self, user_id: str, notification_ids: List[str]) -> bool:
        """Marks specified notifications as read for a user

        Args:
            user_id (str): ID of the user
            notification_ids (List[str]): List of notification IDs to mark as read

        Returns:
            bool: Success indication
        """
        # Validate user_id and notification_ids
        if not user_id or not notification_ids:
            raise ValueError("User ID and notification IDs are required")

        # Mark notifications as read using in_app_service
        success = self.in_app_service.mark_notifications_read(user_id, notification_ids)

        # Return success status
        return success

# Re-export the subservice classes for convenience
EmailService = EmailService
InAppMessageService = InAppMessageService
ThreadService = ThreadService
NotificationService = NotificationService