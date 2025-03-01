"""
Celery configuration for the Justice Bid Rate Negotiation System.

This module initializes and configures the Celery application for asynchronous
task processing, including background jobs, scheduled tasks, and API integrations.
"""

import os
from celery import Celery
from kombu.utils.url import maybe_sanitize_url

from ..app.config import Config, AppConfig
from ..utils.logging import get_logger
from ..utils.redis_client import get_redis_connection_pool

# Initialize logger
logger = get_logger(__name__)

# Get configuration based on environment
config = AppConfig.get_config(os.getenv('FLASK_ENV', 'development'))

# Initialize Celery application
celery_app = Celery('justice_bid')

def configure_celery(app):
    """
    Configure Celery application with proper settings.

    Args:
        app (Celery): Celery application instance to configure

    Returns:
        Celery: Configured Celery application
    """
    # Set broker URL (Redis)
    app.conf.broker_url = config.REDIS_URL
    
    # Set result backend (Redis or MongoDB)
    # For MongoDB backend, use 'mongodb://' URL format
    if hasattr(config, 'MONGODB_URI') and config.MONGODB_URI.startswith('mongodb://'):
        app.conf.result_backend = 'mongodb'
        app.conf.mongodb_backend_settings = {
            'uri': config.MONGODB_URI,
            'database': 'celery_results'
        }
    else:
        app.conf.result_backend = config.REDIS_URL
    
    # Serialization settings
    app.conf.task_serializer = 'json'
    app.conf.result_serializer = 'json'
    app.conf.accept_content = ['json']
    
    # Time settings
    app.conf.timezone = 'UTC'
    app.conf.enable_utc = True
    
    # Task routes by type
    app.conf.task_routes = {
        'tasks.notifications.*': {'queue': 'notifications'},
        'tasks.imports.*': {'queue': 'imports'},
        'tasks.exports.*': {'queue': 'exports'},
        'tasks.analytics.*': {'queue': 'analytics'},
        'tasks.integration.*': {'queue': 'integration'},
    }
    
    # Configure task queues with priorities
    app.conf.task_queues = {
        'notifications': {'exchange': 'notifications', 'routing_key': 'notifications'},
        'imports': {'exchange': 'imports', 'routing_key': 'imports'},
        'exports': {'exchange': 'exports', 'routing_key': 'exports'},
        'analytics': {'exchange': 'analytics', 'routing_key': 'analytics'},
        'integration': {'exchange': 'integration', 'routing_key': 'integration'},
        'default': {'exchange': 'default', 'routing_key': 'default'},
    }
    
    # Set worker prefetch multiplier for optimal throughput
    app.conf.worker_prefetch_multiplier = 4
    
    # Configure default task settings
    app.conf.task_acks_late = True  # Tasks are acknowledged after execution
    app.conf.task_reject_on_worker_lost = True  # Reject tasks when worker dies
    app.conf.task_time_limit = 3600  # 1 hour time limit
    app.conf.task_soft_time_limit = 3000  # 50 minutes soft time limit
    
    # Default retry behavior
    app.conf.task_default_retry_delay = 60  # 1 minute retry delay
    app.conf.task_max_retries = 3  # Maximum 3 retries
    
    # Error email settings (if configured)
    if hasattr(config, 'CELERY_ERROR_EMAILS') and config.CELERY_ERROR_EMAILS:
        app.conf.task_send_sent_event = True
        app.conf.worker_send_task_events = True
        
    # Configure periodic tasks (Celery Beat) if needed
    if hasattr(config, 'CELERY_BEAT_SCHEDULE') and config.CELERY_BEAT_SCHEDULE:
        app.conf.beat_schedule = config.CELERY_BEAT_SCHEDULE
    
    # Log the configuration (sanitized)
    sanitized_broker = maybe_sanitize_url(app.conf.broker_url)
    sanitized_backend = maybe_sanitize_url(str(app.conf.result_backend))
    logger.info(f"Configured Celery with broker: {sanitized_broker}, backend: {sanitized_backend}")
    
    return app

# Configure Celery application
celery_app = configure_celery(celery_app)

def shared_task(name=None, bind=False, max_retries=3, default_retry_delay=60, 
                ignore_result=False, acks_late=True):
    """
    Decorator for registering shared tasks with reasonable defaults.
    
    Args:
        name (str, optional): Task name
        bind (bool, optional): Whether to pass self to the task
        max_retries (int, optional): Maximum number of retries
        default_retry_delay (int, optional): Default retry delay in seconds
        ignore_result (bool, optional): Whether to ignore the task result
        acks_late (bool, optional): Whether to acknowledge the task after execution
        
    Returns:
        callable: Decorated function that will be executed as a Celery task
    """
    def decorator(func):
        return celery_app.task(
            name=name or func.__name__,
            bind=bind,
            max_retries=max_retries,
            default_retry_delay=default_retry_delay,
            ignore_result=ignore_result,
            acks_late=acks_late
        )(func)
    return decorator

def init_celery(flask_app=None):
    """
    Initialize Celery with Flask application context if available.
    
    Args:
        flask_app: Flask application instance
        
    Returns:
        None
    """
    if flask_app:
        class ContextTask(celery_app.Task):
            def __call__(self, *args, **kwargs):
                with flask_app.app_context():
                    return self.run(*args, **kwargs)
                    
        celery_app.Task = ContextTask
        
        logger.info("Initialized Celery with Flask application context")