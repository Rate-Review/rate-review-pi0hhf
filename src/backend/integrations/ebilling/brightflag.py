import requests  # Version: 2.28.2
import json
from typing import Dict, List, Optional, Union
from datetime import datetime
import os
from dataclasses import dataclass

from ..common.adapter import BaseAdapter
from ..common.client import BaseIntegrationClient
from ...utils.logging import logger
from ...utils.encryption import encrypt_credentials, decrypt_credentials
from ...utils.validators import validate_rate_data, validate_timekeeper_data

# Define global variables for BrightFlag API configuration
BRIGHTFLAG_API_BASE_URL = os.environ.get("BRIGHTFLAG_API_BASE_URL", "https://api.brightflag.com/v1")
BRIGHTFLAG_FIELD_MAPPINGS = {
    "rate_amount": {"source_field": "rate"},
    "currency": {"source_field": "currency"},
    "effective_date": {"source_field": "start_date"},
    "timekeeper_id": {"source_field": "timekeeper_id"},
    "timekeeper_name": {"source_field": "timekeeper_name"},
}


def map_rate_to_brightflag(rate_data: Dict) -> Dict:
    """Maps a Justice Bid rate object to BrightFlag format.

    Args:
        rate_data (dict): Justice Bid rate data.

    Returns:
        dict: BrightFlag-formatted rate data.
    """
    brightflag_rate = {}
    brightflag_rate["rate"] = rate_data.get("rate_amount")
    brightflag_rate["currency"] = rate_data.get("currency")
    brightflag_rate["start_date"] = datetime.strptime(rate_data.get("effective_date"), "%Y-%m-%d").strftime("%Y-%m-%d")
    return brightflag_rate


def map_brightflag_to_rate(brightflag_data: Dict) -> Dict:
    """Maps BrightFlag rate data to Justice Bid format.

    Args:
        brightflag_data (dict): BrightFlag rate data.

    Returns:
        dict: Justice Bid-formatted rate data.
    """
    rate_data = {}
    rate_data["rate_amount"] = brightflag_data.get("rate")
    rate_data["currency"] = brightflag_data.get("currency")
    rate_data["effective_date"] = datetime.strptime(brightflag_data.get("start_date"), "%Y-%m-%d").strftime("%Y-%m-%d")
    return rate_data


def map_timekeeper_to_brightflag(timekeeper_data: Dict) -> Dict:
    """Maps a Justice Bid attorney/timekeeper to BrightFlag format.

    Args:
        timekeeper_data (dict): Justice Bid timekeeper data.

    Returns:
        dict: BrightFlag-formatted timekeeper data.
    """
    brightflag_timekeeper = {}
    brightflag_timekeeper["timekeeper_id"] = timekeeper_data.get("timekeeper_id")
    brightflag_timekeeper["timekeeper_name"] = timekeeper_data.get("name")
    return brightflag_timekeeper


def map_brightflag_to_timekeeper(brightflag_data: Dict) -> Dict:
    """Maps BrightFlag timekeeper data to Justice Bid format.

    Args:
        brightflag_data (dict): BrightFlag timekeeper data.

    Returns:
        dict: Justice Bid-formatted timekeeper data.
    """
    timekeeper_data = {}
    timekeeper_data["timekeeper_id"] = brightflag_data.get("timekeeper_id")
    timekeeper_data["name"] = brightflag_data.get("timekeeper_name")
    return timekeeper_data


