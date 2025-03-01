"""
Utility module providing currency validation, conversion, and formatting functionality 
to support multi-currency rate negotiations across the application.
"""

import requests
import json
from decimal import Decimal
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

from ..utils.redis_client import get_redis_client
from ..app.config import AppConfig
from ..utils.logging import get_logger

# Default currency used when no currency is specified
DEFAULT_CURRENCY = "USD"

# List of currency codes supported by the system
SUPPORTED_CURRENCIES = [
    "USD",  # US Dollar
    "EUR",  # Euro
    "GBP",  # British Pound
    "JPY",  # Japanese Yen
    "CAD",  # Canadian Dollar
    "AUD",  # Australian Dollar
    "CHF",  # Swiss Franc
    "CNY",  # Chinese Yuan
    "HKD",  # Hong Kong Dollar
    "SGD",  # Singapore Dollar
]

# Currency symbols for formatting
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CAD": "C$",
    "AUD": "A$",
    "CHF": "Fr",
    "CNY": "¥",
    "HKD": "HK$",
    "SGD": "S$"
}

# Number of decimal places for each currency
CURRENCY_PRECISION = {
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
    "JPY": 0,
    "CAD": 2,
    "AUD": 2,
    "CHF": 2,
    "CNY": 2,
    "HKD": 2,
    "SGD": 2
}

# Cache TTL for exchange rates in seconds (1 day)
EXCHANGE_RATE_CACHE_TTL = 86400

# Set up logger
logger = get_logger(__name__)

def is_valid_currency(currency_code: str) -> bool:
    """
    Validates if a currency code is supported by the system.
    
    Args:
        currency_code: The currency code to validate
        
    Returns:
        True if the currency is supported, False otherwise
    """
    return currency_code.upper() in SUPPORTED_CURRENCIES

def get_currency_symbol(currency_code: str) -> str:
    """
    Retrieves the symbol for a given currency code.
    
    Args:
        currency_code: The currency code
        
    Returns:
        The currency symbol for the given currency code
    """
    if not is_valid_currency(currency_code):
        logger.warning(f"Attempted to get symbol for unsupported currency: {currency_code}")
        return f"({currency_code})"
    
    return CURRENCY_SYMBOLS.get(currency_code.upper(), f"({currency_code})")

def format_currency(amount: Decimal, currency_code: str, include_symbol: bool = True) -> str:
    """
    Formats a decimal value as a currency string with the appropriate symbol and formatting.
    
    Args:
        amount: The amount to format
        currency_code: The currency code
        include_symbol: Whether to include the currency symbol
        
    Returns:
        Formatted currency string
    """
    if not is_valid_currency(currency_code):
        logger.warning(f"Attempted to format unsupported currency: {currency_code}")
        currency_code = DEFAULT_CURRENCY
    
    currency_code = currency_code.upper()
    
    # Round to appropriate precision
    amount = round_currency(amount, currency_code)
    
    # Get the symbol if needed
    symbol = get_currency_symbol(currency_code) if include_symbol else ""
    
    # Format based on currency
    if currency_code == "JPY":
        # JPY typically doesn't use decimal places
        formatted = f"{int(amount):,}"
    else:
        # Get precision for this currency
        precision = CURRENCY_PRECISION.get(currency_code, 2)
        formatted = f"{amount:,.{precision}f}"
    
    # Different currencies have different symbol placements
    if currency_code in ["USD", "CAD", "AUD", "HKD", "SGD"]:
        return f"{symbol}{formatted}"
    elif currency_code in ["EUR", "GBP", "CHF", "JPY", "CNY"]:
        # Some European currencies and Asian currencies have the symbol before the amount
        return f"{symbol}{formatted}"
    else:
        # Default format
        return f"{symbol}{formatted}"

