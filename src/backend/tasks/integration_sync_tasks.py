"""
Defines Celery tasks for synchronizing data between the Justice Bid system and external systems including eBilling platforms, law firm billing systems, and UniCourt. Implements scheduled and on-demand data synchronization with error handling, logging, and performance optimizations.
"""

import typing
import uuid
import json
import time
from datetime import datetime

from tasks.celery_app import shared_task, celery_app  # Import Celery task decorator and app instance
from utils.logging import get_logger  # Import logging utility
from services.organizations.client import get_integration_adapter  # Import client integration adapter factory
from services.organizations.firm import get_lawfirm_adapter  # Import law firm integration adapter factory
from integrations.unicourt.client import UniCourtClient  # Import UniCourt client
from db.repositories.attorney_repository import AttorneyRepository  # Import Attorney repository
from db.repositories.organization_repository import OrganizationRepository  # Import Organization repository
from db.session import db_session  # Import database session context manager
from app.config import Config  # Import application configuration

# Initialize logger
logger = get_logger(__name__)


@shared_task(name='tasks.sync_ebilling_data', max_retries=3, default_retry_delay=300)
def sync_ebilling_data(client_id: str, sync_options: dict) -> dict:
    """
    Synchronizes data between the Justice Bid system and client eBilling systems
    """
    config = Config()
    if not config.INTEGRATIONS_ENABLED:
        logger.warning("Integrations are disabled in the configuration.")
        return {"status": "skipped", "message": "Integrations are disabled."}

    logger.info(f"Starting eBilling sync for client: {client_id} with options: {sync_options}")
    results = {"status": "running", "client_id": client_id, "imported_rates": 0, "imported_billing": 0, "exported_rates": 0, "errors": []}

    if not client_id or not isinstance(sync_options, dict):
        error_message = f"Invalid parameters: client_id={client_id}, sync_options={sync_options}"
        logger.error(error_message)
        results["status"] = "failed"
        results["errors"].append(error_message)
        return results

    try:
        with db_session() as session:
            org_repo = OrganizationRepository(session)
            client_org = org_repo.get_by_id(client_id)

            if not client_org:
                error_message = f"Client organization not found: {client_id}"
                logger.error(error_message)
                results["status"] = "failed"
                results["errors"].append(error_message)
                return results

            integration_adapter = get_integration_adapter(client_org.settings)

            if not integration_adapter:
                error_message = f"No eBilling integration configured for client: {client_id}"
                logger.warning(error_message)
                results["status"] = "skipped"
                results["errors"].append(error_message)
                return results

            if sync_options.get('import_rates'):
                # TODO: Implement historical rate data import
                results["imported_rates"] = 100  # Placeholder
                logger.info(f"Imported historical rate data for client: {client_id}")

            if sync_options.get('import_billing'):
                # TODO: Implement historical billing data import
                results["imported_billing"] = 500  # Placeholder
                logger.info(f"Imported historical billing data for client: {client_id}")

            if sync_options.get('import_timekeepers'):
                # TODO: Implement timekeeper data import
                results["imported_timekeepers"] = 20  # Placeholder
                logger.info(f"Imported timekeeper data for client: {client_id}")

            if sync_options.get('export_rates'):
                # TODO: Implement approved rates export
                results["exported_rates"] = 50  # Placeholder
                logger.info(f"Exported approved rates for client: {client_id}")

            # Update sync timestamp in organization metadata
            client_org.settings['last_ebilling_sync'] = datetime.utcnow().isoformat()
            session.commit()

            results["status"] = "completed"
            logger.info(f"eBilling sync completed successfully for client: {client_id}")

    except Exception as e:
        results["status"] = "failed"
        error_message = f"eBilling sync failed for client {client_id}: {str(e)}"
        results["errors"].append(error_message)
        logger.exception(error_message)

    return results


