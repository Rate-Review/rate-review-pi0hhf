"""
Currency management module for rate-related operations, handling currency conversions,
exchange rate management, and multi-currency calculations.
"""

import requests  # Making HTTP requests to the currency API
import json  # Processing JSON responses from the API
from decimal import Decimal  # Precise decimal calculations for currency conversions
from datetime import datetime, timedelta  # Date and time operations for exchange rate validity
from typing import Dict, List, Optional, Union  # Type hints for function parameters and returns

from ..utils.cache import cache_exchange_rate, get_cached_exchange_rate  # Cache exchange rates to avoid frequent external API calls
from ..integrations.currency.exchange_rate_api import get_exchange_rate  # Fetch current exchange rates from external API
from ..utils.logging import logger  # Logging currency conversion operations and errors
from ..db.session import db_session  # Database session for storing and retrieving custom exchange rates
from ..utils.constants import SUPPORTED_CURRENCIES, DEFAULT_CURRENCY  # Constants for currency-related operations
from ..utils.formatting import format_currency  # Format currency amounts according to locale

EXCHANGE_RATE_CACHE_TTL = 86400  # Cache exchange rates for 24 hours
CURRENCY_PRECISION = 4  # Number of decimal places for exchange rate calculations


def convert_rate(amount: Decimal, from_currency: str, to_currency: str, rate_date: datetime, use_custom_rates: bool) -> Decimal:
    """
    Converts a rate amount from one currency to another using current exchange rates.

    Args:
        amount (Decimal): The rate amount to convert
        from_currency (str): The currency code of the source currency
        to_currency (str): The currency code of the target currency
        rate_date (datetime): The date for which to retrieve the exchange rate
        use_custom_rates (bool): Flag to indicate whether to use custom exchange rate overrides

    Returns:
        Decimal: Converted rate amount in target currency
    """
    # Validate that both currencies are supported
    if from_currency not in SUPPORTED_CURRENCIES or to_currency not in SUPPORTED_CURRENCIES:
        logger.error(f"Unsupported currency: from_currency={from_currency}, to_currency={to_currency}")
        raise ValueError(f"Unsupported currency: from_currency={from_currency}, to_currency={to_currency}")

    # If currencies are the same, return the original amount
    if from_currency == to_currency:
        return amount

    # Get exchange rate between the currencies
    exchange_rate = get_exchange_rate_for_date(from_currency, to_currency, rate_date)

    # If custom rates are enabled, check for custom exchange rate overrides
    if use_custom_rates:
        custom_rate = get_custom_exchange_rate(from_currency, to_currency, rate_date)
        if custom_rate:
            exchange_rate = custom_rate
            logger.info(f"Using custom exchange rate for {from_currency} to {to_currency} on {rate_date}")

    # Apply conversion with appropriate precision
    converted_amount = amount * exchange_rate

    # Return the converted amount
    return converted_amount


def get_exchange_rate_for_date(from_currency: str, to_currency: str, rate_date: datetime) -> Decimal:
    """
    Retrieves exchange rate between two currencies for a specific date.

    Args:
        from_currency (str): The currency code of the source currency
        to_currency (str): The currency code of the target currency
        rate_date (datetime): The date for which to retrieve the exchange rate

    Returns:
        Decimal: Exchange rate to convert from source to target currency
    """
    # Check if exchange rate is cached
    cache_key = f"exchange_rate:{from_currency}:{to_currency}:{rate_date.strftime('%Y-%m-%d')}"
    cached_rate = get_cached_exchange_rate(cache_key)

    # If cached and valid, return cached rate
    if cached_rate:
        logger.info(f"Returning cached exchange rate for {from_currency} to {to_currency} on {rate_date}")
        return Decimal(cached_rate)

    # If not cached or invalid, fetch from external API
    try:
        exchange_rate = get_exchange_rate(from_currency, to_currency)
    except Exception as e:
        logger.error(f"Failed to retrieve exchange rate from API: {str(e)}")
        raise

    # Cache the fetched exchange rate
    cache_exchange_rate(cache_key, str(exchange_rate), EXCHANGE_RATE_CACHE_TTL)
    logger.info(f"Caching exchange rate for {from_currency} to {to_currency} on {rate_date}")

    # Return the exchange rate
    return exchange_rate


