"""
Email utilities for the Justice Bid Rate Negotiation System.

This module provides functionality for sending emails, including template rendering,
SMTP configuration, and retry capabilities. It serves as the foundation for all 
email communications in the application.
"""

import os
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable

import jinja2
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .logging import get_logger
from ..config import AppConfig

# Initialize logger
logger = get_logger(__name__)

# Default email settings
DEFAULT_SENDER = '"Justice Bid <no-reply@justicebid.com>"'
DEFAULT_TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"


def init_email_config(config: Optional[Dict] = None) -> Dict:
    """
    Initialize email configuration from app config or environment variables.
    
    Args:
        config: Optional configuration dictionary to use instead of app config
        
    Returns:
        Dict: Email configuration dictionary
    """
    if not config:
        # Get configuration from AppConfig
        config = AppConfig.get_instance()
    
    # Extract email settings
    smtp_host = os.environ.get('SMTP_HOST', config.get('SMTP_HOST', 'localhost'))
    smtp_port = int(os.environ.get('SMTP_PORT', config.get('SMTP_PORT', 25)))
    smtp_username = os.environ.get('SMTP_USERNAME', config.get('SMTP_USERNAME', ''))
    smtp_password = os.environ.get('SMTP_PASSWORD', config.get('SMTP_PASSWORD', ''))
    use_tls = os.environ.get('SMTP_USE_TLS', config.get('SMTP_USE_TLS', False))
    use_ssl = os.environ.get('SMTP_USE_SSL', config.get('SMTP_USE_SSL', False))
    
    # Convert string values to boolean if needed
    if isinstance(use_tls, str):
        use_tls = use_tls.lower() in ('true', 'yes', '1', 't', 'y')
    if isinstance(use_ssl, str):
        use_ssl = use_ssl.lower() in ('true', 'yes', '1', 't', 'y')
    
    # Set default sender from config or use default
    default_sender = os.environ.get('DEFAULT_EMAIL_SENDER', 
                                  config.get('DEFAULT_EMAIL_SENDER', DEFAULT_SENDER))
    
    # Get templates directory
    templates_dir = os.environ.get('EMAIL_TEMPLATES_DIR',
                                 config.get('EMAIL_TEMPLATES_DIR', str(DEFAULT_TEMPLATES_DIR)))
    
    # Create configuration dictionary
    email_config = {
        'smtp_host': smtp_host,
        'smtp_port': smtp_port,
        'smtp_username': smtp_username,
        'smtp_password': smtp_password,
        'use_tls': use_tls,
        'use_ssl': use_ssl,
        'default_sender': default_sender,
        'templates_dir': Path(templates_dir),
        'max_retries': int(os.environ.get('EMAIL_MAX_RETRIES', config.get('EMAIL_MAX_RETRIES', 3))),
        'retry_delay': float(os.environ.get('EMAIL_RETRY_DELAY', config.get('EMAIL_RETRY_DELAY', 1.0))),
        'retry_backoff': float(os.environ.get('EMAIL_RETRY_BACKOFF', config.get('EMAIL_RETRY_BACKOFF', 2.0)))
    }
    
    logger.info("Email configuration initialized", 
               extra={"additional_data": {k: v for k, v in email_config.items() 
                                       if k not in ['smtp_password']}})
    
    return email_config