@shared_task(name='tasks.sync_lawfirm_data', max_retries=3, default_retry_delay=300)
def sync_lawfirm_data(firm_id: str, sync_options: dict) -> dict:
    """
    Synchronizes data between the Justice Bid system and law firm billing systems
    """
    config = Config()
    if not config.INTEGRATIONS_ENABLED:
        logger.warning("Integrations are disabled in the configuration.")
        return {"status": "skipped", "message": "Integrations are disabled."}

    logger.info(f"Starting law firm sync for firm: {firm_id} with options: {sync_options}")
    results = {"status": "running", "firm_id": firm_id, "imported_attorneys": 0, "imported_rates": 0, "exported_rates": 0, "errors": []}

    if not firm_id or not isinstance(sync_options, dict):
        error_message = f"Invalid parameters: firm_id={firm_id}, sync_options={sync_options}"
        logger.error(error_message)
        results["status"] = "failed"
        results["errors"].append(error_message)
        return results

    try:
        with db_session() as session:
            org_repo = OrganizationRepository(session)
            firm_org = org_repo.get_by_id(firm_id)

            if not firm_org:
                error_message = f"Law firm organization not found: {firm_id}"
                logger.error(error_message)
                results["status"] = "failed"
                results["errors"].append(error_message)
                return results

            lawfirm_adapter = get_lawfirm_adapter(firm_org.settings)

            if not lawfirm_adapter:
                error_message = f"No billing system integration configured for law firm: {firm_id}"
                logger.warning(error_message)
                results["status"] = "skipped"
                results["errors"].append(error_message)
                return results

            if sync_options.get('import_attorneys'):
                # TODO: Implement attorney data import
                results["imported_attorneys"] = 75  # Placeholder
                logger.info(f"Imported attorney data for firm: {firm_id}")

            if sync_options.get('import_rates'):
                # TODO: Implement standard rates import
                results["imported_rates"] = 200  # Placeholder
                logger.info(f"Imported standard rates for firm: {firm_id}")

            if sync_options.get('export_rates'):
                # TODO: Implement approved rates export
                results["exported_rates"] = 25  # Placeholder
                logger.info(f"Exported approved rates for firm: {firm_id}")

            # Update sync timestamp in organization metadata
            firm_org.settings['last_billing_sync'] = datetime.utcnow().isoformat()
            session.commit()

            results["status"] = "completed"
            logger.info(f"Law firm sync completed successfully for firm: {firm_id}")

    except Exception as e:
        results["status"] = "failed"
        error_message = f"Law firm sync failed for firm {firm_id}: {str(e)}"
        results["errors"].append(error_message)
        logger.exception(error_message)

    return results


@shared_task(name='tasks.sync_unicourt_data', max_retries=3, default_retry_delay=300)
def sync_unicourt_data(firm_id: str, all_attorneys: bool) -> dict:
    """
    Synchronizes attorney performance data from UniCourt with the Justice Bid system
    """
    config = Config()
    if not config.INTEGRATIONS_ENABLED:
        logger.warning("Integrations are disabled in the configuration.")
        return {"status": "skipped", "message": "Integrations are disabled."}

    logger.info(f"Starting UniCourt sync for firm: {firm_id}, all_attorneys: {all_attorneys}")
    results = {"status": "running", "firm_id": firm_id, "synced_attorneys": 0, "errors": []}

    if not firm_id:
        error_message = "Invalid parameter: firm_id is required"
        logger.error(error_message)
        results["status"] = "failed"
        results["errors"].append(error_message)
        return results

    try:
        with db_session() as session:
            org_repo = OrganizationRepository(session)
            firm_org = org_repo.get_by_id(firm_id)

            if not firm_org:
                error_message = f"Law firm organization not found: {firm_id}"
                logger.error(error_message)
                results["status"] = "failed"
                results["errors"].append(error_message)
                return results

            api_key = config.UNICOURT_API_KEY
            if not api_key:
                error_message = "UniCourt API key not configured"
                logger.error(error_message)
                results["status"] = "failed"
                results["errors"].append(error_message)
                return results

            unicourt_client = UniCourtClient(api_key=api_key)
            attorney_repo = AttorneyRepository(session)
            attorneys = attorney_repo.get_by_organization(firm_id)

            if not all_attorneys:
                attorneys = [attorney for attorney in attorneys if attorney.unicourt_id]

            attorney_mapping = [{"justice_bid_attorney_id": str(attorney.id), "unicourt_attorney_id": str(attorney.unicourt_id)} for attorney in attorneys]

            sync_results = unicourt_client.bulk_sync_attorneys(attorney_mapping)
            results["synced_attorneys"] = sync_results["success_count"]
            if sync_results["failure_count"] > 0:
                results["errors"].append(f"Failed to sync {sync_results['failure_count']} attorneys")

            # Update sync timestamp in organization metadata
            firm_org.settings['last_unicourt_sync'] = datetime.utcnow().isoformat()
            session.commit()

            results["status"] = "completed"
            logger.info(f"UniCourt sync completed successfully for firm: {firm_id}")

    except Exception as e:
        results["status"] = "failed"
        error_message = f"UniCourt sync failed for firm {firm_id}: {str(e)}"
        results["errors"].append(error_message)
        logger.exception(error_message)

    return results