def get_custom_exchange_rate(from_currency: str, to_currency: str, rate_date: datetime) -> Optional[Decimal]:
    """
    Retrieves custom exchange rate override if available.

    Args:
        from_currency (str): The currency code of the source currency
        to_currency (str): The currency code of the target currency
        rate_date (datetime): The date for which to retrieve the exchange rate

    Returns:
        Optional[Decimal]: Custom exchange rate if available, None otherwise
    """
    # Query database for custom exchange rate between currencies for date
    try:
        # Placeholder for database query logic
        # custom_rate = db_session.query(CustomExchangeRate).filter(...).first()
        # For now, return None
        custom_rate = None

        # If custom rate exists, return it
        if custom_rate:
            logger.info(f"Found custom exchange rate for {from_currency} to {to_currency} on {rate_date}")
            return custom_rate.rate

        # Otherwise return None
        return None
    except Exception as e:
        logger.error(f"Error retrieving custom exchange rate: {str(e)}")
        return None


def set_custom_exchange_rate(from_currency: str, to_currency: str, rate: Decimal, effective_date: datetime, expiration_date: datetime) -> bool:
    """
    Sets a custom exchange rate override between two currencies.

    Args:
        from_currency (str): The currency code of the source currency
        to_currency (str): The currency code of the target currency
        rate (Decimal): The custom exchange rate
        effective_date (datetime): The date from which the custom rate is effective
        expiration_date (datetime): The date when the custom rate expires

    Returns:
        bool: Success status of the operation
    """
    # Validate currencies and rate value
    if from_currency not in SUPPORTED_CURRENCIES or to_currency not in SUPPORTED_CURRENCIES:
        logger.error(f"Unsupported currency: from_currency={from_currency}, to_currency={to_currency}")
        return False

    if rate <= 0:
        logger.error(f"Invalid exchange rate: {rate}")
        return False

    # Create or update custom exchange rate record in database
    try:
        # Placeholder for database update logic
        # custom_rate = CustomExchangeRate(...)
        # db_session.add(custom_rate)
        # db_session.commit()

        # Invalidate any cached exchange rates between these currencies
        cache_key = f"exchange_rate:{from_currency}:{to_currency}:*"
        # clear_cache_pattern(cache_key)

        logger.info(f"Set custom exchange rate for {from_currency} to {to_currency} = {rate}")
        return True
    except Exception as e:
        logger.error(f"Error setting custom exchange rate: {str(e)}")
        return False


def convert_rates_batch(rate_data: List[Dict], target_currency: str, use_custom_rates: bool) -> List[Dict]:
    """
    Converts multiple rate amounts from various currencies to a target currency.

    Args:
        rate_data (List[Dict]): List of dictionaries containing rate information
        target_currency (str): The currency code of the target currency
        use_custom_rates (bool): Flag to indicate whether to use custom exchange rate overrides

    Returns:
        List[Dict]: List of rates converted to target currency
    """
    converted_rates = []
    # Group rates by source currency to minimize API calls
    grouped_rates = {}
    for rate in rate_data:
        from_currency = rate['currency']
        if from_currency not in grouped_rates:
            grouped_rates[from_currency] = []
        grouped_rates[from_currency].append(rate)

    # For each currency group, get the exchange rate once
    for from_currency, rates in grouped_rates.items():
        try:
            # Get the exchange rate once
            exchange_rate = get_exchange_rate_for_date(from_currency, target_currency, datetime.now())

            # Apply conversion to all rates in the group
            for rate in rates:
                amount = rate['amount']
                converted_amount = amount * exchange_rate
                rate['amount'] = converted_amount
                rate['currency'] = target_currency
                converted_rates.append(rate)
        except Exception as e:
            logger.error(f"Error converting rates from {from_currency} to {target_currency}: {str(e)}")
            # Handle error appropriately, e.g., skip the rates or return an error value

    # Return list of converted rates with same structure as input
    return converted_rates


def format_rate_with_currency(amount: Decimal, currency: str, locale: str) -> str:
    """
    Formats a rate amount with its currency symbol.

    Args:
        amount (Decimal): The rate amount to format
        currency (str): The currency code
        locale (str): The locale to use for formatting

    Returns:
        str: Formatted rate with currency symbol
    """
    # Validate currency is supported
    if currency not in SUPPORTED_CURRENCIES:
        logger.error(f"Unsupported currency: {currency}")
        raise ValueError(f"Unsupported currency: {currency}")

    # Use formatting utility to format amount with currency symbol
    formatted_rate = format_currency(amount, currency, locale)

    # Return formatted string
    return formatted_rate


