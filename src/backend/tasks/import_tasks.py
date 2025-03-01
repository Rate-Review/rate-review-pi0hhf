"""
Celery tasks for importing data from various sources into the Justice Bid system,
including eBilling systems, law firm systems, UniCourt, and file uploads.
"""

import os  # File path handling and environment variables
import tempfile  # Create temporary files for import processing
import typing  # Type hints for function parameters and returns
from datetime import datetime  # Date and time handling for import logs and timestamps
import json  # JSON parsing and serialization
from dataclasses import dataclass  # Data class decorators for import data structures

from celery import shared_task  # Access Celery application and task decorators for defining async tasks # Version: 
from src.backend.integrations.file.csv_processor import CSVProcessor  # Process and validate CSV file imports
from src.backend.integrations.file.excel_processor import ExcelProcessor  # Process and validate Excel file imports
from src.backend.integrations.ebilling.onit import OnitClient  # Interact with Onit eBilling system API
from src.backend.integrations.ebilling.teamconnect import TeamConnectClient  # Interact with TeamConnect eBilling system API
from src.backend.integrations.ebilling.legal_tracker import LegalTrackerClient  # Interact with Legal Tracker eBilling system API
from src.backend.integrations.unicourt.client import UniCourtClient  # Retrieve attorney performance data from UniCourt API
from src.backend.integrations.lawfirm.client import LawFirmClient  # Retrieve data from law firm billing systems
from src.backend.utils.logging import logger  # Log import task events and errors
from src.backend.db.repositories.attorney_repository import AttorneyRepository  # Store and retrieve attorney data
from src.backend.db.repositories.rate_repository import RateRepository  # Store and retrieve rate data
from src.backend.db.repositories.billing_repository import BillingRepository  # Store and retrieve billing history data
from src.backend.db.repositories.organization_repository import OrganizationRepository  # Retrieve organization data for imports
from src.backend.services.rates.validation import validate_rate_data  # 
from src.backend.utils.storage import storage_client  # Handle file storage for imports
from src.backend.services.messaging.notifications import send_notification  # 
from src.backend.integrations.common.mapper import DataMapper  # Map imported data to internal models

EBILLING_SYSTEM_CLIENTS = {
    "onit": OnitClient,
    "teamconnect": TeamConnectClient,
    "legal_tracker": LegalTrackerClient
}

IMPORT_STATUS = {
    "PENDING": "pending",
    "PROCESSING": "processing",
    "COMPLETED": "completed",
    "FAILED": "failed"
}


@shared_task(bind=True, max_retries=3)
def import_ebilling_data(self, organization_id: str, ebilling_system: str, credentials: dict,
                         data_types: list, filters: dict, user_id: str) -> dict:
    """Import data from an eBilling system including rates and billing history"""
    logger.info(f"Starting eBilling data import for organization {organization_id} from {ebilling_system}")
    try:
        if ebilling_system not in EBILLING_SYSTEM_CLIENTS:
            raise ValueError(f"Unsupported eBilling system: {ebilling_system}")

        organization_repo = OrganizationRepository()
        organization = organization_repo.get_by_id(organization_id)
        if not organization:
            raise ValueError(f"Organization with ID {organization_id} not found")

        ebilling_client = EBILLING_SYSTEM_CLIENTS[ebilling_system](credentials)

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_messages = []

        for data_type in data_types:
            try:
                data = ebilling_client.get_data(data_type, filters)
                for record in data:
                    try:
                        # Map the data to internal models
                        data_mapper = DataMapper()  # Assuming a generic DataMapper
                        internal_record = data_mapper.map_to_model(record)

                        # Validate the data using appropriate validation functions
                        if data_type == "rates":
                            validate_rate_data(internal_record)

                        # Store the data using the appropriate repository
                        if data_type == "rates":
                            rate_repo = RateRepository()
                            existing_rate = rate_repo.get_by_attorney_and_client(
                                internal_record["attorney_id"], internal_record["client_id"])
                            if existing_rate:
                                rate_repo.update(existing_rate.id, internal_record)
                                updated_count += 1
                            else:
                                rate_repo.create(internal_record)
                                created_count += 1
                    except Exception as e:
                        skipped_count += 1
                        error_messages.append(f"Error processing record: {str(e)}")
            except Exception as e:
                error_messages.append(f"Error retrieving {data_type} data: {str(e)}")

        results = {
            "status": IMPORT_STATUS["COMPLETED"],
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": error_messages
        }
        logger.info(f"eBilling data import completed for organization {organization_id} with results: {results}")
        send_notification(user_id, "ebilling_import_complete", "eBilling Import Complete",
                          f"Imported {created_count} new and updated {updated_count} records.",
                          {"results": results}, ["email"], False, "/rates")
        return results
    except Exception as e:
        logger.error(f"eBilling data import failed for organization {organization_id}: {str(e)}")
        send_notification(user_id, "ebilling_import_failed", "eBilling Import Failed",
                          f"eBilling import failed: {str(e)}", {"error": str(e)}, ["email"], True, "/rates")
        return {"status": IMPORT_STATUS["FAILED"], "error": str(e)}


