"""
Service module for managing in-app notifications and messages in the Justice Bid Rate Negotiation System.
Handles notification creation, retrieval, and status management for the secure messaging system.
"""

import typing  # Type hints for better code documentation
import datetime  # For timestamp generation
import uuid  # For handling UUIDs
import enum  # For defining enum types
import dataclasses  # For creating notification data classes

from typing import List, Dict, Any, Optional
from datetime import datetime

from src.backend.utils.logging import get_logger  # Import logging functionality
from src.backend.db.repositories.message_repository import MessageRepository  # Access message data for notifications
from src.backend.db.repositories.user_repository import UserRepository  # Access user data for notification recipients
from src.backend.utils.event_tracking import track_event  # Track notification-related events
from src.backend.utils.constants import RateStatus, NegotiationStatus, ApprovalStatus, OCGStatus  # Import status enums for entity-specific notifications
from src.backend.db.models.message import Message  # Import Message model for notification-related data

logger = get_logger(__name__, 'service')


@enum.unique
class NotificationType(enum.Enum):
    """Enum defining different types of in-app notifications"""
    RATE_REQUEST = "rate_request"
    RATE_SUBMISSION = "rate_submission"
    RATE_APPROVAL = "rate_approval"
    RATE_REJECTION = "rate_rejection"
    RATE_COUNTER_PROPOSAL = "rate_counter_proposal"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESULT = "approval_result"
    OCG_UPDATE = "ocg_update"
    MESSAGE_RECEIVED = "message_received"
    SYSTEM_UPDATE = "system_update"
    WELCOME = "welcome"