def validate_currency(currency: str) -> bool:
    """
    Validates if a currency is supported by the system.

    Args:
        currency (str): The currency code to validate

    Returns:
        bool: True if currency is supported, False otherwise
    """
    # Check if currency code is in SUPPORTED_CURRENCIES list
    is_valid = currency in SUPPORTED_CURRENCIES

    # Return validation result
    return is_valid


def get_currency_metadata(currency: str) -> Dict:
    """
    Retrieves metadata for a specific currency.

    Args:
        currency (str): The currency code

    Returns:
        Dict: Dictionary with currency metadata (symbol, name, format pattern)
    """
    # Validate currency is supported
    if currency not in SUPPORTED_CURRENCIES:
        logger.error(f"Unsupported currency: {currency}")
        raise ValueError(f"Unsupported currency: {currency}")

    # Return dictionary with currency metadata
    return {
        "symbol": get_currency_symbol(currency),
        "name": currency,
        "format_pattern": "#,##0.00"  # Example format pattern
    }


class CurrencyConverter:
    """
    Class that handles currency conversion operations with state.
    """

    def __init__(self, default_currency: str = DEFAULT_CURRENCY, use_custom_rates: bool = False):
        """
        Initializes a new CurrencyConverter instance.

        Args:
            default_currency (str): The default currency for the converter
            use_custom_rates (bool): Whether to use custom exchange rates
        """
        # Set default currency (default to system default if not provided)
        self.default_currency = default_currency

        # Set custom rates flag
        self.use_custom_rates = use_custom_rates

        # Initialize empty exchange rate cache
        self._exchange_rate_cache = {}

    def convert(self, amount: Decimal, from_currency: str, to_currency: str, rate_date: Optional[datetime] = None) -> Decimal:
        """
        Converts an amount from one currency to another.

        Args:
            amount (Decimal): The amount to convert
            from_currency (str): The currency code of the source currency
            to_currency (str): The currency code of the target currency
            rate_date (datetime): The date for which to retrieve the exchange rate

        Returns:
            Decimal: Converted amount
        """
        # Call convert_rate function with parameters and instance settings
        converted_amount = convert_rate(amount, from_currency, to_currency, rate_date, self.use_custom_rates)

        # Return the converted amount
        return converted_amount

    def convert_to_default(self, amount: Decimal, from_currency: str, rate_date: Optional[datetime] = None) -> Decimal:
        """
        Converts an amount from a currency to the default currency.

        Args:
            amount (Decimal): The amount to convert
            from_currency (str): The currency code of the source currency
            rate_date (datetime): The date for which to retrieve the exchange rate

        Returns:
            Decimal: Amount converted to default currency
        """
        # Call convert method with from_currency and default currency
        converted_amount = self.convert(amount, from_currency, self.default_currency, rate_date)

        # Return the converted amount
        return converted_amount

    def convert_from_default(self, amount: Decimal, to_currency: str, rate_date: Optional[datetime] = None) -> Decimal:
        """
        Converts an amount from the default currency to another currency.

        Args:
            amount (Decimal): The amount to convert
            to_currency (str): The currency code of the target currency
            rate_date (datetime): The date for which to retrieve the exchange rate

        Returns:
            Decimal: Amount converted from default currency
        """
        # Call convert method with default currency and to_currency
        converted_amount = self.convert(amount, self.default_currency, to_currency, rate_date)

        # Return the converted amount
        return converted_amount

    def batch_convert(self, items: List[Dict], target_currency: str, amount_key: str = 'amount', currency_key: str = 'currency', date_key: str = 'date') -> List[Dict]:
        """
        Converts multiple amounts to a target currency.

        Args:
            items (List[Dict]): List of dictionaries containing items to convert
            target_currency (str): The currency code of the target currency
            amount_key (str): The key in each item that contains the amount
            currency_key (str): The key in each item that contains the currency
            date_key (str): The key in each item that contains the date

        Returns:
            List[Dict]: List of items with converted amounts
        """
        # Group items by currency
        grouped_items = {}
        for item in items:
            from_currency = item[currency_key]
            if from_currency not in grouped_items:
                grouped_items[from_currency] = []
            grouped_items[from_currency].append(item)

        # For each currency group, convert amounts in batch
        for from_currency, items in grouped_items.items():
            amounts = [item[amount_key] for item in items]
            converted_amounts = batch_convert_currency(amounts, from_currency, target_currency)

            # Update the items with the converted amounts
            for i, item in enumerate(items):
                item[amount_key] = converted_amounts[i]
                item[currency_key] = target_currency

        # Return transformed list with converted amounts
        return items