class BrightFlagClient(BaseIntegrationClient):
    """Client for communicating with the BrightFlag API."""

    def __init__(self, api_key: str, client_id: str, base_url: str = BRIGHTFLAG_API_BASE_URL):
        """Initialize the BrightFlag API client.

        Args:
            api_key (str): BrightFlag API key.
            client_id (str): BrightFlag client ID.
            base_url (str, optional): Base URL for the BrightFlag API. Defaults to BRIGHTFLAG_API_BASE_URL.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client_id = client_id
        super().__init__(
            base_url=self.base_url,
            auth_config={"api_key": self.api_key, "client_id": self.client_id},
            auth_method="api_key",
            headers={"X-Client-Id": self.client_id},
            timeout=30,
            max_retries=3,
            verify_ssl=True,
        )
        self.session.headers.update({"X-API-Key": self.api_key})
        logger.info("Initialized BrightFlagClient", extra={"additional_data": {"base_url": self.base_url}})

    def get_rates(self, vendor_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Retrieve rates from BrightFlag.

        Args:
            vendor_id (str): BrightFlag vendor ID.
            start_date (datetime): Start date for rate retrieval.
            end_date (datetime): End date for rate retrieval.

        Returns:
            List[Dict]: List of rate dictionaries.
        """
        endpoint = f"/vendors/{vendor_id}/rates"
        params = {"start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d")}
        rates = self.get(endpoint, params=params)
        logger.info(f"Retrieved {len(rates)} rates from BrightFlag for vendor {vendor_id}")
        return rates

    def get_timekeepers(self, vendor_id: str) -> List[Dict]:
        """Retrieve timekeeper data from BrightFlag.

        Args:
            vendor_id (str): BrightFlag vendor ID.

        Returns:
            List[Dict]: List of timekeeper dictionaries.
        """
        endpoint = f"/vendors/{vendor_id}/timekeepers"
        timekeepers = self.get(endpoint)
        logger.info(f"Retrieved {len(timekeepers)} timekeepers from BrightFlag for vendor {vendor_id}")
        return timekeepers

    def get_billing_data(self, vendor_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Retrieve historical billing data from BrightFlag.

        Args:
            vendor_id (str): BrightFlag vendor ID.
            start_date (datetime): Start date for billing data retrieval.
            end_date (datetime): End date for billing data retrieval.

        Returns:
            List[Dict]: List of billing entry dictionaries.
        """
        endpoint = f"/vendors/{vendor_id}/billing_data"
        params = {"start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d")}
        billing_data = self.get(endpoint, params=params)
        logger.info(f"Retrieved {len(billing_data)} billing entries from BrightFlag for vendor {vendor_id}")
        return billing_data

    def update_rates(self, rates: List[Dict]) -> Dict:
        """Update rates in BrightFlag.

        Args:
            rates (List[Dict]): List of rate dictionaries.

        Returns:
            Dict: API response with success/failure information.
        """
        endpoint = "/rates/bulk_update"
        brightflag_rates = [map_rate_to_brightflag(rate) for rate in rates]
        response = self.post(endpoint, json_data={"rates": brightflag_rates})
        logger.info(f"Updated {len(rates)} rates in BrightFlag")
        return response

    def test_connection(self) -> bool:
        """Test the connection to BrightFlag API.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            response = self.get("/ping", raw_response=True)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


class BrightFlagAdapter(BaseAdapter):
    """Adapter for integrating with BrightFlag eBilling system."""

    def __init__(self, config: Dict):
        """Initialize the BrightFlag adapter with configuration.

        Args:
            config (Dict): Configuration dictionary.
        """
        super().__init__()
        self.config = config
        api_key = config.get("api_key")
        client_id = config.get("client_id")
        if not api_key or not client_id:
            raise ValueError("BrightFlag API key and client ID are required")

        self.client = BrightFlagClient(api_key=api_key, client_id=client_id)
        self.field_mappings = BRIGHTFLAG_FIELD_MAPPINGS
        logger.info("Initialized BrightFlagAdapter")

    def import_rates(self, vendor_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Import rates from BrightFlag.

        Args:
            vendor_id (str): BrightFlag vendor ID.
            start_date (datetime): Start date for rate retrieval.
            end_date (datetime): End date for rate retrieval.

        Returns:
            List[Dict]: List of imported rate dictionaries in Justice Bid format.
        """
        brightflag_rates = self.client.get_rates(vendor_id, start_date, end_date)
        rates = [map_brightflag_to_rate(rate) for rate in brightflag_rates]
        for rate in rates:
            validate_rate_data(rate, "BrightFlag Rate")
        logger.info(f"Imported {len(rates)} rates from BrightFlag for vendor {vendor_id}")
        return rates

    def import_timekeepers(self, vendor_id: str) -> List[Dict]:
        """Import timekeeper data from BrightFlag.

        Args:
            vendor_id (str): BrightFlag vendor ID.

        Returns:
            List[Dict]: List of imported timekeeper dictionaries in Justice Bid format.
        """
        brightflag_timekeepers = self.client.get_timekeepers(vendor_id)
        timekeepers = [map_brightflag_to_timekeeper(timekeeper) for timekeeper in brightflag_timekeepers]
        for timekeeper in timekeepers:
            validate_timekeeper_data(timekeeper, "BrightFlag Timekeeper")
        logger.info(f"Imported {len(timekeepers)} timekeepers from BrightFlag for vendor {vendor_id}")
        return timekeepers

    def import_billing_data(self, vendor_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Import historical billing data from BrightFlag.

        Args:
            vendor_id (str): BrightFlag vendor ID.
            start_date (datetime): Start date for billing data retrieval.
            end_date (datetime): End date for billing data retrieval.

        Returns:
            List[Dict]: List of imported billing entries in Justice Bid format.
        """
        billing_data = self.client.get_billing_data(vendor_id, start_date, end_date)
        # TODO: Transform data to Justice Bid format
        logger.info(f"Imported {len(billing_data)} billing entries from BrightFlag for vendor {vendor_id}")
        return billing_data

    def export_rates(self, rates: List[Dict]) -> Dict:
        """Export approved rates to BrightFlag.

        Args:
            rates (List[Dict]): List of rate dictionaries.

        Returns:
            Dict: Export results with success/failure information.
        """
        # TODO: Validate data before export
        brightflag_rates = [map_rate_to_brightflag(rate) for rate in rates]
        response = self.client.update_rates(brightflag_rates)
        logger.info(f"Exported {len(rates)} rates to BrightFlag")
        return response

    def validate_connection(self) -> Dict:
        """Validate the connection to BrightFlag.

        Returns:
            Dict: Connection status with details.
        """
        status = self.client.test_connection()
        return {"status": status, "message": "Connection test " + ("succeeded" if status else "failed")}

    def get_field_mapping(self) -> Dict:
        """Get the field mapping between Justice Bid and BrightFlag.

        Returns:
            Dict: Field mapping dictionary.
        """
        return self.field_mappings

    def update_field_mapping(self, mapping_updates: Dict) -> Dict:
        """Update the field mapping configuration.

        Args:
            mapping_updates (Dict): Dictionary containing mapping updates.

        Returns:
            Dict: Updated field mapping dictionary.
        """
        self.field_mappings.update(mapping_updates)
        return self.field_mappings