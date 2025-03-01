"""
Asynchronous Celery tasks for handling email sending operations in the Justice Bid Rate Negotiation System.

This module provides task definitions for sending various types of emails including password reset emails,
welcome emails, rate notification emails, negotiation updates, and approval workflow notifications.
"""

from celery import shared_task
from datetime import datetime
import time
import json

from ..utils.logging import get_logger
from ..utils.email import send_email
from ..services.messaging.email import get_email_template
from .celery_app import CELERY_APP

# Initialize logger
logger = get_logger(__name__)

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 300  # 5 minutes in seconds


@shared_task(bind=True, max_retries=3)
def send_email_task(self, email_data, retry_on_failure=True):
    """
    Asynchronous task to send a single email with retry capability.
    
    Args:
        email_data (dict): Email data including recipient, subject, and body
        retry_on_failure (bool): Whether to retry on failure
    
    Returns:
        bool: Success status of the email sending operation
    """
    # If email_data is not a dict, log an error and return False
    if not isinstance(email_data, dict):
        logger.error("Invalid email data: not a dictionary", 
                    extra={"additional_data": {"email_data_type": type(email_data).__name__}})
        return False
    
    # Extract recipient for logging
    recipient = email_data.get("recipient", "unknown")
    logger.info(f"Starting email task", extra={"additional_data": {"recipient": recipient}})
    
    # Validate email data
    if not email_data.get("recipient") or not email_data.get("subject") or not email_data.get("body"):
        logger.error("Invalid email data: missing required fields", 
                    extra={"additional_data": {"email_data": email_data}})
        return False
    
    try:
        # Extract email components
        recipient = email_data.get("recipient")
        subject = email_data.get("subject")
        body = email_data.get("body")
        is_html = email_data.get("is_html", True)
        cc = email_data.get("cc", [])
        bcc = email_data.get("bcc", [])
        attachments = email_data.get("attachments", [])
        headers = email_data.get("headers", {})
        from_email = email_data.get("from_email", None)
        
        # Send email using the send_email utility
        result = send_email(
            to_email=recipient,
            subject=subject,
            body=body,
            from_email=from_email,
            html=is_html,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            headers=headers
        )
        
        if result:
            logger.info(f"Email sent successfully", 
                      extra={"additional_data": {"recipient": recipient, "subject": subject}})
            return True
        else:
            raise Exception("Email sending failed")
            
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", 
                    extra={"additional_data": {"recipient": recipient, "error": str(e)}})
        
        # Retry if configured to do so and task is called in a Celery context
        if retry_on_failure and hasattr(self, 'request') and self.request:
            retry_count = getattr(self.request, 'retries', 0)
            if retry_count < MAX_RETRIES:
                retry_delay = RETRY_DELAY * (2 ** retry_count)  # Exponential backoff
                logger.info(f"Retrying email task in {retry_delay} seconds", 
                          extra={"additional_data": {"retry": retry_count + 1, "max_retries": MAX_RETRIES}})
                
                self.retry(exc=e, countdown=retry_delay)
            else:
                logger.error(f"Maximum retry attempts ({MAX_RETRIES}) reached for email task", 
                           extra={"additional_data": {"recipient": recipient}})
        
        return False


@shared_task(bind=True, max_retries=3)
def send_templated_email_task(self, template_name, template_data, recipient_email, subject, retry_on_failure=True):
    """
    Asynchronous task to send an email using a template.
    
    Args:
        template_name (str): Name of the email template to use
        template_data (dict): Data to populate the template
        recipient_email (str): Recipient's email address
        subject (str): Email subject
        retry_on_failure (bool): Whether to retry on failure
    
    Returns:
        bool: Success status of the email sending operation
    """
    logger.info(f"Starting templated email task", 
               extra={"additional_data": {"recipient": recipient_email, "template": template_name}})
    
    try:
        # Validate input parameters
        if not template_name or not recipient_email or not subject:
            logger.error("Invalid parameters for templated email", 
                       extra={"additional_data": {"template": template_name, "recipient": recipient_email}})
            return False
        
        # Get the email template content
        template_content = get_email_template(template_name, template_data)
        
        if not template_content:
            logger.error(f"Failed to retrieve or render template: {template_name}", 
                       extra={"additional_data": {"template_data": template_data}})
            return False
        
        # Create email data dictionary
        email_data = {
            "recipient": recipient_email,
            "subject": subject,
            "body": template_content,
            "is_html": True
        }
        
        # Use the send_email_task to send the email
        return send_email_task(email_data, retry_on_failure)
        
    except Exception as e:
        logger.error(f"Error in templated email task: {str(e)}", 
                    extra={"additional_data": {"recipient": recipient_email, "template": template_name, "error": str(e)}})
        
        # Retry if configured to do so
        if retry_on_failure and hasattr(self, 'request') and self.request:
            retry_count = getattr(self.request, 'retries', 0)
            if retry_count < MAX_RETRIES:
                retry_delay = RETRY_DELAY * (2 ** retry_count)  # Exponential backoff
                self.retry(exc=e, countdown=retry_delay)
            else:
                logger.error(f"Maximum retry attempts ({MAX_RETRIES}) reached for templated email task", 
                           extra={"additional_data": {"recipient": recipient_email}})
        
        return False