def get_exchange_rate(from_currency: str, to_currency: str, force_refresh: bool = False) -> Decimal:
    """
    Retrieves the exchange rate between two currencies, using cached values or fetching from an API.
    
    Args:
        from_currency: The source currency code
        to_currency: The target currency code
        force_refresh: Whether to force a refresh from the API
        
    Returns:
        The exchange rate to convert from the source to target currency
    """
    # Standardize currency codes
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    # Validate currencies
    if not is_valid_currency(from_currency) or not is_valid_currency(to_currency):
        logger.error(f"Invalid currency in exchange rate request: {from_currency} to {to_currency}")
        raise ValueError(f"Unsupported currency code: {from_currency if not is_valid_currency(from_currency) else to_currency}")
    
    # If currencies are the same, rate is 1.0
    if from_currency == to_currency:
        return Decimal('1.0')
    
    # Try to get from cache first if not forcing refresh
    if not force_refresh:
        redis_client = get_redis_client()
        cache_key = f"exchange_rate:{from_currency}:{to_currency}"
        
        cached_rate = redis_client.get(cache_key)
        if cached_rate:
            logger.debug(f"Retrieved exchange rate from cache: {from_currency} to {to_currency} = {cached_rate}")
            return Decimal(cached_rate)
    
    # Need to fetch from API
    try:
        # Get settings for currency API
        app_config = AppConfig()
        config = app_config.config
        api_key = getattr(config, 'CURRENCY_API_KEY', None)
        api_url = getattr(config, 'CURRENCY_API_URL', 'https://api.exchangerate-api.com/v4/latest/')
        
        if not api_key:
            logger.warning("No currency API key configured, using fallback method")
            # Fallback to public API that doesn't require a key
            response = requests.get(f"{api_url}{from_currency}")
        else:
            # Use API with key
            response = requests.get(f"{api_url}{from_currency}", params={"api_key": api_key})
        
        response.raise_for_status()
        data = response.json()
        
        # API responses vary, but most provide a rates object
        if "rates" in data and to_currency in data["rates"]:
            rate = Decimal(str(data["rates"][to_currency]))
        else:
            logger.error(f"Unexpected API response format or currency not found: {to_currency}")
            raise ValueError(f"Could not retrieve exchange rate for {to_currency}")
        
        # Cache the result
        redis_client = get_redis_client()
        cache_key = f"exchange_rate:{from_currency}:{to_currency}"
        redis_client.set(cache_key, str(rate), EXCHANGE_RATE_CACHE_TTL)
        
        logger.info(f"Retrieved and cached exchange rate from API: {from_currency} to {to_currency} = {rate}")
        return rate
    
    except requests.RequestException as e:
        logger.error(f"Error fetching exchange rate: {str(e)}")
        # Try inverse rate if available in cache
        redis_client = get_redis_client()
        inverse_cache_key = f"exchange_rate:{to_currency}:{from_currency}"
        inverse_rate = redis_client.get(inverse_cache_key)
        
        if inverse_rate:
            rate = Decimal('1') / Decimal(inverse_rate)
            logger.warning(f"Using calculated inverse rate: {from_currency} to {to_currency} = {rate}")
            return rate
        
        raise ValueError(f"Failed to retrieve exchange rate and no cached data available: {str(e)}")

def convert_currency(amount: Decimal, from_currency: str, to_currency: str, 
                    exchange_rate: Optional[Decimal] = None) -> Decimal:
    """
    Converts an amount from one currency to another using current exchange rates.
    
    Args:
        amount: The amount to convert
        from_currency: The source currency code
        to_currency: The target currency code
        exchange_rate: Optional specific exchange rate to use
        
    Returns:
        The converted amount in the target currency
    """
    # Standardize currency codes
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    # Validate currencies
    if not is_valid_currency(from_currency) or not is_valid_currency(to_currency):
        logger.error(f"Invalid currency in conversion request: {from_currency} to {to_currency}")
        raise ValueError(f"Unsupported currency code: {from_currency if not is_valid_currency(from_currency) else to_currency}")
    
    # If currencies are the same, no conversion needed
    if from_currency == to_currency:
        return amount
    
    # Get exchange rate if not provided
    if exchange_rate is None:
        exchange_rate = get_exchange_rate(from_currency, to_currency)
    
    # Convert the amount
    converted_amount = amount * exchange_rate
    
    # Round to appropriate precision for target currency
    converted_amount = round_currency(converted_amount, to_currency)
    
    logger.debug(f"Converted {amount} {from_currency} to {converted_amount} {to_currency} (rate: {exchange_rate})")
    return converted_amount

