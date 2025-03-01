"""
Utility functions for formatting various types of data in the Justice Bid Rate Negotiation System,
including currencies, dates, percentages, and text.
"""

from datetime import date, datetime
from decimal import Decimal
import locale
from typing import Optional, Union

# Try to import Babel, but provide fallback if not available
try:
    import babel.numbers
    import babel.dates
    from babel.core import UnknownLocaleError
    BABEL_AVAILABLE = True
except ImportError:
    BABEL_AVAILABLE = False

from ..utils.constants import DEFAULT_CURRENCY, DEFAULT_LOCALE
from ..utils.currency import get_currency_symbol, convert_currency
from ..utils.datetime_utils import get_local_timezone

# Default number of decimal places for formatting numbers
DEFAULT_DECIMAL_PLACES = 2

# Default number of decimal places for formatting percentages
PERCENTAGE_DECIMAL_PLACES = 1


def format_currency(amount: Decimal, currency_code: Optional[str] = None, 
                   locale: Optional[str] = None, decimal_places: Optional[int] = None) -> str:
    """
    Formats a monetary value according to the specified currency and locale.
    
    Args:
        amount: The monetary value to format
        currency_code: Currency code (e.g., 'USD', 'EUR'). Defaults to system default currency.
        locale: Locale code (e.g., 'en_US', 'fr_FR'). Defaults to system default locale.
        decimal_places: Number of decimal places. Defaults to standard for the currency.
    
    Returns:
        Formatted currency string with appropriate symbol and formatting
    """
    if currency_code is None:
        currency_code = DEFAULT_CURRENCY
    
    if locale is None:
        locale = DEFAULT_LOCALE
    
    if decimal_places is None:
        decimal_places = DEFAULT_DECIMAL_PLACES
    
    # Try to use Babel if available
    if BABEL_AVAILABLE:
        try:
            # Use Babel's format_currency for locale-aware formatting
            formatted = babel.numbers.format_currency(
                amount, 
                currency_code, 
                locale=locale,
                decimal_quantization=False,
                format_type='standard'
            )
            return formatted
        except (ValueError, UnknownLocaleError, Exception):
            # Fall through to fallback formatting
            pass
    
    # Fallback formatting if Babel fails or is not available
    try:
        symbol = get_currency_symbol(currency_code)
        formatted_number = f"{float(amount):,.{decimal_places}f}"
        return f"{symbol}{formatted_number}"
    except Exception:
        # Last resort fallback
        return f"{currency_code} {float(amount):,.{decimal_places}f}"


def format_percentage(value: Decimal, decimal_places: Optional[int] = None, 
                     locale: Optional[str] = None, include_symbol: Optional[bool] = True) -> str:
    """
    Formats a decimal value as a percentage.
    
    Args:
        value: The decimal value to format as percentage (e.g., 0.05 for 5%)
        decimal_places: Number of decimal places. Defaults to PERCENTAGE_DECIMAL_PLACES.
        locale: Locale code (e.g., 'en_US', 'fr_FR'). Defaults to system default locale.
        include_symbol: Whether to include the % symbol. Defaults to True.
    
    Returns:
        Formatted percentage string
    """
    if decimal_places is None:
        decimal_places = PERCENTAGE_DECIMAL_PLACES
    
    if locale is None:
        locale = DEFAULT_LOCALE
    
    # Convert to percentage value (multiply by 100)
    percentage_value = value * 100
    
    # Try to use Babel if available
    if BABEL_AVAILABLE:
        try:
            # Use Babel for locale-aware formatting
            if include_symbol:
                return babel.numbers.format_percent(
                    value, 
                    locale=locale, 
                    decimal_quantization=False,
                    format=f"#,##0.{'0' * decimal_places} %"
                )
            else:
                formatted = babel.numbers.format_decimal(
                    percentage_value,
                    locale=locale,
                    decimal_quantization=False,
                    format=f"#,##0.{'0' * decimal_places}"
                )
                return formatted
        except (ValueError, UnknownLocaleError, Exception):
            # Fall through to fallback formatting
            pass
    
    # Fallback formatting
    formatted = f"{float(percentage_value):,.{decimal_places}f}"
    if include_symbol:
        return f"{formatted}%"
    return formatted