@shared_task
def send_batch_emails_task(email_data_list, retry_on_failure=True):
    """
    Asynchronous task to send multiple emails in batch.
    
    Args:
        email_data_list (list): List of email data dictionaries
        retry_on_failure (bool): Whether to retry on failure
    
    Returns:
        dict: Summary of batch email sending results
    """
    logger.info(f"Starting batch email sending task", 
               extra={"additional_data": {"count": len(email_data_list)}})
    
    # Initialize counters
    success_count = 0
    failure_count = 0
    
    # Process each email in the batch
    for email_data in email_data_list:
        try:
            # Queue individual email tasks
            send_email_task.delay(email_data, retry_on_failure)
            success_count += 1
        except Exception as e:
            recipient = email_data.get("recipient", "unknown")
            logger.error(f"Error processing email in batch: {str(e)}", 
                        extra={"additional_data": {"recipient": recipient, "error": str(e)}})
            failure_count += 1
    
    # Log the batch results
    total_count = len(email_data_list)
    logger.info(f"Batch email sending completed", 
               extra={"additional_data": {
                   "total": total_count,
                   "success": success_count,
                   "failure": failure_count
               }})
    
    # Return a summary of the batch operation
    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "total_count": total_count
    }


@shared_task
def send_password_reset_email_task(user_email, reset_token, user_name):
    """
    Specialized task to send password reset emails.
    
    Args:
        user_email (str): Recipient's email address
        reset_token (str): Password reset token
        user_name (str): User's name for personalization
    
    Returns:
        bool: Success status of the email sending operation
    """
    logger.info(f"Sending password reset email", extra={"additional_data": {"recipient": user_email}})
    
    try:
        # Construct the reset URL with the token
        from ..app.config import AppConfig
        settings = AppConfig().config
        reset_url = f"{settings.APP_URL}/reset-password?token={reset_token}"
        
        # Prepare template data
        template_data = {
            "user_name": user_name,
            "reset_url": reset_url,
            "expiry_hours": 24,  # Token typically expires in 24 hours
            "company_name": "Justice Bid",
            "support_email": "support@justicebid.com"
        }
        
        # Send the email using the password_reset template
        send_templated_email_task.delay(
            "password_reset", 
            template_data, 
            user_email, 
            "Password Reset Request"
        )
        return True
        
    except Exception as e:
        logger.error(f"Error sending password reset email: {str(e)}", 
                    extra={"additional_data": {"recipient": user_email, "error": str(e)}})
        return False


@shared_task
def send_welcome_email_task(user_email, user_name, organization_name):
    """
    Specialized task to send welcome emails to new users.
    
    Args:
        user_email (str): Recipient's email address
        user_name (str): User's name for personalization
        organization_name (str): Name of the user's organization
    
    Returns:
        bool: Success status of the email sending operation
    """
    logger.info(f"Sending welcome email", extra={"additional_data": {"recipient": user_email}})
    
    try:
        # Get application URL from configuration
        from ..app.config import AppConfig
        settings = AppConfig().config
        
        # Prepare template data
        template_data = {
            "user_name": user_name,
            "organization_name": organization_name,
            "app_url": settings.APP_URL,
            "support_email": "support@justicebid.com",
            "help_url": f"{settings.APP_URL}/help"
        }
        
        # Send the email using the welcome template
        subject = f"Welcome to Justice Bid, {user_name}!"
        send_templated_email_task.delay(
            "welcome", 
            template_data, 
            user_email, 
            subject
        )
        return True
        
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}", 
                    extra={"additional_data": {"recipient": user_email, "error": str(e)}})
        return False


