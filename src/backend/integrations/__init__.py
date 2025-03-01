"""
Initialization file for the integrations package, exposing key integration components for external systems
including eBilling systems, law firm billing systems, UniCourt API, OpenAI, and file-based integration capabilities.
"""

from .common.adapter import BaseAdapter  # Internal import
from .common.adapter import APIAdapter  # Internal import
from .common.adapter import FileAdapter  # Internal import
from .common.adapter import create_adapter  # Internal import
from .common.client import BaseIntegrationClient  # Internal import
from .common.client import ApiError  # Internal import
from .common.client import CircuitBreakerError  # Internal import
from .common.client import RateLimitError  # Internal import
from .common.mapper import Mapper  # Internal import
from .common.mapper import FieldMapper  # Internal import
from .ebilling.teamconnect import TeamConnectAdapter  # Internal import
from .ebilling.teamconnect import TeamConnectClient  # Internal import
from .ebilling.teamconnect import create_teamconnect_adapter  # Internal import
from .ebilling.legal_tracker import LegalTrackerAdapter  # Internal import
from .ebilling.legal_tracker import create_legal_tracker_adapter  # Internal import
from .ebilling.onit import OnitAdapter  # Internal import
from .ebilling.onit import create_onit_adapter  # Internal import
from .unicourt.client import UniCourtClient  # Internal import
from ..utils.constants import IntegrationType  # Internal import

VERSION = "1.0.0"
SUPPORTED_INTEGRATIONS = [IntegrationType.EBILLING_TEAMCONNECT, IntegrationType.EBILLING_LEGAL_TRACKER, IntegrationType.EBILLING_ONIT, IntegrationType.UNICOURT, IntegrationType.OPENAI]


def get_supported_integrations() -> list:
    """Returns the list of supported integration types

    Returns:
        list: List of supported IntegrationType values
    """
    return SUPPORTED_INTEGRATIONS


def create_integration_adapter(integration_type: IntegrationType, name: str, base_url: str, auth_credentials: dict, headers: dict, timeout: int, verify_ssl: bool) -> BaseAdapter:
    """Factory function to create the appropriate integration adapter based on integration type

    Args:
        integration_type (IntegrationType): integration_type
        name (str): name
        base_url (str): base_url
        auth_credentials (dict): auth_credentials
        headers (dict): headers
        timeout (int): timeout
        verify_ssl (bool): verify_ssl

    Returns:
        BaseAdapter: Initialized adapter for the specified integration type
    """
    if integration_type == IntegrationType.EBILLING_TEAMCONNECT:
        adapter = create_teamconnect_adapter(name=name, base_url=base_url, auth_credentials=auth_credentials, headers=headers, timeout=timeout, verify_ssl=verify_ssl)
    elif integration_type == IntegrationType.EBILLING_LEGAL_TRACKER:
        adapter = create_legal_tracker_adapter(name=name, base_url=base_url, auth_credentials=auth_credentials, headers=headers, timeout=timeout, verify_ssl=verify_ssl)
    elif integration_type == IntegrationType.EBILLING_ONIT:
        adapter = create_onit_adapter(name=name, base_url=base_url, auth_credentials=auth_credentials, headers=headers, timeout=timeout, verify_ssl=verify_ssl)
    else:
        adapter = create_adapter(integration_type=integration_type, config={"name": name, "base_url": base_url, "auth_credentials": auth_credentials, "headers": headers, "timeout": timeout, "verify_ssl": verify_ssl})
    return adapter


def create_unicourt_client(api_key: str, base_url: str, timeout: int) -> UniCourtClient:
    """Factory function to create a UniCourt client instance

    Args:
        api_key (str): api_key
        base_url (str): base_url
        timeout (int): timeout

    Returns:
        UniCourtClient: Initialized UniCourt client instance
    """
    return UniCourtClient(api_key=api_key, base_url=base_url, timeout=timeout)