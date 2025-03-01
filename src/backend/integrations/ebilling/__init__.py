"""
Initialization file for the eBilling integration module that acts as an entry point for integrating with various client eBilling systems (Onit, TeamConnect, Legal Tracker, BrightFlag). Provides factory functions and exports adapters for each supported system.
"""

from typing import Union

from ...utils.constants import IntegrationType  # Import IntegrationType enum
from ...utils.logging import get_logger  # Import logger utility
from .brightflag import BrightFlagAdapter, create_brightflag_adapter  # Import BrightFlag adapter and factory
from .legal_tracker import LegalTrackerAdapter, create_legal_tracker_adapter  # Import Legal Tracker adapter and factory
from .onit import OnitAdapter, create_onit_adapter  # Import Onit adapter and factory
from .teamconnect import TeamConnectAdapter, create_teamconnect_adapter  # Import TeamConnect adapter and factory

# Initialize logger for this module
logger = get_logger(__name__)

__all__ = [
    'create_ebilling_adapter',
    'TeamConnectAdapter',
    'OnitAdapter',
    'LegalTrackerAdapter',
    'BrightFlagAdapter'
]


def create_ebilling_adapter(
    integration_type: str,
    name: str,
    base_url: str,
    auth_credentials: dict,
    headers: dict,
    timeout: int,
    verify_ssl: bool
) -> Union[TeamConnectAdapter, OnitAdapter, LegalTrackerAdapter, BrightFlagAdapter]:
    """
    Factory function that creates and returns an appropriate eBilling adapter based on the integration type

    Args:
        integration_type (str): Type of eBilling system (e.g., 'onit', 'teamconnect', 'legal_tracker', 'brightflag')
        name (str): Name of the eBilling system instance
        base_url (str): Base URL for the eBilling system API
        auth_credentials (dict): Authentication credentials for the eBilling system
        headers (dict): Additional headers for API requests
        timeout (int): Timeout for API requests in seconds
        verify_ssl (bool): Whether to verify SSL certificates

    Returns:
        Union[TeamConnectAdapter, OnitAdapter, LegalTrackerAdapter, BrightFlagAdapter]: An initialized adapter instance for the specified eBilling system

    Raises:
        ValueError: If an unsupported integration type is provided
    """
    logger.info(f"Attempting to create eBilling adapter for integration type: {integration_type}")

    if integration_type == IntegrationType.EBILLING_TEAMCONNECT.value:
        logger.debug("Creating TeamConnect adapter")
        return create_teamconnect_adapter(name, base_url, auth_credentials, headers, timeout, verify_ssl)
    elif integration_type == IntegrationType.EBILLING_ONIT.value:
        logger.debug("Creating Onit adapter")
        return create_onit_adapter(name, base_url, auth_credentials, headers, timeout, verify_ssl)
    elif integration_type == IntegrationType.EBILLING_LEGAL_TRACKER.value:
        logger.debug("Creating Legal Tracker adapter")
        return create_legal_tracker_adapter(name, base_url, auth_credentials, headers, timeout, verify_ssl)
    elif integration_type == IntegrationType.EBILLING_BRIGHTFLAG.value:
        logger.debug("Creating BrightFlag adapter")
        return create_brightflag_adapter(name, base_url, auth_credentials, headers, timeout, verify_ssl)
    else:
        error_message = f"Unsupported eBilling integration type: {integration_type}"
        logger.error(error_message)
        raise ValueError(error_message)