@shared_task
def send_rate_notification_email_task(notification_type, recipient_email, recipient_name, rate_data, organization_name):
    """
    Specialized task to send rate notification emails.
    
    Args:
        notification_type (str): Type of notification (request, submission, approval, rejection, counter)
        recipient_email (str): Recipient's email address
        recipient_name (str): Recipient's name for personalization
        rate_data (dict): Data about the rates being notified
        organization_name (str): Name of the originating organization
    
    Returns:
        bool: Success status of the email sending operation
    """
    logger.info(f"Sending rate notification email", 
               extra={"additional_data": {"recipient": recipient_email, "type": notification_type}})
    
    try:
        # Validate notification type
        valid_types = ["request", "submission", "approval", "rejection", "counter"]
        if notification_type not in valid_types:
            logger.error(f"Invalid rate notification type: {notification_type}", 
                       extra={"additional_data": {"valid_types": valid_types}})
            return False
        
        # Get application URL from configuration
        from ..app.config import AppConfig
        settings = AppConfig().config
        
        # Prepare template data
        template_data = {
            "recipient_name": recipient_name,
            "rate_data": rate_data,
            "organization_name": organization_name,
            "app_url": settings.APP_URL,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Determine template and subject based on notification type
        template_mapping = {
            "request": ("rate_request", f"Rate Request from {organization_name}"),
            "submission": ("rate_submission", f"Rate Submission from {organization_name}"),
            "approval": ("rate_approval", f"Rate Approval from {organization_name}"),
            "rejection": ("rate_rejection", f"Rate Rejection from {organization_name}"),
            "counter": ("rate_counter", f"Rate Counter-Proposal from {organization_name}")
        }
        
        template_name, subject = template_mapping[notification_type]
        
        # Send the email
        send_templated_email_task.delay(
            template_name, 
            template_data, 
            recipient_email, 
            subject
        )
        return True
        
    except Exception as e:
        logger.error(f"Error sending rate notification email: {str(e)}", 
                    extra={"additional_data": {
                        "recipient": recipient_email, 
                        "type": notification_type,
                        "error": str(e)
                    }})
        return False


@shared_task
def send_negotiation_update_email_task(update_type, recipient_email, recipient_name, negotiation_data, organization_name):
    """
    Specialized task to send negotiation update emails.
    
    Args:
        update_type (str): Type of update (started, updated, completed, etc.)
        recipient_email (str): Recipient's email address
        recipient_name (str): Recipient's name for personalization
        negotiation_data (dict): Data about the negotiation
        organization_name (str): Name of the originating organization
    
    Returns:
        bool: Success status of the email sending operation
    """
    logger.info(f"Sending negotiation update email", 
               extra={"additional_data": {"recipient": recipient_email, "type": update_type}})
    
    try:
        # Validate update type
        valid_types = ["started", "updated", "completed", "rejected", "message"]
        if update_type not in valid_types:
            logger.error(f"Invalid negotiation update type: {update_type}", 
                       extra={"additional_data": {"valid_types": valid_types}})
            return False
        
        # Get application URL from configuration
        from ..app.config import AppConfig
        settings = AppConfig().config
        
        # Prepare template data
        template_data = {
            "recipient_name": recipient_name,
            "negotiation_data": negotiation_data,
            "organization_name": organization_name,
            "app_url": settings.APP_URL,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Determine template and subject based on update type
        template_mapping = {
            "started": ("negotiation_started", f"Negotiation Started by {organization_name}"),
            "updated": ("negotiation_updated", f"Negotiation Updated by {organization_name}"),
            "completed": ("negotiation_completed", f"Negotiation Completed with {organization_name}"),
            "rejected": ("negotiation_rejected", f"Negotiation Rejected by {organization_name}"),
            "message": ("negotiation_message", f"New Message in Negotiation with {organization_name}")
        }
        
        template_name, subject = template_mapping[update_type]
        
        # Send the email
        send_templated_email_task.delay(
            template_name, 
            template_data, 
            recipient_email, 
            subject
        )
        return True
        
    except Exception as e:
        logger.error(f"Error sending negotiation update email: {str(e)}", 
                    extra={"additional_data": {
                        "recipient": recipient_email, 
                        "type": update_type,
                        "error": str(e)
                    }})
        return False


@shared_task
def send_approval_workflow_email_task(workflow_action, recipient_email, recipient_name, approval_data):
    """
    Specialized task to send approval workflow emails.
    
    Args:
        workflow_action (str): Type of workflow action (requested, approved, rejected, etc.)
        recipient_email (str): Recipient's email address
        recipient_name (str): Recipient's name for personalization
        approval_data (dict): Data about the approval workflow
    
    Returns:
        bool: Success status of the email sending operation
    """
    logger.info(f"Sending approval workflow email", 
               extra={"additional_data": {"recipient": recipient_email, "action": workflow_action}})
    
    try:
        # Validate workflow action
        valid_actions = ["requested", "approved", "rejected", "escalated", "reminder"]
        if workflow_action not in valid_actions:
            logger.error(f"Invalid approval workflow action: {workflow_action}", 
                       extra={"additional_data": {"valid_actions": valid_actions}})
            return False
        
        # Get application URL from configuration
        from ..app.config import AppConfig
        settings = AppConfig().config
        
        # Prepare template data
        template_data = {
            "recipient_name": recipient_name,
            "approval_data": approval_data,
            "app_url": settings.APP_URL,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add requester name if present in approval data
        if "requester_name" in approval_data:
            template_data["requester_name"] = approval_data["requester_name"]
        
        # Determine template and subject based on workflow action
        template_mapping = {
            "requested": ("approval_requested", "Approval Requested"),
            "approved": ("approval_granted", "Approval Granted"),
            "rejected": ("approval_rejected", "Approval Rejected"),
            "escalated": ("approval_escalated", "Approval Escalated"),
            "reminder": ("approval_reminder", "Approval Reminder")
        }
        
        template_name, subject_base = template_mapping[workflow_action]
        
        # Add context to subject if available
        subject = subject_base
        if "context" in approval_data and approval_data["context"]:
            subject = f"{subject_base}: {approval_data['context']}"
        
        # Send the email
        send_templated_email_task.delay(
            template_name, 
            template_data, 
            recipient_email, 
            subject
        )
        return True
        
    except Exception as e:
        logger.error(f"Error sending approval workflow email: {str(e)}", 
                    extra={"additional_data": {
                        "recipient": recipient_email, 
                        "action": workflow_action,
                        "error": str(e)
                    }})
        return False


@shared_task
def send_ocg_notification_email_task(notification_type, recipient_email, recipient_name, ocg_data, organization_name):
    """
    Specialized task to send Outside Counsel Guidelines notification emails.
    
    Args:
        notification_type (str): Type of notification (published, updated, negotiation, etc.)
        recipient_email (str): Recipient's email address
        recipient_name (str): Recipient's name for personalization
        ocg_data (dict): Data about the OCG
        organization_name (str): Name of the originating organization
    
    Returns:
        bool: Success status of the email sending operation
    """
    logger.info(f"Sending OCG notification email", 
               extra={"additional_data": {"recipient": recipient_email, "type": notification_type}})
    
    try:
        # Validate notification type
        valid_types = ["published", "updated", "negotiation_requested", "negotiation_response", "signed"]
        if notification_type not in valid_types:
            logger.error(f"Invalid OCG notification type: {notification_type}", 
                       extra={"additional_data": {"valid_types": valid_types}})
            return False
        
        # Get application URL from configuration
        from ..app.config import AppConfig
        settings = AppConfig().config
        
        # Prepare template data
        template_data = {
            "recipient_name": recipient_name,
            "ocg_data": ocg_data,
            "organization_name": organization_name,
            "app_url": settings.APP_URL,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Determine template and subject based on notification type
        template_mapping = {
            "published": ("ocg_published", f"New Outside Counsel Guidelines from {organization_name}"),
            "updated": ("ocg_updated", f"Updated Outside Counsel Guidelines from {organization_name}"),
            "negotiation_requested": ("ocg_negotiation_requested", f"OCG Negotiation Requested by {organization_name}"),
            "negotiation_response": ("ocg_negotiation_response", f"OCG Negotiation Response from {organization_name}"),
            "signed": ("ocg_signed", f"OCG Agreement Signed with {organization_name}")
        }
        
        template_name, subject = template_mapping[notification_type]
        
        # Send the email
        send_templated_email_task.delay(
            template_name, 
            template_data, 
            recipient_email, 
            subject
        )
        return True
        
    except Exception as e:
        logger.error(f"Error sending OCG notification email: {str(e)}", 
                    extra={"additional_data": {
                        "recipient": recipient_email, 
                        "type": notification_type,
                        "error": str(e)
                    }})
        return False