def get_all_exchange_rates(base_currency: str, force_refresh: bool = False) -> Dict[str, Decimal]:
    """
    Retrieves all exchange rates for a base currency against all supported currencies.
    
    Args:
        base_currency: The base currency code
        force_refresh: Whether to force a refresh from the API
        
    Returns:
        Dictionary mapping currency codes to their exchange rates against the base currency
    """
    # Standardize currency code
    base_currency = base_currency.upper()
    
    # Validate currency
    if not is_valid_currency(base_currency):
        logger.error(f"Invalid base currency for exchange rates: {base_currency}")
        raise ValueError(f"Unsupported currency code: {base_currency}")
    
    # Try to get all rates from cache first if not forcing refresh
    if not force_refresh:
        redis_client = get_redis_client()
        cache_key = f"all_exchange_rates:{base_currency}"
        
        cached_rates = redis_client.get(cache_key)
        if cached_rates:
            try:
                rates_dict = {k: Decimal(v) for k, v in json.loads(cached_rates).items()}
                logger.debug(f"Retrieved all exchange rates from cache for {base_currency}")
                return rates_dict
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Invalid cache data for {cache_key}, fetching fresh data")
    
    # Need to fetch from API
    try:
        # Get settings for currency API
        app_config = AppConfig()
        config = app_config.config
        api_key = getattr(config, 'CURRENCY_API_KEY', None)
        api_url = getattr(config, 'CURRENCY_API_URL', 'https://api.exchangerate-api.com/v4/latest/')
        
        if not api_key:
            logger.warning("No currency API key configured, using fallback method")
            # Fallback to public API that doesn't require a key
            response = requests.get(f"{api_url}{base_currency}")
        else:
            # Use API with key
            response = requests.get(f"{api_url}{base_currency}", params={"api_key": api_key})
        
        response.raise_for_status()
        data = response.json()
        
        # API responses vary, but most provide a rates object
        if "rates" not in data:
            logger.error(f"Unexpected API response format: {data}")
            raise ValueError("Could not retrieve exchange rates from API")
        
        # Filter for supported currencies only
        rates_dict = {
            curr: Decimal(str(data["rates"][curr])) 
            for curr in SUPPORTED_CURRENCIES 
            if curr in data["rates"]
        }
        
        # Add base currency with rate 1.0
        rates_dict[base_currency] = Decimal('1.0')
        
        # Cache the result
        redis_client = get_redis_client()
        cache_key = f"all_exchange_rates:{base_currency}"
        redis_client.set(
            cache_key, 
            json.dumps({k: str(v) for k, v in rates_dict.items()}),
            EXCHANGE_RATE_CACHE_TTL
        )
        
        logger.info(f"Retrieved and cached all exchange rates for {base_currency}")
        return rates_dict
    
    except requests.RequestException as e:
        logger.error(f"Error fetching exchange rates: {str(e)}")
        raise ValueError(f"Failed to retrieve exchange rates: {str(e)}")