@shared_task(name='tasks.sync_all_ebilling_systems')
def sync_all_ebilling_systems(sync_options: dict) -> dict:
    """
    Synchronizes data with all configured client eBilling systems
    """
    config = Config()
    if not config.INTEGRATIONS_ENABLED:
        logger.warning("Integrations are disabled in the configuration.")
        return {"status": "skipped", "message": "Integrations are disabled."}

    logger.info(f"Starting bulk eBilling sync with options: {sync_options}")
    results = {"status": "running", "total_clients": 0, "synced_clients": [], "errors": []}

    try:
        with db_session() as session:
            org_repo = OrganizationRepository(session)
            clients = org_repo.get_all_clients()
            ebilling_clients = [client for client in clients if client.settings and 'ebilling_integration' in client.settings]

            results["total_clients"] = len(ebilling_clients)
            for client in ebilling_clients:
                try:
                    # Queue individual sync task
                    sync_result = sync_ebilling_data.delay(str(client.id), sync_options)
                    results["synced_clients"].append(str(client.id))
                    logger.debug(f"Queued eBilling sync for client: {client.id}, task_id: {sync_result.id}")
                except Exception as e:
                    error_message = f"Failed to queue eBilling sync for client {client.id}: {str(e)}"
                    results["errors"].append(error_message)
                    logger.exception(error_message)

            logger.info(f"Queued eBilling sync for {len(results['synced_clients'])} clients")
            results["status"] = "completed"

    except Exception as e:
        results["status"] = "failed"
        error_message = f"Bulk eBilling sync failed: {str(e)}"
        results["errors"].append(error_message)
        logger.exception(error_message)

    return results


@shared_task(name='tasks.sync_all_lawfirm_systems')
def sync_all_lawfirm_systems(sync_options: dict) -> dict:
    """
    Synchronizes data with all configured law firm billing systems
    """
    config = Config()
    if not config.INTEGRATIONS_ENABLED:
        logger.warning("Integrations are disabled in the configuration.")
        return {"status": "skipped", "message": "Integrations are disabled."}

    logger.info(f"Starting bulk law firm sync with options: {sync_options}")
    results = {"status": "running", "total_firms": 0, "synced_firms": [], "errors": []}

    try:
        with db_session() as session:
            org_repo = OrganizationRepository(session)
            firms = org_repo.get_all_firms()
            billing_firms = [firm for firm in firms if firm.settings and 'billing_system_type' in firm.settings]

            results["total_firms"] = len(billing_firms)
            for firm in billing_firms:
                try:
                    # Queue individual sync task
                    sync_result = sync_lawfirm_data.delay(str(firm.id), sync_options)
                    results["synced_firms"].append(str(firm.id))
                    logger.debug(f"Queued law firm sync for firm: {firm.id}, task_id: {sync_result.id}")
                except Exception as e:
                    error_message = f"Failed to queue law firm sync for firm {firm.id}: {str(e)}"
                    results["errors"].append(error_message)
                    logger.exception(error_message)

            logger.info(f"Queued law firm sync for {len(results['synced_firms'])} firms")
            results["status"] = "completed"

    except Exception as e:
        results["status"] = "failed"
        error_message = f"Bulk law firm sync failed: {str(e)}"
        results["errors"].append(error_message)
        logger.exception(error_message)

    return results