def format_date(date_obj: date, format_str: Optional[str] = None, 
               locale: Optional[str] = None) -> str:
    """
    Formats a date according to the specified format and locale.
    
    Args:
        date_obj: The date to format
        format_str: Format string (e.g., 'yyyy-MM-dd'). If None, uses locale default.
        locale: Locale code (e.g., 'en_US', 'fr_FR'). Defaults to system default locale.
    
    Returns:
        Formatted date string
    """
    if locale is None:
        locale = DEFAULT_LOCALE
    
    # Try to use Babel if available
    if BABEL_AVAILABLE:
        try:
            # Use Babel for locale-aware date formatting
            if format_str is None:
                # Use locale's default date format
                return babel.dates.format_date(date_obj, locale=locale)
            else:
                # Use specified format
                return babel.dates.format_date(date_obj, format=format_str, locale=locale)
        except (ValueError, UnknownLocaleError, Exception):
            # Fall through to fallback formatting
            pass
    
    # Fallback formatting
    if format_str is None:
        # Use a locale-appropriate format based on locale string
        if locale.startswith('en_US'):
            format_str = "%m/%d/%Y"  # MM/DD/YYYY for US
        elif locale.startswith(('en_GB', 'fr_', 'de_')):
            format_str = "%d/%m/%Y"  # DD/MM/YYYY for UK, France, Germany
        elif locale.startswith('ja_'):
            format_str = "%Y/%m/%d"  # YYYY/MM/DD for Japan
        else:
            format_str = "%Y-%m-%d"  # ISO format as default fallback
    
    try:
        return date_obj.strftime(format_str)
    except Exception:
        # Last resort fallback to ISO format
        return date_obj.isoformat()


def format_datetime(dt: datetime, format_str: Optional[str] = None,
                   locale: Optional[str] = None, timezone: Optional[str] = None) -> str:
    """
    Formats a datetime according to the specified format, locale, and timezone.
    
    Args:
        dt: The datetime to format
        format_str: Format string. If None, uses locale default.
        locale: Locale code (e.g., 'en_US', 'fr_FR'). Defaults to system default locale.
        timezone: Timezone name (e.g., 'America/New_York'). If None, uses user's timezone.
    
    Returns:
        Formatted datetime string
    """
    if locale is None:
        locale = DEFAULT_LOCALE
    
    if timezone is None:
        try:
            timezone = get_local_timezone()
        except Exception:
            timezone = None
    
    # Try to convert to specified timezone
    try:
        if timezone and dt.tzinfo is not None:
            dt = dt.astimezone(timezone)
    except Exception:
        # Continue with original timezone if conversion fails
        pass
    
    # Try to use Babel if available
    if BABEL_AVAILABLE:
        try:
            # Use Babel for locale-aware datetime formatting
            if format_str is None:
                # Use locale's default datetime format
                return babel.dates.format_datetime(dt, locale=locale, tzinfo=timezone)
            else:
                # Use specified format
                return babel.dates.format_datetime(dt, format=format_str, locale=locale, tzinfo=timezone)
        except (ValueError, UnknownLocaleError, Exception):
            # Fall through to fallback formatting
            pass
    
    # Fallback formatting
    if format_str is None:
        # Use a locale-appropriate format based on locale string
        if locale.startswith('en_US'):
            format_str = "%m/%d/%Y %I:%M:%S %p"  # US format with 12-hour clock
        elif locale.startswith(('en_GB', 'fr_')):
            format_str = "%d/%m/%Y %H:%M:%S"  # UK/French format with 24-hour clock
        elif locale.startswith('de_'):
            format_str = "%d.%m.%Y %H:%M:%S"  # German format with 24-hour clock
        elif locale.startswith('ja_'):
            format_str = "%Y/%m/%d %H:%M:%S"  # Japanese format
        else:
            format_str = "%Y-%m-%d %H:%M:%S"  # ISO-like format as default fallback
    
    try:
        return dt.strftime(format_str)
    except Exception:
        # Last resort fallback to ISO format
        return dt.isoformat()