@shared_task(bind=True, max_retries=3)
def import_law_firm_data(self, organization_id: str, credentials: dict, data_types: list,
                         filters: dict, user_id: str) -> dict:
    """Import attorney and rate data from a law firm billing system"""
    logger.info(f"Starting law firm data import for organization {organization_id}")
    try:
        organization_repo = OrganizationRepository()
        organization = organization_repo.get_by_id(organization_id)
        if not organization:
            raise ValueError(f"Organization with ID {organization_id} not found")

        law_firm_client = LawFirmClient(credentials)

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_messages = []

        for data_type in data_types:
            try:
                data = law_firm_client.get_data(data_type, filters)
                for record in data:
                    try:
                        # Map the data to internal models
                        data_mapper = DataMapper()  # Assuming a generic DataMapper
                        internal_record = data_mapper.map_to_model(record)

                        # Validate the data using appropriate validation functions
                        if data_type == "attorneys":
                            # validate_attorney_data(internal_record)
                            pass  # TODO: Implement attorney validation

                        # Store the data using the appropriate repository
                        if data_type == "attorneys":
                            attorney_repo = AttorneyRepository()
                            existing_attorney = attorney_repo.get_by_timekeeper_id(
                                internal_record["timekeeper_id"])
                            if existing_attorney:
                                attorney_repo.update(existing_attorney.id, internal_record)
                                updated_count += 1
                            else:
                                attorney_repo.create(internal_record)
                                created_count += 1
                    except Exception as e:
                        skipped_count += 1
                        error_messages.append(f"Error processing record: {str(e)}")
            except Exception as e:
                error_messages.append(f"Error retrieving {data_type} data: {str(e)}")

        results = {
            "status": IMPORT_STATUS["COMPLETED"],
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": error_messages
        }
        logger.info(f"Law firm data import completed for organization {organization_id} with results: {results}")
        send_notification(user_id, "law_firm_import_complete", "Law Firm Import Complete",
                          f"Imported {created_count} new and updated {updated_count} records.",
                          {"results": results}, ["email"], False, "/attorneys")
        return results
    except Exception as e:
        logger.error(f"Law firm data import failed for organization {organization_id}: {str(e)}")
        send_notification(user_id, "law_firm_import_failed", "Law Firm Import Failed",
                          f"Law firm import failed: {str(e)}", {"error": str(e)}, ["email"], True, "/attorneys")
        return {"status": IMPORT_STATUS["FAILED"], "error": str(e)}