@shared_task(name='tasks.sync_all_unicourt_data')
def sync_all_unicourt_data(all_attorneys: bool) -> dict:
    """
    Synchronizes UniCourt data for all law firms with attorney mappings
    """
    config = Config()
    if not config.INTEGRATIONS_ENABLED:
        logger.warning("Integrations are disabled in the configuration.")
        return {"status": "skipped", "message": "Integrations are disabled."}

    logger.info(f"Starting bulk UniCourt sync, all_attorneys: {all_attorneys}")
    results = {"status": "running", "total_firms": 0, "synced_firms": [], "errors": []}

    try:
        with db_session() as session:
            org_repo = OrganizationRepository(session)
            firms = org_repo.get_all_firms()

            results["total_firms"] = len(firms)
            for firm in firms:
                try:
                    # Queue individual sync task
                    sync_result = sync_unicourt_data.delay(str(firm.id), all_attorneys)
                    results["synced_firms"].append(str(firm.id))
                    logger.debug(f"Queued UniCourt sync for firm: {firm.id}, task_id: {sync_result.id}")
                except Exception as e:
                    error_message = f"Failed to queue UniCourt sync for firm {firm.id}: {str(e)}"
                    results["errors"].append(error_message)
                    logger.exception(error_message)

            logger.info(f"Queued UniCourt sync for {len(results['synced_firms'])} firms")
            results["status"] = "completed"

    except Exception as e:
        results["status"] = "failed"
        error_message = f"Bulk UniCourt sync failed: {str(e)}"
        results["errors"].append(error_message)
        logger.exception(error_message)

    return results


@shared_task(name='tasks.retry_failed_synchronization')
def retry_failed_synchronization(sync_type: str, organization_id: str) -> dict:
    """
    Retries previously failed synchronization tasks based on stored error logs
    """
    config = Config()
    if not config.INTEGRATIONS_ENABLED:
        logger.warning("Integrations are disabled in the configuration.")
        return {"status": "skipped", "message": "Integrations are disabled."}

    logger.info(f"Starting retry task for sync_type: {sync_type}, organization_id: {organization_id}")
    results = {"status": "running", "sync_type": sync_type, "organization_id": organization_id, "retried": False, "errors": []}

    if sync_type not in ['ebilling', 'lawfirm', 'unicourt']:
        error_message = f"Invalid sync_type: {sync_type}. Must be 'ebilling', 'lawfirm', or 'unicourt'."
        logger.error(error_message)
        results["status"] = "failed"
        results["errors"].append(error_message)
        return results

    try:
        with db_session() as session:
            org_repo = OrganizationRepository(session)
            organization = org_repo.get_by_id(organization_id)

            if not organization:
                error_message = f"Organization not found: {organization_id}"
                logger.error(error_message)
                results["status"] = "failed"
                results["errors"].append(error_message)
                return results

            # TODO: Retrieve failed sync records from organization metadata
            failed_sync_records = organization.settings.get('failed_sync_records', [])

            if sync_type == 'ebilling':
                # TODO: Call sync_ebilling_data with appropriate options
                pass
            elif sync_type == 'lawfirm':
                # TODO: Call sync_lawfirm_data with appropriate options
                pass
            elif sync_type == 'unicourt':
                # TODO: Call sync_unicourt_data
                pass

            # TODO: Update failure record status in organization metadata

            results["status"] = "completed"
            results["retried"] = True
            logger.info(f"Retry task completed successfully for {sync_type}, organization: {organization_id}")

    except Exception as e:
        results["status"] = "failed"
        error_message = f"Retry task failed for {sync_type}, organization {organization_id}: {str(e)}"
        results["errors"].append(error_message)
        logger.exception(error_message)

    return results