def send_email(
    to_email: Union[str, List[str]],
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    html: bool = False,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[Dict]] = None,
    headers: Optional[Dict[str, str]] = None
) -> bool:
    """
    Send an email with the specified parameters.
    
    Args:
        to_email: Recipient email address(es)
        subject: Email subject
        body: Email body content
        from_email: Sender email address (defaults to configured default)
        html: Whether the body content is HTML
        cc: Carbon copy recipients
        bcc: Blind carbon copy recipients
        attachments: List of attachment dictionaries with 'content' and 'filename' keys
        headers: Additional email headers
        
    Returns:
        bool: Success status of the email sending operation
    """
    config = init_email_config()
    
    # Ensure to_email is a list
    if isinstance(to_email, str):
        to_email = [to_email]
    
    # Default values for optional parameters
    from_email = from_email or config['default_sender']
    cc = cc or []
    bcc = bcc or []
    attachments = attachments or []
    headers = headers or {}
    
    try:
        # Create message object
        message = MIMEMultipart() if attachments or html else MIMEText(body, 'html' if html else 'plain')
        
        # Set headers
        message['From'] = from_email
        message['To'] = ', '.join(to_email)
        message['Subject'] = subject
        
        if cc:
            message['Cc'] = ', '.join(cc)
        
        # Add custom headers
        for header_name, header_value in headers.items():
            message[header_name] = header_value
        
        # Add body if using MIMEMultipart
        if isinstance(message, MIMEMultipart):
            content_type = 'html' if html else 'plain'
            message.attach(MIMEText(body, content_type))
        
        # Add attachments
        for attachment in attachments:
            part = MIMEApplication(attachment['content'])
            part.add_header('Content-Disposition', 'attachment', filename=attachment['filename'])
            message.attach(part)
        
        # Determine all recipients
        all_recipients = to_email + cc + bcc
        
        # Connect to SMTP server
        context = ssl.create_default_context()
        
        if config['use_ssl']:
            smtp = smtplib.SMTP_SSL(config['smtp_host'], config['smtp_port'], context=context)
        else:
            smtp = smtplib.SMTP(config['smtp_host'], config['smtp_port'])
            
            if config['use_tls']:
                smtp.starttls(context=context)
        
        # Login if credentials provided
        if config['smtp_username'] and config['smtp_password']:
            smtp.login(config['smtp_username'], config['smtp_password'])
        
        # Send email
        smtp.sendmail(from_email, all_recipients, message.as_string())
        smtp.quit()
        
        logger.info(f"Email sent successfully to {', '.join(to_email)}",
                   extra={"additional_data": {
                       "subject": subject,
                       "recipients": to_email,
                       "cc": cc,
                       "bcc": bcc
                   }})
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}",
                    extra={"additional_data": {
                        "subject": subject,
                        "recipients": to_email,
                        "error": str(e)
                    }})
        return False


def send_template_email(
    to_email: Union[str, List[str]],
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    from_email: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[Dict]] = None,
    headers: Optional[Dict[str, str]] = None
) -> bool:
    """
    Send an email using a Jinja2 template.
    
    Args:
        to_email: Recipient email address(es)
        subject: Email subject
        template_name: Name of the template file
        context: Context data for template rendering
        from_email: Sender email address (defaults to configured default)
        cc: Carbon copy recipients
        bcc: Blind carbon copy recipients
        attachments: List of attachment dictionaries with 'content' and 'filename' keys
        headers: Additional email headers
        
    Returns:
        bool: Success status of the email sending operation
    """
    config = init_email_config()
    
    # Create template instance
    email_template = EmailTemplate(config['templates_dir'])
    
    try:
        # Render template with context
        content = email_template.render_template(template_name, context)
        
        # Send the email with rendered content
        return send_email(
            to_email=to_email,
            subject=subject,
            body=content,
            from_email=from_email,
            html=True,  # Template emails are HTML by default
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            headers=headers
        )
    
    except Exception as e:
        logger.error(f"Failed to send template email: {str(e)}",
                    extra={"additional_data": {
                        "subject": subject,
                        "template": template_name,
                        "error": str(e)
                    }})
        return False


