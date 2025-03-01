"""
Task queue module initialization file that imports and registers all asynchronous tasks with Celery for the Justice Bid Rate Negotiation System.
"""

from .celery_app import celery_app  # Import the Celery application instance for task registration
from .email_tasks import email_tasks  # Import email task module to register tasks with Celery
from .notification_tasks import notification_tasks  # Import notification task module to register tasks with Celery
from .import_tasks import import_tasks  # Import data import task module to register tasks with Celery
from .export_tasks import export_tasks  # Import data export task module to register tasks with Celery
from .data_cleanup_tasks import data_cleanup_tasks  # Import data cleanup task module to register tasks with Celery
from .integration_sync_tasks import integration_sync_tasks  # Import integration synchronization task module to register tasks with Celery
from .analytics_tasks import analytics_tasks  # Import analytics task module to register tasks with Celery
from .scheduled_tasks import scheduled_tasks  # Import scheduled task module to register tasks with Celery

__all__ = ['celery_app']