@shared_task(bind=True, max_retries=3)
def import_unicourt_data(self, attorney_ids: list, organization_id: str, user_id: str) -> dict:
    """Import attorney performance data from UniCourt API"""
    logger.info(f"Starting UniCourt data import for organization {organization_id} and attorneys {attorney_ids}")
    try:
        organization_repo = OrganizationRepository()
        organization = organization_repo.get_by_id(organization_id)
        if not organization:
            raise ValueError(f"Organization with ID {organization_id} not found")

        unicourt_client = UniCourtClient()

        updated_count = 0
        skipped_count = 0
        error_messages = []

        for attorney_id in attorney_ids:
            try:
                # Retrieve performance data from UniCourt API
                performance_data = unicourt_client.get_performance_metrics(attorney_id)

                # Map the data to internal attorney model's performance_data field
                attorney_repo = AttorneyRepository()
                attorney = attorney_repo.get_by_id(attorney_id)
                if attorney:
                    attorney.performance_data = performance_data
                    attorney_repo.update(attorney.id, attorney.performance_data)
                    updated_count += 1
                else:
                    skipped_count += 1
                    error_messages.append(f"Attorney with ID {attorney_id} not found")
            except Exception as e:
                skipped_count += 1
                error_messages.append(f"Error processing attorney {attorney_id}: {str(e)}")

        results = {
            "status": IMPORT_STATUS["COMPLETED"],
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": error_messages
        }
        logger.info(f"UniCourt data import completed for organization {organization_id} with results: {results}")
        send_notification(user_id, "unicourt_import_complete", "UniCourt Import Complete",
                          f"Imported UniCourt data for {updated_count} attorneys.",
                          {"results": results}, ["email"], False, "/attorneys")
        return results
    except Exception as e:
        logger.error(f"UniCourt data import failed for organization {organization_id}: {str(e)}")
        send_notification(user_id, "unicourt_import_failed", "UniCourt Import Failed",
                          f"UniCourt import failed: {str(e)}", {"error": str(e)}, ["email"], True, "/attorneys")
        return {"status": IMPORT_STATUS["FAILED"], "error": str(e)}


@shared_task(bind=True, max_retries=3)
def process_file_import(self, file_path: str, file_type: str, import_type: str, organization_id: str,
                         mapping: dict, user_id: str) -> dict:
    """Process a file import (CSV or Excel) for attorneys, rates, or billing data"""
    logger.info(f"Starting file import for organization {organization_id} from {file_path}")
    try:
        # Retrieve the file from storage
        file_content = storage_client.get_file(file_path)

        # Create a temporary local copy of the file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        # Select the appropriate file processor based on file_type (CSV or Excel)
        if file_type == "csv":
            file_processor = CSVProcessor()
        elif file_type == "excel":
            file_processor = ExcelProcessor()
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Validate the file schema using the processor
        validation_schema = {}  # TODO: Define validation schema based on import_type
        if not file_processor.validate_schema(temp_file_path, validation_schema):
            raise ValueError(f"File schema validation failed: {file_processor.get_validation_errors()}")

        # Process the file into a list of records
        data = file_processor.process_file(temp_file_path)

        # Map the records to internal models using the provided field mapping
        # TODO: Implement field mapping logic

        # Validate the data using appropriate validation functions
        # TODO: Implement data validation logic

        # Store the data using the appropriate repository based on import_type
        # TODO: Implement data storage logic

        results = {
            "status": IMPORT_STATUS["COMPLETED"],
            "created": 0,  # TODO: Update with actual counts
            "updated": 0,  # TODO: Update with actual counts
            "skipped": 0,  # TODO: Update with actual counts
            "errors": []  # TODO: Update with actual errors
        }
        logger.info(f"File import completed for organization {organization_id} from {file_path} with results: {results}")
        send_notification(user_id, "file_import_complete", "File Import Complete",
                          f"Imported data from {file_path}.",
                          {"results": results}, ["email"], False, "/data")

        # Clean up the temporary file
        os.remove(temp_file_path)
        return results
    except Exception as e:
        logger.error(f"File import failed for organization {organization_id} from {file_path}: {str(e)}")
        send_notification(user_id, "file_import_failed", "File Import Failed",
                          f"File import failed: {str(e)}", {"error": str(e)}, ["email"], True, "/data")
        return {"status": IMPORT_STATUS["FAILED"], "error": str(e)}