def format_number(number: Union[int, float, Decimal], decimal_places: Optional[int] = None,
                 locale: Optional[str] = None) -> str:
    """
    Formats a number according to the specified locale and decimal places.
    
    Args:
        number: The number to format
        decimal_places: Number of decimal places. Defaults to DEFAULT_DECIMAL_PLACES.
        locale: Locale code (e.g., 'en_US', 'fr_FR'). Defaults to system default locale.
    
    Returns:
        Formatted number string
    """
    if decimal_places is None:
        decimal_places = DEFAULT_DECIMAL_PLACES
    
    if locale is None:
        locale = DEFAULT_LOCALE
    
    # Try to use Babel if available
    if BABEL_AVAILABLE:
        try:
            # Use Babel for locale-aware number formatting
            pattern = f"#,##0.{'0' * decimal_places}"
            return babel.numbers.format_decimal(
                number,
                format=pattern,
                locale=locale,
                decimal_quantization=False
            )
        except (ValueError, UnknownLocaleError, Exception):
            # Fall through to fallback formatting
            pass
    
    # Fallback formatting with simple comma as thousands separator
    try:
        value = float(number)
        integer_part = int(value)
        # Format integer part with commas
        integer_str = f"{integer_part:,}"
        
        if decimal_places > 0:
            # Add decimal part
            decimal_part = abs(value - integer_part)
            decimal_str = f"{decimal_part:.{decimal_places}f}".lstrip('0')
            if decimal_str.startswith('.'):
                return f"{integer_str}{decimal_str}"
            else:
                return f"{integer_str}.{'0' * decimal_places}"
        else:
            return integer_str
    except Exception:
        # Last resort fallback
        return f"{float(number):.{decimal_places}f}"


def truncate_text(text: str, max_length: int, ellipsis: Optional[str] = None) -> str:
    """
    Truncates text to a specified length and adds ellipsis if needed.
    
    Args:
        text: The text to truncate
        max_length: Maximum length of the returned string
        ellipsis: String to append if text is truncated. Defaults to '...'.
    
    Returns:
        Truncated text with ellipsis if needed
    """
    if not text:
        return ""
    
    if ellipsis is None:
        ellipsis = "..."
    
    if len(text) <= max_length:
        return text
    
    # Account for ellipsis length
    truncated_length = max_length - len(ellipsis)
    if truncated_length <= 0:
        truncated_length = max_length
        ellipsis = ""
    
    return text[:truncated_length] + ellipsis


