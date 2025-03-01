"""
Integration module for interacting with an external currency exchange rate API to fetch, store, and manage currency conversion rates for multi-currency support in the Justice Bid system.
"""

import requests  #  Making HTTP requests to the currency API
import json  # Processing JSON responses from the API
from datetime import datetime  # Handling date objects for historical exchange rates
from typing import List, Dict, Optional, Any  # Type annotations

from ..common.adapter import BaseAdapter  # Base class for integration adapters
from ..common.client import BaseClient  # Base class for API clients
from ...utils.cache import cache  # Caching utility for API responses
from ...utils.logging import logger  # Logging utility

DEFAULT_BASE_CURRENCY = "USD"
CACHE_DURATION = 86400  # 24 hours


class ExchangeRateClient(BaseClient):
    """Client for interacting with the currency exchange rate API"""

    def __init__(self, api_key: str, base_url: str):
        """Initialize the exchange rate API client"""
        super().__init__(base_url=base_url, auth_config={'api_key': api_key}, auth_method='api_key')
        self.api_key = api_key
        self.base_url = base_url

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to the exchange rate API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        params['apikey'] = self.api_key
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    def get_latest_rates(self, base_currency: str, symbols: Optional[List[str]] = None) -> Dict[str, float]:
        """Get latest exchange rates for a base currency"""
        params = {'base': base_currency}
        if symbols:
            params['symbols'] = ','.join(symbols)
        data = self._make_request('latest', params)
        return data['rates']

    def get_historical_rates(self, date: datetime, base_currency: str, symbols: Optional[List[str]] = None) -> Dict[str, float]:
        """Get historical exchange rates for a specific date"""
        date_str = date.strftime('%Y-%m-%d')
        params = {'base': base_currency}
        if symbols:
            params['symbols'] = ','.join(symbols)
        data = self._make_request(date_str, params)
        return data['rates']

    def convert(self, amount: float, from_currency: str, to_currency: str, date: Optional[datetime] = None) -> float:
        """Convert amount between currencies"""
        if from_currency == to_currency:
            return amount

        if date:
            rates = self.get_historical_rates(date, from_currency, [to_currency])
        else:
            rates = self.get_latest_rates(from_currency, [to_currency])

        rate = rates[to_currency]
        return amount * rate

    def get_supported_currencies(self) -> List[str]:
        """Get list of all supported currencies"""
        data = self._make_request('symbols', {})
        return list(data['symbols'].keys())


class ExchangeRateAdapter(BaseAdapter):
    """Adapter that provides a standardized interface for currency exchange functionality"""

    def __init__(self, client: ExchangeRateClient):
        """Initialize the exchange rate adapter"""
        super().__init__(name="ExchangeRateAdapter", integration_type="currency")
        self.client = client
        self._override_rates: Dict[str, Dict[str, float]] = {}

    def get_rate(self, from_currency: str, to_currency: str, date: Optional[datetime] = None) -> float:
        """Get exchange rate between two currencies, respecting any overrides"""
        if from_currency == to_currency:
            return 1.0

        if from_currency in self._override_rates and to_currency in self._override_rates[from_currency]:
            return self._override_rates[from_currency][to_currency]

        if date:
            rates = self.client.get_historical_rates(date, from_currency, [to_currency])
        else:
            rates = self.client.get_latest_rates(from_currency, [to_currency])

        return rates[to_currency]

    def convert(self, amount: float, from_currency: str, to_currency: str, date: Optional[datetime] = None) -> float:
        """Convert amount between currencies, respecting any overrides"""
        if from_currency == to_currency:
            return amount

        rate = self.get_rate(from_currency, to_currency, date)
        return amount * rate

    def override_rate(self, from_currency: str, to_currency: str, rate: float) -> None:
        """Override an exchange rate between two currencies"""
        if rate <= 0:
            raise ValueError("Rate must be positive")

        if from_currency not in self._override_rates:
            self._override_rates[from_currency] = {}
        self._override_rates[from_currency][to_currency] = rate

        if to_currency not in self._override_rates:
            self._override_rates[to_currency] = {}
        self._override_rates[to_currency][from_currency] = 1 / rate

        logger.info(f"Overriding rate: {from_currency} to {to_currency} = {rate}")

    def clear_rate_override(self, from_currency: str, to_currency: str) -> bool:
        """Clear an overridden exchange rate"""
        cleared = False
        if from_currency in self._override_rates:
            if to_currency in self._override_rates[from_currency]:
                del self._override_rates[from_currency][to_currency]
                cleared = True
        if to_currency in self._override_rates:
            if from_currency in self._override_rates[to_currency]:
                del self._override_rates[to_currency][from_currency]
                cleared = True

        if cleared:
            logger.info(f"Cleared rate override: {from_currency} to {to_currency}")
            return True
        else:
            return False

    def clear_all_overrides(self) -> None:
        """Clear all rate overrides"""
        self._override_rates.clear()
        logger.info("Cleared all rate overrides")

    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        return self.client.get_supported_currencies()


@cache(duration=CACHE_DURATION)
def get_exchange_rate(from_currency: str, to_currency: str, date: Optional[datetime] = None) -> float:
    """Get the exchange rate between two currencies"""
    if from_currency == to_currency:
        return 1.0

    app_config = AppConfig()
    config = app_config.config
    api_key = config.CURRENCY_API_KEY
    api_url = config.CURRENCY_API_URL

    client = ExchangeRateClient(api_key=api_key, base_url=api_url)
    adapter = ExchangeRateAdapter(client=client)
    return adapter.get_rate(from_currency=from_currency, to_currency=to_currency, date=date)


def convert_amount(amount: float, from_currency: str, to_currency: str, date: Optional[datetime] = None) -> float:
    """Convert an amount from one currency to another"""
    if from_currency == to_currency:
        return amount

    app_config = AppConfig()
    config = app_config.config
    api_key = config.CURRENCY_API_KEY
    api_url = config.CURRENCY_API_URL

    client = ExchangeRateClient(api_key=api_key, base_url=api_url)
    adapter = ExchangeRateAdapter(client=client)
    return adapter.convert(amount=amount, from_currency=from_currency, to_currency=to_currency, date=date)


@cache(duration=CACHE_DURATION * 7)
def get_supported_currencies() -> List[str]:
    """Get list of supported currencies from the API"""
    app_config = AppConfig()
    config = app_config.config
    api_key = config.CURRENCY_API_KEY
    api_url = config.CURRENCY_API_URL

    client = ExchangeRateClient(api_key=api_key, base_url=api_url)
    adapter = ExchangeRateAdapter(client=client)
    return adapter.get_supported_currencies()