def batch_convert_currency(amounts: List[Decimal], from_currency: str, 
                          to_currency: str) -> List[Decimal]:
    """
    Converts multiple amounts from one currency to another in a single operation.
    
    Args:
        amounts: List of amounts to convert
        from_currency: The source currency code
        to_currency: The target currency code
        
    Returns:
        List of converted amounts in the target currency
    """
    # Standardize currency codes
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    # Validate currencies
    if not is_valid_currency(from_currency) or not is_valid_currency(to_currency):
        logger.error(f"Invalid currency in batch conversion: {from_currency} to {to_currency}")
        raise ValueError(f"Unsupported currency code: {from_currency if not is_valid_currency(from_currency) else to_currency}")
    
    # If currencies are the same, no conversion needed
    if from_currency == to_currency:
        return amounts
    
    # Get exchange rate once for efficiency
    exchange_rate = get_exchange_rate(from_currency, to_currency)
    
    # Convert all amounts
    converted_amounts = [
        round_currency(amount * exchange_rate, to_currency)
        for amount in amounts
    ]
    
    logger.debug(f"Batch converted {len(amounts)} amounts from {from_currency} to {to_currency}")
    return converted_amounts

def refresh_exchange_rates() -> bool:
    """
    Forces a refresh of all exchange rates from the currency API.
    
    Returns:
        True if refresh was successful, False otherwise
    """
    try:
        # Refresh rates for each supported currency
        for base_currency in SUPPORTED_CURRENCIES:
            get_all_exchange_rates(base_currency, force_refresh=True)
            
        logger.info("Successfully refreshed all exchange rates")
        return True
    except Exception as e:
        logger.error(f"Failed to refresh exchange rates: {str(e)}")
        return False

def set_custom_exchange_rate(from_currency: str, to_currency: str, 
                            rate: Decimal, ttl: int = EXCHANGE_RATE_CACHE_TTL) -> bool:
    """
    Sets a custom exchange rate between two currencies, overriding the default rate.
    
    Args:
        from_currency: The source currency code
        to_currency: The target currency code
        rate: The custom exchange rate
        ttl: Time-to-live in seconds for this custom rate
        
    Returns:
        True if the custom rate was set successfully, False otherwise
    """
    # Standardize currency codes
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    # Validate currencies
    if not is_valid_currency(from_currency) or not is_valid_currency(to_currency):
        logger.error(f"Invalid currency in custom rate setting: {from_currency} to {to_currency}")
        raise ValueError(f"Unsupported currency code: {from_currency if not is_valid_currency(from_currency) else to_currency}")
    
    # Validate rate
    if rate <= Decimal('0'):
        logger.error(f"Invalid exchange rate: {rate}")
        raise ValueError("Exchange rate must be positive")
    
    try:
        # Set the custom rate in the cache
        redis_client = get_redis_client()
        cache_key = f"exchange_rate:{from_currency}:{to_currency}"
        redis_client.set(cache_key, str(rate), ttl)
        
        # Also set the inverse rate
        inverse_rate = Decimal('1') / rate
        inverse_cache_key = f"exchange_rate:{to_currency}:{from_currency}"
        redis_client.set(inverse_cache_key, str(inverse_rate), ttl)
        
        logger.info(f"Set custom exchange rate: {from_currency} to {to_currency} = {rate} (ttl: {ttl}s)")
        return True
    except Exception as e:
        logger.error(f"Failed to set custom exchange rate: {str(e)}")
        return False

def round_currency(amount: Decimal, currency_code: str) -> Decimal:
    """
    Rounds an amount to the appropriate number of decimal places for a given currency.
    
    Args:
        amount: The amount to round
        currency_code: The currency code
        
    Returns:
        The amount rounded to the appropriate precision for the currency
    """
    # Standardize currency code
    currency_code = currency_code.upper()
    
    # Validate currency
    if not is_valid_currency(currency_code):
        logger.warning(f"Attempted to round for unsupported currency: {currency_code}")
        currency_code = DEFAULT_CURRENCY
    
    # Get precision for this currency
    precision = CURRENCY_PRECISION.get(currency_code, 2)
    
    # Round to the appropriate number of decimal places
    rounded = amount.quantize(Decimal('0.1') ** precision)
    
    return rounded