def format_name(first_name: str, last_name: str, middle_name: Optional[str] = None,
               style: Optional[str] = None) -> str:
    """
    Formats a person's name according to the specified style.
    
    Args:
        first_name: First name
        last_name: Last name
        middle_name: Middle name or initial (optional)
        style: Formatting style ('full', 'last_first', 'initial', 'last_initial')
            Defaults to 'full'.
    
    Returns:
        Formatted name according to the specified style
    """
    # Ensure all name parts are strings and not None
    first_name = str(first_name) if first_name else ""
    last_name = str(last_name) if last_name else ""
    middle_name = str(middle_name) if middle_name else ""
    
    if not style:
        style = 'full'
    
    if style == 'full':
        if middle_name:
            return f"{first_name} {middle_name} {last_name}".strip()
        return f"{first_name} {last_name}".strip()
    
    elif style == 'last_first':
        if middle_name:
            return f"{last_name}, {first_name} {middle_name}".strip()
        return f"{last_name}, {first_name}".strip()
    
    elif style == 'initial':
        first_initial = first_name[0].upper() if first_name else ""
        if middle_name:
            middle_initial = middle_name[0].upper() if middle_name else ""
            return f"{first_initial}. {middle_initial}. {last_name}".strip()
        return f"{first_initial}. {last_name}".strip() if first_initial else last_name
    
    elif style == 'last_initial':
        first_initial = first_name[0].upper() if first_name else ""
        if middle_name:
            middle_initial = middle_name[0].upper() if middle_name else ""
            if first_initial:
                return f"{last_name}, {first_initial}. {middle_initial}.".strip()
            return last_name
        return f"{last_name}, {first_initial}.".strip() if first_initial else last_name
    
    # Default to full name if style not recognized
    if middle_name:
        return f"{first_name} {middle_name} {last_name}".strip()
    return f"{first_name} {last_name}".strip()


def format_phone(phone_number: str, country_code: Optional[str] = None) -> str:
    """
    Formats a phone number according to the specified country code.
    
    Args:
        phone_number: The phone number to format
        country_code: The country code (e.g., 'US', 'UK'). Defaults to 'US'.
    
    Returns:
        Formatted phone number
    """
    if not phone_number:
        return ""
    
    if not country_code:
        country_code = 'US'
    
    country_code = country_code.upper()
    
    # Remove all non-numeric characters
    digits = ''.join(filter(str.isdigit, phone_number))
    
    if not digits:
        return phone_number  # Return original if no digits
    
    if country_code == 'US':
        # Format as (XXX) XXX-XXXX or +1 (XXX) XXX-XXXX
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            # Return original if not matching expected format
            return phone_number
    
    elif country_code == 'UK':
        # Format UK numbers (simplified, not handling all UK number formats)
        if len(digits) == 11 and digits.startswith('0'):
            return f"+44 {digits[1:4]} {digits[4:7]} {digits[7:]}"
        else:
            return phone_number
    
    elif country_code == 'FR':
        # Format French numbers
        if len(digits) == 10 and digits.startswith('0'):
            return f"+33 {digits[1:3]} {digits[3:5]} {digits[5:7]} {digits[7:9]} {digits[9:]}"
        else:
            return phone_number
    
    # Return original if country code not supported
    return phone_number


def format_address(street: str, city: str, state: str, postal_code: str,
                  country: Optional[str] = None) -> str:
    """
    Formats an address according to the specified country's conventions.
    
    Args:
        street: Street address
        city: City
        state: State or region
        postal_code: Postal or ZIP code
        country: Country code (e.g., 'US', 'UK'). Defaults to 'US'.
    
    Returns:
        Formatted address string
    """
    # Ensure all address parts are strings and not None
    street = str(street) if street else ""
    city = str(city) if city else ""
    state = str(state) if state else ""
    postal_code = str(postal_code) if postal_code else ""
    
    if not country:
        country = 'US'
    
    country = country.upper()
    
    if country == 'US':
        # US format: Street, City, State ZIP
        return f"{street}, {city}, {state} {postal_code}".strip(", ")
    
    elif country == 'UK':
        # UK format: Street, City, State, Postal Code
        return f"{street}, {city}, {state}, {postal_code}".strip(", ")
    
    elif country == 'FR':
        # French format: Street, Postal Code City, State
        return f"{street}, {postal_code} {city}, {state}".strip(", ")
    
    elif country == 'DE':
        # German format: Street, Postal Code City, State
        return f"{street}, {postal_code} {city}, {state}".strip(", ")
    
    elif country == 'JP':
        # Japanese format: Postal Code, Prefecture, City, Street
        return f"{postal_code}, {state}, {city}, {street}".strip(", ")
    
    # Default format for other countries
    return f"{street}, {city}, {state}, {postal_code}, {country}".strip(", ")