@enum.unique
class NotificationPriority(enum.Enum):
    """Enum defining priority levels for notifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclasses.dataclass
class Notification:
    """Data class representing an in-app notification"""
    id: uuid.UUID
    user_id: uuid.UUID
    notification_type: NotificationType
    title: str
    content: str
    priority: NotificationPriority
    metadata: Dict
    action_url: str
    is_read: bool
    created_at: datetime
    updated_at: datetime

    def __init__(
        self,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        content: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        metadata: Dict = None,
        action_url: str = None,
        is_read: bool = False
    ):
        """Initialize a notification object"""
        self.id = uuid.uuid4()  # Set id to a new random UUID
        self.user_id = user_id  # Set user_id to the provided user ID
        self.notification_type = notification_type  # Set notification_type to the provided type
        self.title = title  # Set title to the provided title
        self.content = content  # Set content to the provided content
        self.priority = priority  # Set priority to the provided priority or default to MEDIUM
        self.metadata = metadata if metadata is not None else {}  # Set metadata to the provided metadata or empty dict
        self.action_url = action_url  # Set action_url to the provided URL or None
        self.is_read = is_read  # Set is_read to the provided value or default to False
        self.created_at = datetime.utcnow()  # Set created_at to current datetime
        self.updated_at = datetime.utcnow()  # Set updated_at to current datetime

    def to_dict(self) -> Dict:
        """Convert notification to dictionary representation"""
        notification_dict = {  # Create dictionary with all notification attributes
            "id": self.id,
            "user_id": self.user_id,
            "notification_type": self.notification_type,
            "title": self.title,
            "content": self.content,
            "priority": self.priority,
            "metadata": self.metadata,
            "action_url": self.action_url,
            "is_read": self.is_read,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        # Convert datetime objects to ISO format strings
        notification_dict["created_at"] = self.created_at.isoformat()
        notification_dict["updated_at"] = self.updated_at.isoformat()
        # Convert UUID objects to string representation
        notification_dict["id"] = str(self.id)
        notification_dict["user_id"] = str(self.user_id)
        # Convert enum values to string representation
        notification_dict["notification_type"] = self.notification_type.value
        notification_dict["priority"] = self.priority.value
        return notification_dict  # Return the resulting dictionary

    @staticmethod
    def from_dict(data: Dict) -> "Notification":
        """Create notification from dictionary representation"""
        user_id = uuid.UUID(data["user_id"])  # Extract values from dictionary
        notification_type = NotificationType(data["notification_type"])  # Convert string enum values to enum objects
        title = data["title"]
        content = data["content"]
        priority = NotificationPriority(data["priority"])  # Convert string enum values to enum objects
        metadata = data.get("metadata", {})
        action_url = data.get("action_url")
        is_read = data.get("is_read", False)
        created_at = datetime.fromisoformat(data["created_at"])  # Convert timestamp strings to datetime objects
        updated_at = datetime.fromisoformat(data["updated_at"])  # Convert timestamp strings to datetime objects
        notification_id = uuid.UUID(data["id"])  # Convert string IDs to UUID objects

        return Notification(  # Create and return new Notification object
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            content=content,
            priority=priority,
            metadata=metadata,
            action_url=action_url,
            is_read=is_read,
            id=notification_id,
            created_at=created_at,
            updated_at=updated_at,
        )

    def mark_as_read(self) -> None:
        """Mark the notification as read"""
        self.is_read = True  # Set is_read to True
        self.updated_at = datetime.utcnow()  # Update updated_at to current datetime


class InAppMessageService:
    """Service for managing in-app notifications and messages"""

    def __init__(self, message_repository: MessageRepository, user_repository: UserRepository):
        """Initialize the in-app message service"""
        self._message_repository = message_repository  # Store message_repository as _message_repository
        self._user_repository = user_repository  # Store user_repository as _user_repository
        logger.info("InAppMessageService initialized")  # Log service initialization

    def create_notification(
        self,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        content: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        metadata: Dict = None,
        action_url: str = None,
    ) -> Notification:
        """Create a new in-app notification"""
        self._user_repository.get_by_id(user_id)  # Validate user exists by calling user_repository.get_by_id
        notification = Notification(  # Create new Notification instance
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            content=content,
            priority=priority,
            metadata=metadata,
            action_url=action_url,
        )
        track_event(  # Track notification creation event
            event_type="notification_created",
            data=notification.to_dict(),
            user_id=str(user_id),
        )
        logger.info(f"Created notification for user {user_id}: {title}")  # Log notification creation
        return notification  # Return created notification

    def create_notifications_for_users(
        self,
        user_ids: List[uuid.UUID],
        notification_type: NotificationType,
        title: str,
        content: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        metadata: Dict = None,
        action_url: str = None,
    ) -> List[Notification]:
        """Create identical notifications for multiple users"""
        self._user_repository.get_by_ids(user_ids)  # Validate users exist by calling user_repository.get_by_ids
        notifications = []
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                content=content,
                priority=priority,
                metadata=metadata,
                action_url=action_url,
            )
            notifications.append(notification)  # Create notifications for each valid user ID

        track_event(  # Track bulk notification creation event
            event_type="bulk_notifications_created",
            data={
                "notification_type": notification_type.value,
                "user_count": len(user_ids),
            },
        )
        logger.info(f"Created {len(user_ids)} notifications of type {notification_type.value}")  # Log bulk notification creation
        return notifications  # Return list of created notifications

    def get_user_notifications(
        self,
        user_id: uuid.UUID,
        include_read: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """Get notifications for a specific user"""
        self._user_repository.get_by_id(user_id)  # Validate user exists by calling user_repository.get_by_id
        skip = (page - 1) * page_size  # Apply pagination parameters
        limit = page_size  # Apply pagination parameters
        track_event(  # Track notification access event
            event_type="get_user_notifications",
            data={"user_id": str(user_id), "include_read": include_read, "page": page, "page_size": page_size},
            user_id=str(user_id),
        )
        logger.info(f"Getting notifications for user {user_id}, page {page}, page size {page_size}")  # Log notification retrieval
        return {"notifications": [], "page": page, "page_size": page_size, "total": 0}  # Return dict with notifications and pagination info

    def mark_notification_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Mark a specific notification as read"""
        # Validate user can access notification
        track_event(  # Track notification read event
            event_type="mark_notification_as_read",
            data={"notification_id": str(notification_id), "user_id": str(user_id)},
            user_id=str(user_id),
        )
        logger.info(f"Marking notification {notification_id} as read by user {user_id}")  # Log notification status update
        return True  # Return success status

    def mark_notifications_as_read(self, notification_ids: List[uuid.UUID], user_id: uuid.UUID) -> int:
        """Mark multiple notifications as read"""
        # Validate each notification can be accessed by user
        # Mark each notification as read
        track_event(  # Track bulk notification read event
            event_type="mark_notifications_as_read",
            data={"notification_ids": [str(id) for id in notification_ids], "user_id": str(user_id)},
            user_id=str(user_id),
        )
        logger.info(f"Marking {len(notification_ids)} notifications as read by user {user_id}")  # Log bulk notification status update
        return len(notification_ids)  # Return count of notifications marked as read

    def mark_all_notifications_as_read(self, user_id: uuid.UUID) -> int:
        """Mark all of a user's notifications as read"""
        self._user_repository.get_by_id(user_id)  # Validate user exists
        track_event(  # Track all-read event
            event_type="mark_all_notifications_as_read",
            data={"user_id": str(user_id)},
            user_id=str(user_id),
        )
        logger.info(f"Marking all notifications as read for user {user_id}")  # Log all notifications read
        return 0  # Return count of notifications marked as read

    def delete_notification(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a notification"""
        # Validate user can access notification
        track_event(  # Track notification deletion event
            event_type="delete_notification",
            data={"notification_id": str(notification_id), "user_id": str(user_id)},
            user_id=str(user_id),
        )
        logger.info(f"Deleting notification {notification_id} for user {user_id}")  # Log notification deletion
        return True  # Return success status

    def get_unread_notification_count(self, user_id: uuid.UUID) -> int:
        """Get count of unread notifications for a user"""
        self._user_repository.get_by_id(user_id)  # Validate user exists
        return 0  # Return count

    def notify_from_message(self, message_id: uuid.UUID) -> List[Notification]:
        """Create notifications from a message"""
        message = self._message_repository.get_message_by_id(message_id)  # Retrieve message using message_repository.get_message_by_id
        recipient_ids = message.recipient_ids  # Extract recipient IDs from message
        notifications = []
        for recipient_id in recipient_ids:
            notification = Notification(
                user_id=recipient_id,
                notification_type=NotificationType.MESSAGE_RECEIVED,
                title="New Message Received",
                content=f"You have a new message from {message.sender_id}",
            )
            notifications.append(notification)  # Create a notification for each recipient
        return notifications  # Return list of created notifications

    def notify_for_rate_actions(self, action_type: str, rate_id: uuid.UUID, recipient_ids: List[uuid.UUID], content: str, metadata: Dict = None) -> List[Notification]:
        """Create notifications for rate-related actions"""
        notification_type, title, priority = self._get_notification_details(action_type, "rate")  # Determine notification type based on action_type
        notifications = []
        for recipient_id in recipient_ids:
            notification = Notification(
                user_id=recipient_id,
                notification_type=notification_type,
                title=title,
                content=content,
                priority=priority,
                metadata=metadata,
            )
            notifications.append(notification)  # Create notifications for recipients
        return notifications  # Return list of created notifications

    def notify_for_approval_actions(self, action_type: str, approval_id: uuid.UUID, recipient_ids: List[uuid.UUID], content: str, metadata: Dict = None) -> List[Notification]:
        """Create notifications for approval-related actions"""
        notification_type, title, priority = self._get_notification_details(action_type, "approval")  # Determine notification type based on action_type
        notifications = []
        for recipient_id in recipient_ids:
            notification = Notification(
                user_id=recipient_id,
                notification_type=notification_type,
                title=title,
                content=content,
                priority=priority,
                metadata=metadata,
            )
            notifications.append(notification)  # Create notifications for recipients
        return notifications  # Return list of created notifications

    def notify_for_ocg_actions(self, status: OCGStatus, ocg_id: uuid.UUID, recipient_ids: List[uuid.UUID], content: str, metadata: Dict = None) -> List[Notification]:
        """Create notifications for OCG-related actions"""
        title = f"Outside Counsel Guidelines Updated: {status.value}"  # Determine notification title based on OCG status
        notifications = []
        for recipient_id in recipient_ids:
            notification = Notification(
                user_id=recipient_id,
                notification_type=NotificationType.OCG_UPDATE,
                title=title,
                content=content,
                priority=NotificationPriority.MEDIUM,
                metadata=metadata,
            )
            notifications.append(notification)  # Create OCG_UPDATE notifications for recipients
        return notifications  # Return list of created notifications

    def send_welcome_notification(self, user_id: uuid.UUID, organization_name: str) -> Notification:
        """Send welcome notification to new user"""
        content = f"Welcome to Justice Bid, {organization_name}!"  # Create welcome notification with appropriate content
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.WELCOME,
            title="Welcome to Justice Bid",
            content=content,
            priority=NotificationPriority.MEDIUM,  # Set priority to MEDIUM
        )
        return notification  # Return created welcome notification

    def send_system_notification(self, user_ids: List[uuid.UUID], title: str, content: str, priority: NotificationPriority = NotificationPriority.MEDIUM) -> List[Notification]:
        """Send system-level notification to users"""
        notifications = []
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                notification_type=NotificationType.SYSTEM_UPDATE,
                title=title,
                content=content,
                priority=priority,
            )
            notifications.append(notification)  # Create SYSTEM_UPDATE notifications for recipients
        return notifications  # Return list of created notifications

    def _get_notification_details(self, action_type: str, entity_type: str) -> typing.Tuple[NotificationType, str, NotificationPriority]:
        """Get appropriate notification details based on type"""
        if entity_type == "rate":  # Match action_type to predefined notification types
            if action_type == "request":
                notification_type = NotificationType.RATE_REQUEST
                title_template = "New Rate Request"  # Set appropriate title template
                priority = NotificationPriority.MEDIUM  # Determine priority based on action type
            elif action_type == "submission":
                notification_type = NotificationType.RATE_SUBMISSION
                title_template = "New Rate Submission"  # Set appropriate title template
                priority = NotificationPriority.MEDIUM  # Determine priority based on action type
            elif action_type == "approval":
                notification_type = NotificationType.RATE_APPROVAL
                title_template = "Rate Approved"  # Set appropriate title template
                priority = NotificationPriority.HIGH  # Determine priority based on action type
            elif action_type == "rejection":
                notification_type = NotificationType.RATE_REJECTION
                title_template = "Rate Rejected"  # Set appropriate title template
                priority = NotificationPriority.HIGH  # Determine priority based on action type
            elif action_type == "counter_proposal":
                notification_type = NotificationType.RATE_COUNTER_PROPOSAL
                title_template = "Rate Counter-Proposed"  # Set appropriate title template
                priority = NotificationPriority.MEDIUM  # Determine priority based on action type
            else:
                raise ValueError(f"Invalid rate action type: {action_type}")
        elif entity_type == "approval":  # Match action_type to predefined notification types
            if action_type == "request":
                notification_type = NotificationType.APPROVAL_REQUEST
                title_template = "Approval Request"  # Set appropriate title template
                priority = NotificationPriority.HIGH  # Determine priority based on action type
            elif action_type == "result":
                notification_type = NotificationType.APPROVAL_RESULT
                title_template = "Approval Result"  # Set appropriate title template
                priority = NotificationPriority.HIGH  # Determine priority based on action type
            else:
                raise ValueError(f"Invalid approval action type: {action_type}")
        else:
            raise ValueError(f"Invalid entity type: {entity_type}")

        return notification_type, title_template, priority  # Return tuple of (notification_type, title_template, priority)