"""
Email service component for the Justice Bid Rate Negotiation System.

This module handles sending email notifications to users based on system events
such as rate requests, rate submissions, counter-proposals, and approvals.
It supports HTML templated emails and integrates with Celery for asynchronous sending.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional

from jinja2 import Environment, FileSystemLoader

from ...app.config import settings
from ...tasks.celery_app import app as celery_app
from ...utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Set up template directory and Jinja environment
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def send_email(to_email: str, subject: str, content: str, is_html: bool = True) -> bool:
    """
    Sends an email to a recipient with given subject and content.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        content: Email body content (HTML or plain text)
        is_html: Whether content is HTML (True) or plain text (False)
    
    Returns:
        bool: Success status of the email sending operation
    """
    try:
        # Create a MIMEMultipart message
        message = MIMEMultipart()
        
        # Set the email sender, recipient, and subject
        message['From'] = settings.EMAIL_SENDER
        message['To'] = to_email
        message['Subject'] = subject
        
        # Attach the content as either plain text or HTML
        if is_html:
            message.attach(MIMEText(content, 'html'))
        else:
            message.attach(MIMEText(content, 'plain'))
        
        # Connect to the SMTP server using settings from config
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            # Start TLS if enabled
            if settings.SMTP_USE_TLS:
                server.starttls()
            
            # Login if credentials are provided
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            # Send the email
            server.send_message(message)
            
        logger.info(f"Email sent successfully to {to_email}", 
                   extra={"additional_data": {"subject": subject}})
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}", 
                    extra={"additional_data": {"subject": subject, "error": str(e)}})
        return False


def send_email_async(to_email: str, subject: str, content: str, is_html: bool = True) -> str:
    """
    Queues an email to be sent asynchronously via Celery.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        content: Email body content
        is_html: Whether content is HTML (True) or plain text (False)
    
    Returns:
        str: Celery task ID
    """
    # Queue the email sending as a Celery task
    task = celery_app.send_task(
        'tasks.notifications.send_email',
        args=[to_email, subject, content, is_html],
        queue='notifications'
    )
    
    logger.debug(f"Email queued for async delivery to {to_email}", 
                extra={"additional_data": {"subject": subject, "task_id": task.id}})
    
    return task.id


def render_template(template_name: str, context: Dict) -> str:
    """
    Renders an email template with provided context data.
    
    Args:
        template_name: Name of the template file
        context: Dictionary of variables to pass to the template
    
    Returns:
        str: Rendered HTML content
    """
    try:
        # Get the template by name from jinja_env
        template = jinja_env.get_template(template_name)
        
        # Render the template with the provided context
        rendered_content = template.render(**context)
        
        return rendered_content
    
    except Exception as e:
        logger.error(f"Failed to render template {template_name}: {str(e)}", 
                    extra={"additional_data": {"context": context, "error": str(e)}})
        # Return a simple error message that can be safely emailed
        return f"<p>Error rendering email template. Please contact support.</p>"


def send_rate_request_notification(recipient_email: str, firm_name: str, 
                                  request_id: str, additional_context: Optional[Dict] = None) -> bool:
    """
    Sends a notification about a rate request.
    
    Args:
        recipient_email: Email address of the recipient
        firm_name: Name of the law firm making the request
        request_id: Unique identifier for the rate request
        additional_context: Additional template variables
    
    Returns:
        bool: Success status of the email sending operation
    """
    try:
        # Prepare the context for the template
        context = {
            'firm_name': firm_name,
            'request_id': request_id,
            'app_url': settings.APP_URL,
        }
        
        # Add any additional context if provided
        if additional_context:
            context.update(additional_context)
        
        # Render the template
        content = render_template('rate_request.html', context)
        
        # Create a descriptive subject line
        subject = f"Rate Request from {firm_name}"
        
        # Send the email asynchronously
        send_email_async(recipient_email, subject, content)
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to send rate request notification: {str(e)}", 
                    extra={"additional_data": {"recipient": recipient_email, "firm": firm_name}})
        return False


def send_rate_submission_notification(recipient_email: str, firm_name: str, 
                                     submission_id: str, additional_context: Optional[Dict] = None) -> bool:
    """
    Sends a notification about a rate submission.
    
    Args:
        recipient_email: Email address of the recipient
        firm_name: Name of the law firm that submitted rates
        submission_id: Unique identifier for the rate submission
        additional_context: Additional template variables
    
    Returns:
        bool: Success status of the email sending operation
    """
    try:
        # Prepare the context for the template
        context = {
            'firm_name': firm_name,
            'submission_id': submission_id,
            'app_url': settings.APP_URL,
        }
        
        # Add any additional context if provided
        if additional_context:
            context.update(additional_context)
        
        # Render the template
        content = render_template('rate_submission.html', context)
        
        # Create a descriptive subject line
        subject = f"Rate Submission from {firm_name}"
        
        # Send the email asynchronously
        send_email_async(recipient_email, subject, content)
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to send rate submission notification: {str(e)}", 
                    extra={"additional_data": {"recipient": recipient_email, "firm": firm_name}})
        return False


def send_counter_proposal_notification(recipient_email: str, organization_name: str, 
                                      negotiation_id: str, additional_context: Optional[Dict] = None) -> bool:
    """
    Sends a notification about a counter-proposal.
    
    Args:
        recipient_email: Email address of the recipient
        organization_name: Name of the organization making the counter-proposal
        negotiation_id: Unique identifier for the negotiation
        additional_context: Additional template variables
    
    Returns:
        bool: Success status of the email sending operation
    """
    try:
        # Prepare the context for the template
        context = {
            'organization_name': organization_name,
            'negotiation_id': negotiation_id,
            'app_url': settings.APP_URL,
        }
        
        # Add any additional context if provided
        if additional_context:
            context.update(additional_context)
        
        # Render the template
        content = render_template('counter_proposal.html', context)
        
        # Create a descriptive subject line
        subject = f"Counter-Proposal from {organization_name}"
        
        # Send the email asynchronously
        send_email_async(recipient_email, subject, content)
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to send counter-proposal notification: {str(e)}", 
                    extra={"additional_data": {"recipient": recipient_email, "org": organization_name}})
        return False


def send_approval_notification(recipient_email: str, negotiation_id: str, 
                              requester_name: str, additional_context: Optional[Dict] = None) -> bool:
    """
    Sends a notification about an approval request.
    
    Args:
        recipient_email: Email address of the approver
        negotiation_id: Unique identifier for the negotiation
        requester_name: Name of the person requesting approval
        additional_context: Additional template variables
    
    Returns:
        bool: Success status of the email sending operation
    """
    try:
        # Prepare the context for the template
        context = {
            'requester_name': requester_name,
            'negotiation_id': negotiation_id,
            'app_url': settings.APP_URL,
        }
        
        # Add any additional context if provided
        if additional_context:
            context.update(additional_context)
        
        # Render the template
        content = render_template('approval_request.html', context)
        
        # Create a descriptive subject line
        subject = f"Approval Request from {requester_name}"
        
        # Send the email asynchronously
        send_email_async(recipient_email, subject, content)
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to send approval notification: {str(e)}", 
                    extra={"additional_data": {"recipient": recipient_email, "requester": requester_name}})
        return False


def send_message_notification(recipient_email: str, sender_name: str, 
                             message_subject: str, message_preview: str, thread_id: str) -> bool:
    """
    Sends a notification about a new message.
    
    Args:
        recipient_email: Email address of the recipient
        sender_name: Name of the message sender
        message_subject: Subject of the message
        message_preview: Preview of the message content
        thread_id: Unique identifier for the message thread
    
    Returns:
        bool: Success status of the email sending operation
    """
    try:
        # Prepare the context with sender_name, message_subject, message_preview, and thread_id
        context = {
            'sender_name': sender_name,
            'message_subject': message_subject,
            'message_preview': message_preview,
            'thread_id': thread_id,
            'app_url': settings.APP_URL,
        }
        
        # Render the template
        content = render_template('new_message.html', context)
        
        # Create a descriptive subject line
        subject = f"New Message: {message_subject}"
        
        # Send the email asynchronously
        send_email_async(recipient_email, subject, content)
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to send message notification: {str(e)}", 
                    extra={"additional_data": {"recipient": recipient_email, "sender": sender_name}})
        return False


def send_ocg_negotiation_notification(recipient_email: str, organization_name: str, 
                                     ocg_id: str, status: str, additional_context: Optional[Dict] = None) -> bool:
    """
    Sends a notification about OCG negotiation updates.
    
    Args:
        recipient_email: Email address of the recipient
        organization_name: Name of the organization updating the OCG
        ocg_id: Unique identifier for the OCG
        status: Current status of the OCG negotiation
        additional_context: Additional template variables
    
    Returns:
        bool: Success status of the email sending operation
    """
    try:
        # Prepare the context with organization_name, ocg_id, status and additional context
        context = {
            'organization_name': organization_name,
            'ocg_id': ocg_id,
            'status': status,
            'app_url': settings.APP_URL,
        }
        
        # Add any additional context if provided
        if additional_context:
            context.update(additional_context)
        
        # Render the template
        content = render_template('ocg_negotiation.html', context)
        
        # Create a descriptive subject line
        subject = f"OCG Negotiation Update: {status}"
        
        # Send the email asynchronously
        send_email_async(recipient_email, subject, content)
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to send OCG negotiation notification: {str(e)}", 
                    extra={"additional_data": {"recipient": recipient_email, "org": organization_name}})
        return False