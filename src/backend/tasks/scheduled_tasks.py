"""
Configures and manages scheduled background tasks for the Justice Bid Rate Negotiation System, including data synchronization, analytics updates, cleanup operations, and periodic notifications. Serves as the central orchestration point for all time-based operations that maintain system data freshness and integrity.
"""

import datetime  # standard library
from typing import List, Dict  # standard library

import celery  # celery 5.3+
from celery import schedules  # celery 5.3+

from .celery_app import celery_app  # Internal import: Celery application instance for scheduling periodic tasks
from .integration_sync_tasks import sync_all_ebilling_systems, sync_all_lawfirm_systems, sync_all_unicourt_data  # Internal import: Tasks for synchronizing data with external systems
from .analytics_tasks import refresh_analytics_cache, schedule_recurring_analytics  # Internal import: Tasks for refreshing cached analytics data
from .data_cleanup_tasks import archive_expired_active_data, purge_expired_archived_data, anonymize_personal_data, verify_archived_data_integrity, cleanup_temporary_files, cleanup_expired_sessions  # Internal import: Tasks for data cleanup operations
from .notification_tasks import process_notification_queue, clean_old_notifications  # Internal import: Tasks for processing the notification queue
from ..integrations.currency.exchange_rate_api import update_exchange_rates  # Internal import: Module for updating currency exchange rates
from ..utils.logging import get_logger  # Internal import: Logging utility for scheduled tasks
from ..app.config import Config  # Internal import: Configuration settings for scheduled tasks

# Initialize logger
logger = get_logger(__name__)

@celery_app.task
def update_currency_exchange_rates() -> dict:
    """
    Celery task that updates currency exchange rates from external providers
    """
    logger.info("Starting currency exchange rate update task")
    try:
        # Call the exchange_rate_api.update_exchange_rates function
        update_status = update_exchange_rates()

        # Log successful updates or errors encountered
        if update_status["success_count"] > 0:
            logger.info(f"Successfully updated {update_status['success_count']} exchange rates")
        if update_status["error_count"] > 0:
            logger.error(f"Encountered {update_status['error_count']} errors during exchange rate update")

        # Return a dictionary with update status and counts
        return update_status
    except Exception as e:
        logger.error(f"Error updating currency exchange rates: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def sync_external_systems() -> dict:
    """
    Celery task that orchestrates synchronization with all external systems
    """
    logger.info("Starting external systems synchronization task")
    try:
        # Call sync_all_ebilling_systems.delay() with appropriate options
        ebilling_task = sync_all_ebilling_systems.delay(sync_options={"import_rates": True, "import_billing": True, "export_rates": True})

        # Call sync_all_lawfirm_systems.delay() with appropriate options
        lawfirm_task = sync_all_lawfirm_systems.delay(sync_options={"import_attorneys": True, "import_rates": True, "export_rates": True})

        # Call sync_all_unicourt_data.delay() with appropriate options
        unicourt_task = sync_all_unicourt_data.delay(all_attorneys=True)

        # Return a dictionary with references to the scheduled tasks
        return {
            "ebilling_task_id": str(ebilling_task.id),
            "lawfirm_task_id": str(lawfirm_task.id),
            "unicourt_task_id": str(unicourt_task.id),
        }
    except Exception as e:
        logger.error(f"Error synchronizing external systems: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def refresh_analytics() -> dict:
    """
    Celery task that refreshes analytics data and caches
    """
    logger.info("Starting analytics refresh task")
    try:
        # Call refresh_analytics_cache.delay() for commonly accessed analytics
        cache_task = refresh_analytics_cache.delay()

        # Call schedule_recurring_analytics.delay() to update all organization analytics
        recurring_task = schedule_recurring_analytics.delay()

        # Return a dictionary with references to the scheduled tasks
        return {
            "cache_task_id": str(cache_task.id),
            "recurring_task_id": str(recurring_task.id),
        }
    except Exception as e:
        logger.error(f"Error refreshing analytics: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def run_data_maintenance() -> dict:
    """
    Celery task that performs regular data maintenance operations including archiving, purging, and integrity checks
    """
    logger.info("Starting data maintenance task")
    try:
        data_types = ["rates", "billing", "messages", "negotiations"]
        task_ids = {}

        # For each data type:
        for data_type in data_types:
            # Call archive_expired_active_data.delay(data_type)
            archive_task = archive_expired_active_data.delay(data_type)
            task_ids[f"{data_type}_archive"] = str(archive_task.id)

            # Call purge_expired_archived_data.delay(data_type)
            purge_task = purge_expired_archived_data.delay(data_type)
            task_ids[f"{data_type}_purge"] = str(purge_task.id)

            # Call anonymize_personal_data.delay(data_type, False)
            anonymize_task = anonymize_personal_data.delay(data_type, False)
            task_ids[f"{data_type}_anonymize"] = str(anonymize_task.id)

            # Call verify_archived_data_integrity.delay(data_type)
            verify_task = verify_archived_data_integrity.delay(data_type)
            task_ids[f"{data_type}_verify"] = str(verify_task.id)

        # Call cleanup_temporary_files.delay()
        cleanup_files_task = cleanup_temporary_files.delay()
        task_ids["cleanup_files"] = str(cleanup_files_task.id)

        # Call cleanup_expired_sessions.delay()
        cleanup_sessions_task = cleanup_expired_sessions.delay()
        task_ids["cleanup_sessions"] = str(cleanup_sessions_task.id)

        # Return a dictionary with references to all scheduled tasks
        return task_ids
    except Exception as e:
        logger.error(f"Error running data maintenance: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def process_notifications() -> dict:
    """
    Celery task that processes queued notifications
    """
    logger.info("Starting notification processing task")
    try:
        # Call process_notification_queue.delay() with appropriate batch size
        queue_task = process_notification_queue.delay(batch_size=100)

        # Call clean_old_notifications.delay() with retention period
        cleanup_task = clean_old_notifications.delay(days_to_keep=30)

        # Return a dictionary with references to the scheduled tasks
        return {
            "queue_task_id": str(queue_task.id),
            "cleanup_task_id": str(cleanup_task.id),
        }
    except Exception as e:
        logger.error(f"Error processing notifications: {str(e)}")
        return {"status": "error", "message": str(e)}