def validate_import_data(data: list, import_type: str, organization_id: str) -> tuple:
    """Validate data before import to ensure it meets system requirements"""
    valid_data = []
    invalid_data = []
    error_messages = []

    # Determine the appropriate validation rules based on import_type
    if import_type == "rates":
        validation_rules = {}  # TODO: Define rate validation rules
    elif import_type == "attorneys":
        validation_rules = {}  # TODO: Define attorney validation rules
    elif import_type == "billing":
        validation_rules = {}  # TODO: Define billing validation rules
    else:
        raise ValueError(f"Unsupported import type: {import_type}")

    for record in data:
        try:
            # Apply validation rules to the record
            # TODO: Implement validation logic based on validation_rules
            valid_data.append(record)
        except Exception as e:
            invalid_data.append(record)
            error_messages.append(str(e))

    return valid_data, invalid_data, error_messages


@shared_task(bind=True, max_retries=3)
def retry_failed_import(self, import_id: str, user_id: str) -> dict:
    """Retry a previously failed import task"""
    logger.info(f"Retrying import task with ID {import_id} for user {user_id}")
    try:
        # Retrieve the original import task details
        # TODO: Implement retrieval of original task details

        # Based on the import type, call the appropriate import function
        # TODO: Implement logic to call the correct import function

        # Pass the original parameters to the new import task
        # TODO: Implement passing original parameters

        # Return the new import task ID and status
        return {"task_id": "new_task_id", "status": IMPORT_STATUS["PROCESSING"]}
    except Exception as e:
        logger.error(f"Failed to retry import task {import_id}: {str(e)}")
        return {"status": IMPORT_STATUS["FAILED"], "error": str(e)}


@shared_task(bind=True)
def check_import_status(self, task_id: str) -> dict:
    """Check the status of an ongoing import task"""
    logger.info(f"Checking status of import task with ID {task_id}")
    try:
        # Query the Celery task status using task_id
        task = self.AsyncResult(task_id)

        if task.state == "PENDING":
            # If task is still running, calculate progress if available
            progress = 0  # TODO: Implement progress calculation
            return {"status": IMPORT_STATUS["PENDING"], "progress": progress}
        elif task.state == "SUCCESS":
            # If task is complete, retrieve the result
            result = task.get()
            return {"status": IMPORT_STATUS["COMPLETED"], "result": result}
        elif task.state == "FAILURE":
            # If task failed, retrieve the error information
            error = str(task.info)
            return {"status": IMPORT_STATUS["FAILED"], "error": error}
        else:
            return {"status": task.state}
    except Exception as e:
        logger.error(f"Failed to check import status for task {task_id}: {str(e)}")
        return {"status": IMPORT_STATUS["FAILED"], "error": str(e)}


class ImportTracker:
    """Class to track and manage import jobs and their status"""

    def __init__(self):
        """Initialize the import tracker"""
        self.active_imports = {}
        self.import_history = {}

    def register_import(self, task_id: str, import_type: str, organization_id: str,
                        user_id: str, parameters: dict) -> str:
        """Register a new import task and track its status"""
        import_id = str(uuid.uuid4())
        self.active_imports[import_id] = {
            "task_id": task_id,
            "import_type": import_type,
            "organization_id": organization_id,
            "user_id": user_id,
            "parameters": parameters,
            "status": IMPORT_STATUS["PENDING"],
            "start_time": datetime.utcnow(),
            "end_time": None,
            "results": {}
        }
        logger.info(f"Registered import {import_id} for task {task_id}")
        return import_id

    def update_import_status(self, import_id: str, status: str, results: dict) -> bool:
        """Update the status of an active import task"""
        if import_id not in self.active_imports:
            logger.warning(f"Import with ID {import_id} not found")
            return False

        self.active_imports[import_id]["status"] = status
        self.active_imports[import_id]["end_time"] = datetime.utcnow()
        self.active_imports[import_id]["results"] = results

        if status in [IMPORT_STATUS["COMPLETED"], IMPORT_STATUS["FAILED"]]:
            self.import_history[import_id] = self.active_imports.pop(import_id)

        logger.info(f"Updated import {import_id} status to {status}")
        return True

    def get_import_status(self, import_id: str) -> dict:
        """Get the current status of an import task"""
        if import_id in self.active_imports:
            return self.active_imports[import_id]
        elif import_id in self.import_history:
            return self.import_history[import_id]
        else:
            return {"status": "NOT_FOUND"}


class ImportError(Exception):
    """Custom exception class for import-related errors"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        return f"ImportError: {self.message} Details: {self.details}"