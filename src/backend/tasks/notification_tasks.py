"""
Celery tasks for processing and sending notifications throughout the Justice Bid Rate Negotiation System,
handling both email and in-app notifications for various event types.
"""

import typing
import json
from datetime import datetime

from celery import shared_task  # Third-party import: celery - version: N/A
from src.backend.services.messaging.notifications import NotificationService  # Internal import
from src.backend.services.messaging.in_app import InAppNotificationService  # Internal import
from src.backend.utils.email import EmailService  # Internal import
from src.backend.utils.logging import logger  # Internal import
from src.backend.db.session import db  # Internal import
from src.backend.utils.constants import NOTIFICATION_TYPES  # Internal import


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 5})
def send_user_notification(self, user_id: str, notification_type: str, context: dict, priority: str, force_email: bool) -> None:
    """
    Celery task for sending a notification to a single user via their preferred channels (email, in-app, etc.)
    """
    logger.info(f"Starting send_user_notification task for user {user_id}, type {notification_type}")
    try:
        # Get user notification preferences from NotificationService
        notification_service = NotificationService(db)
        user_preferences = notification_service.get_user_preferences(user_id, notification_type)

        # Check if user has opted in for this notification type
        if not user_preferences.get(notification_type, {}).get('enabled', True):
            logger.info(f"User {user_id} has disabled {notification_type} notifications")
            return

        # Prepare notification content based on notification type and context
        title = f"Notification: {notification_type}"
        content = f"You have a new notification of type {notification_type}"

        # If user prefers in-app notifications or notification is high priority, create in-app notification
        if user_preferences.get('in_app', True) or priority == 'high':
            in_app_service = InAppNotificationService(db)
            in_app_service.create_notification(user_id=user_id, notification_type=notification_type, title=title, content=content, priority=priority, context=context)
            logger.info(f"In-app notification created for user {user_id}")

        # If user prefers email notifications or force_email is True, send email notification
        if user_preferences.get('email', True) or force_email:
            email_service = EmailService()
            email_service.send_email(to_email=user_id, subject=title, content=content)
            logger.info(f"Email notification sent to user {user_id}")

        logger.info(f"Successfully delivered notification to user {user_id}")

    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {str(e)}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_organization_notification(self, organization_id: str, notification_type: str, context: dict, priority: str, role_filters: list) -> None:
    """
    Celery task for sending notifications to all relevant users within an organization
    """
    logger.info(f"Starting send_organization_notification task for org {organization_id}, type {notification_type}")
    try:
        # Query users belonging to the organization that match the role filters
        user_repository = UserRepository(db)
        users = user_repository.get_users_by_role(organization_id=organization_id, role_filters=role_filters)

        # Group users by notification preferences for batch processing
        email_users = []
        in_app_users = []
        notification_service = NotificationService(db)

        for user in users:
            user_preferences = notification_service.get_user_preferences(user.id, notification_type)
            if user_preferences.get('email', True):
                email_users.append(user.id)
            if user_preferences.get('in_app', True) or priority == 'high':
                in_app_users.append(user.id)

        # Prepare batch notifications
        title = f"Organization Notification: {notification_type}"
        content = f"Your organization has a new notification of type {notification_type}"

        # Send in-app notifications in batch for efficiency
        if in_app_users:
            in_app_service = InAppNotificationService(db)
            in_app_service.create_notifications_for_users(user_ids=in_app_users, notification_type=notification_type, title=title, content=content, priority=priority, metadata=context)
            logger.info(f"Batch in-app notifications created for {len(in_app_users)} users")

        # Send email notifications in batch for efficiency
        if email_users:
            email_service = EmailService()
            email_service.send_batch_email(to_emails=email_users, subject=title, content=content)
            logger.info(f"Batch email notifications sent to {len(email_users)} users")

        logger.info(f"Successfully dispatched notifications to organization {organization_id}")

    except Exception as e:
        logger.error(f"Error sending organization notification: {str(e)}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_negotiation_update_notification(self, negotiation_id: str, update_type: str, context: dict, notify_firm: bool, notify_client: bool) -> None:
    """
    Celery task for sending notifications about negotiation updates to relevant parties
    """
    logger.info(f"Starting send_negotiation_update_notification task for negotiation {negotiation_id}, update type {update_type}")
    try:
        # Retrieve negotiation details from database
        negotiation_repository = NegotiationRepository(db)
        negotiation = negotiation_repository.get_negotiation_by_id(negotiation_id)

        if not negotiation:
            logger.warning(f"Negotiation not found: {negotiation_id}")
            return

        # Determine the appropriate notification type based on update_type
        notification_type = f"negotiation_update_{update_type}"

        # If notify_firm is True, call send_organization_notification for the law firm
        if notify_firm:
            send_organization_notification.delay(organization_id=negotiation.firm_id, notification_type=notification_type, context=context, priority='medium', role_filters=[])

        # If notify_client is True, call send_organization_notification for the client
        if notify_client:
            send_organization_notification.delay(organization_id=negotiation.client_id, notification_type=notification_type, context=context, priority='medium', role_filters=[])

        logger.info("Successfully dispatched negotiation update notifications")

    except Exception as e:
        logger.error(f"Error sending negotiation update notification: {str(e)}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_rate_approval_notification(self, rate_id: str, approval_status: str, message: str, approver_id: str) -> None:
    """
    Celery task for sending notifications about rate approvals to relevant parties
    """
    logger.info(f"Starting send_rate_approval_notification task for rate {rate_id}, status {approval_status}")
    try:
        # Retrieve rate details from database including attorney and negotiation information
        # Determine notification type based on approval_status (approved, rejected, countered)
        notification_type = f"rate_approval_{approval_status}"

        # Prepare context with rate information, message, and approver details
        context = {
            'rate_id': rate_id,
            'approval_status': approval_status,
            'message': message,
            'approver_id': approver_id
        }

        # Determine recipient organizations based on approval_status and notification rules
        # Send organization notifications to each recipient organization
        # For simplicity, sending to both client and firm for now
        # In a real system, this would be more nuanced
        send_organization_notification.delay(organization_id='client_org_id', notification_type=notification_type, context=context, priority='high', role_filters=[])
        send_organization_notification.delay(organization_id='firm_org_id', notification_type=notification_type, context=context, priority='high', role_filters=[])

        logger.info("Successfully dispatched rate approval notifications")

    except Exception as e:
        logger.error(f"Error sending rate approval notification: {str(e)}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_approval_workflow_notification(self, workflow_id: str, event_type: str, approver_ids: list, context: dict) -> None:
    """
    Celery task for sending notifications about approval workflow events
    """
    logger.info(f"Starting send_approval_workflow_notification task for workflow {workflow_id}, event {event_type}")
    try:
        # Retrieve workflow details from database
        # Determine appropriate notification type based on event_type
        notification_type = f"approval_workflow_{event_type}"

        # Prepare context with workflow information and entity details
        context['workflow_id'] = workflow_id

        # For each approver_id, call send_user_notification with high priority
        for approver_id in approver_ids:
            send_user_notification.delay(user_id=approver_id, notification_type=notification_type, context=context, priority='high', force_email=True)

        logger.info("Successfully dispatched approval workflow notifications")

    except Exception as e:
        logger.error(f"Error sending approval workflow notification: {str(e)}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_message_notification(self, message_id: str, recipient_ids: list) -> None:
    """
    Celery task for sending notifications about new messages
    """
    logger.info(f"Starting send_message_notification task for message {message_id}")
    try:
        # Retrieve message details from database
        # Prepare context with message content, sender, and thread information
        context = {
            'message_id': message_id
        }

        # For each recipient_id, call send_user_notification
        for recipient_id in recipient_ids:
            send_user_notification.delay(user_id=recipient_id, notification_type='new_message', context=context, priority='medium', force_email=False)

        logger.info("Successfully dispatched message notifications")

    except Exception as e:
        logger.error(f"Error sending message notification: {str(e)}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_ocg_update_notification(self, ocg_id: str, update_type: str, context: dict, notify_firm: bool, notify_client: bool) -> None:
    """
    Celery task for sending notifications about Outside Counsel Guidelines updates
    """
    logger.info(f"Starting send_ocg_update_notification task for OCG {ocg_id}, update type {update_type}")
    try:
        # Retrieve OCG details from database
        # Determine appropriate notification type based on update_type
        notification_type = f"ocg_update_{update_type}"

        # Prepare context with OCG information and update details
        context['ocg_id'] = ocg_id

        # If notify_firm is True, send organization notification to the law firm
        if notify_firm:
            send_organization_notification.delay(organization_id='firm_org_id', notification_type=notification_type, context=context, priority='medium', role_filters=[])

        # If notify_client is True, send organization notification to the client
        if notify_client:
            send_organization_notification.delay(organization_id='client_org_id', notification_type=notification_type, context=context, priority='medium', role_filters=[])

        logger.info("Successfully dispatched OCG update notifications")

    except Exception as e:
        logger.error(f"Error sending OCG update notification: {str(e)}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 3})
def process_notification_queue(self, batch_size: int = 100) -> int:
    """
    Celery task for processing the notification queue in batches
    """
    logger.info(f"Starting process_notification_queue task with batch size {batch_size}")
    try:
        # Query pending notifications from database up to batch_size
        # Group notifications by type and recipient for efficient processing
        # Process each group using the appropriate notification method
        # Mark processed notifications as sent
        # For demonstration purposes, just logging the task execution
        logger.info(f"Processing {batch_size} notifications from the queue")
        return batch_size

    except Exception as e:
        logger.error(f"Error processing notification queue: {str(e)}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 3})
def clean_old_notifications(self, days_to_keep: int = 30) -> int:
    """
    Celery task for cleaning up old notifications based on retention policy
    """
    logger.info(f"Starting clean_old_notifications task, keeping notifications for {days_to_keep} days")
    try:
        # Calculate the cutoff date based on days_to_keep
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days_to_keep)

        # Query notifications older than the cutoff date
        # Delete or archive the old notifications based on configuration
        # For demonstration purposes, just logging the task execution
        logger.info(f"Cleaning notifications older than {cutoff_date}")
        return 100  # Placeholder for number of notifications cleaned up

    except Exception as e:
        logger.error(f"Error cleaning old notifications: {str(e)}", exc_info=True)
        raise self.retry(exc=e)