class EmailTemplate:
    """
    Manages email templates using Jinja2 template engine.
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize the email template manager.
        
        Args:
            templates_dir: Directory containing email templates
        """
        self.templates_dir = templates_dir or DEFAULT_TEMPLATES_DIR
        
        # Initialize template environment
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Template cache
        self._template_cache = {}
    
    def get_template(self, template_name: str) -> jinja2.Template:
        """
        Get a template by name, loading from file or cache.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            jinja2.Template: Loaded Jinja2 template
        """
        # Add .html extension if not provided
        if not template_name.endswith('.html'):
            template_name += '.html'
        
        # Check cache first
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        try:
            # Load template
            template = self._env.get_template(template_name)
            
            # Cache template
            self._template_cache[template_name] = template
            
            return template
        
        except jinja2.exceptions.TemplateNotFound:
            logger.error(f"Email template not found: {template_name}",
                        extra={"additional_data": {
                            "template_name": template_name,
                            "templates_dir": str(self.templates_dir)
                        }})
            raise ValueError(f"Email template not found: {template_name}")
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template file
            context: Context data for template rendering
            
        Returns:
            str: Rendered template content
        """
        template = self.get_template(template_name)
        return template.render(**context)
    
    def clear_cache(self) -> None:
        """
        Clear the template cache.
        """
        self._template_cache = {}


class EmailRetry:
    """
    Handles retries for email sending operations.
    """
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """
        Initialize the retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries in seconds
            backoff: Backoff multiplier for exponential backoff
        """
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
    
    def should_retry(self, exception: Exception) -> bool:
        """
        Determine if a failed operation should be retried.
        
        Args:
            exception: The exception that occurred
            
        Returns:
            bool: True if should retry, False otherwise
        """
        # Retry on network-related errors and server errors
        if isinstance(exception, (
            smtplib.SMTPServerDisconnected,
            smtplib.SMTPConnectError,
            smtplib.SMTPHeloError,
            smtplib.SMTPException,
            ConnectionError,
            TimeoutError
        )):
            return True
        
        # Don't retry on authentication errors or other client errors
        return False
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute with retry
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            
        Returns:
            Any: Return value from the function
        """
        # Configure retry decorator
        retry_decorator = retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=self.delay, max=self.delay * (self.backoff ** (self.max_retries - 1))),
            retry=retry_if_exception_type(
                (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, ConnectionError, TimeoutError)
            ),
            reraise=True
        )
        
        # Apply decorator to function
        wrapped_func = retry_decorator(func)
        
        # Execute with retry
        try:
            return wrapped_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Operation failed after {self.max_retries} retries: {str(e)}",
                        extra={"additional_data": {
                            "function": func.__name__,
                            "max_retries": self.max_retries,
                            "error": str(e)
                        }})
            raise


class SMTPEmailSender:
    """
    SMTP implementation for sending emails.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize SMTP email sender with configuration.
        
        Args:
            config: Email configuration dictionary
        """
        self.config = config or init_email_config()
        
        # Initialize retry handler
        self.retry_handler = EmailRetry(
            max_retries=self.config.get('max_retries', 3),
            delay=self.config.get('retry_delay', 1.0),
            backoff=self.config.get('retry_backoff', 2.0)
        )
    
    def send(self, 
            to_emails: List[str],
            subject: str,
            body: str,
            from_email: Optional[str] = None,
            html: bool = False,
            cc: Optional[List[str]] = None,
            bcc: Optional[List[str]] = None,
            attachments: Optional[List[Dict]] = None,
            headers: Optional[Dict[str, str]] = None) -> bool:
        """
        Send an email with retry capability.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Email body content
            from_email: Sender email address
            html: Whether the body content is HTML
            cc: Carbon copy recipients
            bcc: Blind carbon copy recipients
            attachments: List of attachment dictionaries
            headers: Additional email headers
            
        Returns:
            bool: Success status of the email sending operation
        """
        try:
            return self.retry_handler.retry(
                send_email,
                to_email=to_emails,
                subject=subject,
                body=body,
                from_email=from_email or self.config['default_sender'],
                html=html,
                cc=cc,
                bcc=bcc,
                attachments=attachments,
                headers=headers
            )
        except Exception as e:
            logger.error(f"Failed to send email after retries: {str(e)}",
                        extra={"additional_data": {
                            "subject": subject,
                            "recipients": to_emails,
                            "error": str(e)
                        }})
            return False
    
    def send_template(self,
                     to_emails: List[str],
                     subject: str,
                     template_name: str,
                     context: Dict[str, Any],
                     from_email: Optional[str] = None,
                     cc: Optional[List[str]] = None,
                     bcc: Optional[List[str]] = None,
                     attachments: Optional[List[Dict]] = None,
                     headers: Optional[Dict[str, str]] = None) -> bool:
        """
        Send a template email with retry capability.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            template_name: Name of the template file
            context: Context data for template rendering
            from_email: Sender email address
            cc: Carbon copy recipients
            bcc: Blind carbon copy recipients
            attachments: List of attachment dictionaries
            headers: Additional email headers
            
        Returns:
            bool: Success status of the email sending operation
        """
        try:
            return self.retry_handler.retry(
                send_template_email,
                to_email=to_emails,
                subject=subject,
                template_name=template_name,
                context=context,
                from_email=from_email or self.config['default_sender'],
                cc=cc,
                bcc=bcc,
                attachments=attachments,
                headers=headers
            )
        except Exception as e:
            logger.error(f"Failed to send template email after retries: {str(e)}",
                        extra={"additional_data": {
                            "subject": subject,
                            "template": template_name,
                            "recipients": to_emails,
                            "error": str(e)
                        }})
            return False