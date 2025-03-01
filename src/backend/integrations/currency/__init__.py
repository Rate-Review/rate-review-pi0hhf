"""
Initialization file for the currency integration module, exposing key classes and functions to provide easy access to exchange rate functionality throughout the Justice Bid application.
"""

from datetime import datetime  # vstandard library - Date handling for historical exchange rates
from decimal import Decimal  # vstandard library - Decimal type for precise currency calculations

from .exchange_rate_api import ExchangeRateClient, ExchangeRateAPIError, get_exchange_rate_client  # vInternal - Import the ExchangeRateClient class for handling currency exchange rate operations
from ...utils.constants import CurrencyCode, DEFAULT_CURRENCY  # vInternal - Import enumeration of supported currency codes


def get_exchange_rate(from_currency: str, to_currency: str, use_cache: bool = True) -> Decimal:
    """
    Convenience function to get the current exchange rate between two currencies

    Args:
        from_currency (str): The source currency code
        to_currency (str): The target currency code
        use_cache (bool): Whether to use cached exchange rates

    Returns:
        decimal.Decimal: The exchange rate from source to target currency
    """
    # LD1: Get a client instance using get_exchange_rate_client
    client = get_exchange_rate_client()
    # LD2: Call get_latest_rate method on the client with from_currency, to_currency, and use_cache
    exchange_rate = client.get_latest_rate(from_currency, to_currency, use_cache=use_cache)
    # LD3: Return the exchange rate
    return exchange_rate


def get_historical_rate(from_currency: str, to_currency: str, date: datetime.date, use_cache: bool = True) -> Decimal:
    """
    Convenience function to get a historical exchange rate for a specific date

    Args:
        from_currency (str): The source currency code
        to_currency (str): The target currency code
        date (datetime.date): The date for which to retrieve the exchange rate
        use_cache (bool): Whether to use cached exchange rates

    Returns:
        decimal.Decimal: The historical exchange rate for the specified date
    """
    # LD1: Get a client instance using get_exchange_rate_client
    client = get_exchange_rate_client()
    # LD2: Call get_historical_rate method on the client with from_currency, to_currency, date, and use_cache
    exchange_rate = client.get_historical_rate(from_currency, to_currency, date, use_cache=use_cache)
    # LD3: Return the historical exchange rate
    return exchange_rate


def convert_amount(amount: Decimal, from_currency: str, to_currency: str, use_cache: bool = True) -> Decimal:
    """
    Convenience function to convert an amount from one currency to another

    Args:
        amount (decimal.Decimal): The amount to convert
        from_currency (str): The source currency code
        to_currency (str): The target currency code
        use_cache (bool): Whether to use cached exchange rates

    Returns:
        decimal.Decimal: The converted amount in the target currency
    """
    # LD1: Get a client instance using get_exchange_rate_client
    client = get_exchange_rate_client()
    # LD2: Call convert_amount method on the client with amount, from_currency, to_currency, and use_cache
    converted_amount = client.convert_amount(amount, from_currency, to_currency, use_cache=use_cache)
    # LD3: Return the converted amount
    return converted_amount


def get_all_rates(base_currency: str, use_cache: bool = True) -> dict:
    """
    Convenience function to get all exchange rates for a base currency

    Args:
        base_currency (str): The base currency code
        use_cache (bool): Whether to use cached exchange rates

    Returns:
        dict: Dictionary mapping currency codes to exchange rates
    """
    # LD1: Get a client instance using get_exchange_rate_client
    client = get_exchange_rate_client()
    # LD2: Call get_all_rates method on the client with base_currency and use_cache
    exchange_rates = client.get_all_rates(base_currency, use_cache=use_cache)
    # LD3: Return the dictionary of exchange rates
    return exchange_rates


def get_supported_currencies() -> list:
    """
    Returns the list of currencies supported by the system

    Args:
        None

    Returns:
        list: List of supported currency codes
    """
    # LD1: Return the CurrencyCode values as a list
    return [currency.value for currency in CurrencyCode]


def refresh_exchange_rates() -> bool:
    """
    Forces a refresh of all exchange rates from the API

    Args:
        None

    Returns:
        bool: Success status of the refresh operation
    """
    # LD1: Get a client instance using get_exchange_rate_client
    client = get_exchange_rate_client()
    # LD2: Call refresh_all_rates method on the client
    success = client.refresh_all_rates()
    # LD3: Return the operation success status
    return success


__all__ = [
    'ExchangeRateClient',
    'ExchangeRateAPIError',
    'get_exchange_rate_client',
    'get_exchange_rate',
    'get_historical_rate',
    'convert_amount',
    'get_all_rates',
    'get_supported_currencies',
    'refresh_exchange_rates',
    'DEFAULT_CURRENCY'
]