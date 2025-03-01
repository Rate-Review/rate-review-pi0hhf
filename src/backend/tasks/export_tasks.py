"""
Asynchronous tasks for exporting rate data to various destinations including files (Excel, CSV),
eBilling systems, and law firm billing systems. These tasks handle the potentially long-running
export operations in the background to ensure system responsiveness.
"""

import io  # standard library
import typing  # standard library
from datetime import datetime  # standard library

from celery import shared_task  # celery v5.3+ - Distributed task queue
from src.backend.integrations.ebilling.teamconnect import TeamConnectAdapter  # Internal import
from src.backend.integrations.file.excel_processor import ExcelProcessor  # Internal import
from src.backend.services.rates.export import RateExportService  # Internal import
from src.backend.utils.email import send_email  # Internal import
from src.backend.utils.logging import get_logger  # Internal import
from src.backend.utils.storage import save_file  # Internal import

# Initialize logger
logger = get_logger(__name__)

# Initialize RateExportService
rate_export_service = RateExportService()


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def export_rates_to_file_task(self, filters: dict, file_format: str, currency: str, user_id: str, email: str) -> dict:
    """Asynchronous task for exporting rates to a file format (Excel or CSV)

    Args:
        filters (dict): Filters to apply to the rate data
        file_format (str): File format for the export (excel or csv)
        currency (str): Currency for the exported rates
        user_id (str): User ID initiating the export
        email (str): Email address to send the export notification

    Returns:
        dict: Export result including file url and status
    """
    try:
        # Log the start of the export task
        logger.info(f"Starting export to file task for user {user_id} with format {file_format}")

        # Call rate_export_service.export_to_file with the provided parameters
        filename, file_content = rate_export_service.export_to_file(filters, file_format, currency)

        # If export is successful, save the file to storage
        file_url = save_file(filename, file_content)

        # If email is provided, send an email notification with the download link
        if email:
            subject = "Justice Bid Rate Export Complete"
            body = f"Your rate export is complete. You can download the file here: {file_url}"
            send_email(to_email=email, subject=subject, body=body)

        # Log the completion of the export task
        logger.info(f"Export to file task completed successfully for user {user_id}")

        # Return export result including status and file URL
        return {"status": "success", "file_url": file_url}

    except Exception as e:
        # Log errors and return failed status on unrecoverable errors
        logger.error(f"Export to file task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def export_rates_to_ebilling_task(self, client_id: str, ebilling_system: str, filters: dict, user_id: str, email: str) -> dict:
    """Asynchronous task for exporting rates to a client's eBilling system

    Args:
        client_id (str): Client ID for the eBilling system
        ebilling_system (str): eBilling system type (e.g., teamconnect)
        filters (dict): Filters to apply to the rate data
        user_id (str): User ID initiating the export
        email (str): Email address to send the export notification

    Returns:
        dict: Export result including success count, failure count, and errors
    """
    try:
        # Log the start of the eBilling export task
        logger.info(f"Starting eBilling export task for client {client_id} to {ebilling_system} for user {user_id}")

        # Call rate_export_service.export_to_ebilling with provided parameters
        export_result = rate_export_service.export_to_ebilling(client_id, ebilling_system, filters)

        # Process export results, tracking successes and failures
        success_count = export_result.get("success_count", 0)
        failure_count = export_result.get("failure_count", 0)
        errors = export_result.get("errors", [])

        # If email is provided, send a notification with export results
        if email:
            subject = f"Justice Bid eBilling Export to {ebilling_system} Complete"
            body = f"Export to {ebilling_system} complete. {success_count} rates exported successfully, {failure_count} failures."
            if errors:
                body += f"\nErrors:\n{chr(10).join(errors)}"
            send_email(to_email=email, subject=subject, body=body)

        # Log the completion of the export task
        logger.info(f"eBilling export task completed for client {client_id} to {ebilling_system} for user {user_id}")

        # Return export results with detailed statistics
        return {
            "status": "success",
            "success_count": success_count,
            "failure_count": failure_count,
            "errors": errors
        }

    except Exception as e:
        # Log errors and return failed status on unrecoverable errors
        logger.error(f"eBilling export task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def export_rates_to_lawfirm_task(self, firm_id: str, filters: dict, user_id: str, email: str) -> dict:
    """Asynchronous task for exporting rates to a law firm's billing system

    Args:
        firm_id (str): Law firm ID
        filters (dict): Filters to apply to the rate data
        user_id (str): User ID initiating the export
        email (str): Email address to send the export notification

    Returns:
        dict: Export result including success count, failure count, and errors
    """
    try:
        # Log the start of the law firm export task
        logger.info(f"Starting law firm export task for firm {firm_id} for user {user_id}")

        # Call rate_export_service.export_to_lawfirm with provided parameters
        export_result = rate_export_service.export_to_lawfirm(firm_id, filters)

        # Process export results, tracking successes and failures
        success_count = export_result.get("success_count", 0)
        failure_count = export_result.get("failure_count", 0)
        errors = export_result.get("errors", [])

        # If email is provided, send a notification with export results
        if email:
            subject = f"Justice Bid Law Firm Export Complete"
            body = f"Export to law firm system complete. {success_count} rates exported successfully, {failure_count} failures."
            if errors:
                body += f"\nErrors:\n{chr(10).join(errors)}"
            send_email(to_email=email, subject=subject, body=body)

        # Log the completion of the export task
        logger.info(f"Law firm export task completed for firm {firm_id} for user {user_id}")

        # Return export results with detailed statistics
        return {
            "status": "success",
            "success_count": success_count,
            "failure_count": failure_count,
            "errors": errors
        }

    except Exception as e:
        # Log errors and return failed status on unrecoverable errors
        logger.error(f"Law firm export task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def export_rates_by_negotiation_task(self, negotiation_id: str, format: str, destination_type: str, destination_id: str, user_id: str, email: str) -> dict:
    """Asynchronous task for exporting rates from a specific negotiation to a destination

    Args:
        negotiation_id (str): Negotiation ID
        format (str): Export format (e.g., excel, csv)
        destination_type (str): Destination type (e.g., file, ebilling, lawfirm)
        destination_id (str): Destination ID (e.g., file path, eBilling system ID)
        user_id (str): User ID initiating the export
        email (str): Email address to send the export notification

    Returns:
        dict: Export result including status and details
    """
    try:
        # Log the start of the negotiation export task
        logger.info(f"Starting negotiation export task for negotiation {negotiation_id} to {destination_type} for user {user_id}")

        # Call rate_export_service.export_by_negotiation with provided parameters
        export_result = rate_export_service.export_by_negotiation(negotiation_id, format, destination_type, destination_id)

        # Process result based on destination type (file, eBilling, law firm)
        if destination_type == "file" and export_result.get("success"):
            # If destination is file and export is successful, save the file and generate download URL
            file_url = save_file(export_result["filename"], export_result["file_content"])
            export_result["file_url"] = file_url

        # If email is provided, send a notification with export results
        if email:
            subject = f"Justice Bid Negotiation Export Complete"
            body = f"Export of negotiation {negotiation_id} complete. Status: {export_result.get('status')}"
            if "file_url" in export_result:
                body += f"\nDownload file: {export_result['file_url']}"
            send_email(to_email=email, subject=subject, body=body)

        # Log the completion of the export task
        logger.info(f"Negotiation export task completed for negotiation {negotiation_id} to {destination_type} for user {user_id}")

        # Return export results with appropriate details
        return export_result

    except Exception as e:
        # Log errors and return failed status on unrecoverable errors
        logger.error(f"Negotiation export task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def bulk_export_rates_task(self, export_configs: list, filters: dict, user_id: str, email: str) -> dict:
    """Asynchronous task for exporting rates to multiple destinations in bulk

    Args:
        export_configs (list): List of export configurations, each specifying format and destination
        filters (dict): Filters to apply to the rate data
        user_id (str): User ID initiating the export
        email (str): Email address to send the export notification

    Returns:
        dict: Bulk export results including status for each destination
    """
    try:
        # Log the start of the bulk export task
        logger.info(f"Starting bulk export task for user {user_id} with {len(export_configs)} destinations")

        # Initialize results dictionary to track each export result
        results = {}

        # Iterate through export_configs and call appropriate export task for each
        for config in export_configs:
            destination_type = config["destination_type"]
            destination_id = config["destination_id"]
            format = config["format"]
            task_id = f"{destination_type}_{destination_id}_{format}"

            try:
                # Call appropriate export task based on destination_type
                if destination_type == "file":
                    results[task_id] = export_rates_to_file_task.delay(filters, format, "USD", user_id, None).get()  # No email for individual file exports
                elif destination_type == "ebilling":
                    results[task_id] = export_rates_to_ebilling_task.delay(destination_id, format, filters, user_id, None).get()  # No email for individual eBilling exports
                elif destination_type == "lawfirm":
                    results[task_id] = export_rates_to_lawfirm_task.delay(destination_id, filters, user_id, None).get()  # No email for individual law firm exports
                else:
                    results[task_id] = {"status": "failed", "error": f"Invalid destination type: {destination_type}"}

            except Exception as e:
                results[task_id] = {"status": "failed", "error": str(e)}

        # If email is provided, send a consolidated notification with all export results
        if email:
            subject = "Justice Bid Bulk Rate Export Complete"
            body = "Bulk rate export complete. Results:\n"
            for task_id, result in results.items():
                body += f"{task_id}: {result.get('status')}\n"
                if "error" in result:
                    body += f"Error: {result['error']}\n"
            send_email(to_email=email, subject=subject, body=body)

        # Log the completion of the bulk export task
        logger.info(f"Bulk export task completed for user {user_id}")

        # Return consolidated results of all exports
        return results

    except Exception as e:
        # Log errors for failed exports
        logger.error(f"Bulk export task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True)
def scheduled_export_rates_task(self) -> dict:
    """Scheduled task for automatically exporting rates based on configured schedules

    Returns:
        dict: Results of all scheduled exports
    """
    try:
        # Log the start of the scheduled export task
        logger.info("Starting scheduled export task")

        # Retrieve all scheduled export configurations
        # TODO: Implement retrieval of scheduled export configurations from database or config file
        export_configs = []  # Placeholder for scheduled export configurations

        # Initialize results dictionary to track each export result
        results = {}

        # For each configuration, check if it's due to run based on schedule
        for config in export_configs:
            if config["is_due"]:
                destination_type = config["destination_type"]
                destination_id = config["destination_id"]
                format = config["format"]
                filters = config["filters"]
                user_id = config["user_id"]
                email = config["email"]
                task_id = f"{destination_type}_{destination_id}_{format}"

                try:
                    # Execute due exports by calling appropriate export tasks
                    if destination_type == "file":
                        results[task_id] = export_rates_to_file_task.delay(filters, format, "USD", user_id, email).get()
                    elif destination_type == "ebilling":
                        results[task_id] = export_rates_to_ebilling_task.delay(destination_id, format, filters, user_id, email).get()
                    elif destination_type == "lawfirm":
                        results[task_id] = export_rates_to_lawfirm_task.delay(destination_id, filters, user_id, email).get()
                    else:
                        results[task_id] = {"status": "failed", "error": f"Invalid destination type: {destination_type}"}

                except Exception as e:
                    results[task_id] = {"status": "failed", "error": str(e)}

        # Send notification to configured recipients
        # TODO: Implement notification logic

        # Log the completion of the scheduled export task
        logger.info("Scheduled export task completed")

        # Return results of all exports executed
        return results

    except Exception as e:
        # Log errors for failed exports
        logger.error(f"Scheduled export task failed: {str(e)}", exc_info=True)
        return {"status": "failed", "error": str(e)}