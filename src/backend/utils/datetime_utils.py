"""
Utility module providing date and time manipulation, validation, and formatting functions
to support various date-related operations across the Justice Bid Rate Negotiation System,
particularly for rate effective dates, submission deadlines, and analytics date ranges.
"""

from datetime import datetime, date, timedelta
import calendar
from dateutil.relativedelta import relativedelta
from dateutil import parser
import pytz
from typing import List, Optional, Union, Tuple

# Date and time format constants
DEFAULT_DATE_FORMAT = "%Y-%m-%d"  # YYYY-MM-DD
SUPPORTED_DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"  # YYYY-MM-DD HH:MM:SS

# Month names for formatting and display
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", "December"]
SHORT_MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Fiscal quarter definitions (quarter number: (start_month, end_month))
FISCAL_QUARTERS = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}


def get_current_date() -> date:
    """
    Returns the current date.
    
    Returns:
        date: Current date object
    """
    return date.today()


def get_current_datetime(timezone: Optional[str] = None) -> datetime:
    """
    Returns the current datetime, optionally with timezone.
    
    Args:
        timezone: Optional timezone string (e.g., 'UTC', 'America/New_York')
    
    Returns:
        datetime: Current datetime object
    """
    if timezone is None:
        return datetime.now()
    
    tz = pytz.timezone(timezone)
    return datetime.now(tz)


def parse_date(date_string: str, date_format: Optional[str] = None) -> date:
    """
    Parses a date string into a date object using flexible parsing.
    
    Args:
        date_string: String representation of a date
        date_format: Optional format string for datetime.strptime
    
    Returns:
        date: Parsed date object
    
    Raises:
        ValueError: If the date string cannot be parsed
    """
    try:
        if date_format:
            parsed_date = datetime.strptime(date_string, date_format).date()
        else:
            # Try flexible parsing
            parsed_date = parser.parse(date_string).date()
        
        return parsed_date
    except (ValueError, TypeError) as e:
        valid_formats = DEFAULT_DATE_FORMAT if date_format else ", ".join(fmt for fmt in SUPPORTED_DATE_FORMATS)
        raise ValueError(f"Could not parse date '{date_string}'. Expected format: {valid_formats}") from e


def parse_datetime(datetime_string: str, datetime_format: Optional[str] = None, 
                  timezone: Optional[str] = None) -> datetime:
    """
    Parses a datetime string into a datetime object.
    
    Args:
        datetime_string: String representation of a datetime
        datetime_format: Optional format string for datetime.strptime
        timezone: Optional timezone string to apply to the parsed datetime
    
    Returns:
        datetime: Parsed datetime object
    
    Raises:
        ValueError: If the datetime string cannot be parsed
    """
    try:
        if datetime_format:
            parsed_datetime = datetime.strptime(datetime_string, datetime_format)
        else:
            # Try flexible parsing
            parsed_datetime = parser.parse(datetime_string)
        
        if timezone:
            tz = pytz.timezone(timezone)
            if parsed_datetime.tzinfo is None:
                parsed_datetime = tz.localize(parsed_datetime)
            else:
                parsed_datetime = parsed_datetime.astimezone(tz)
                
        return parsed_datetime
    except (ValueError, TypeError) as e:
        valid_format = datetime_format if datetime_format else DEFAULT_DATETIME_FORMAT
        raise ValueError(f"Could not parse datetime '{datetime_string}'. Expected format: {valid_format}") from e


def format_date(date_obj: Union[date, datetime], date_format: Optional[str] = None) -> str:
    """
    Formats a date object into a string using the specified format.
    
    Args:
        date_obj: Date or datetime object to format
        date_format: Optional format string for strftime (default: DEFAULT_DATE_FORMAT)
    
    Returns:
        str: Formatted date string
    """
    # If date_obj is a datetime, extract the date part
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    if date_format is None:
        date_format = DEFAULT_DATE_FORMAT
    
    return date_obj.strftime(date_format)


def format_datetime(datetime_obj: datetime, datetime_format: Optional[str] = None) -> str:
    """
    Formats a datetime object into a string using the specified format.
    
    Args:
        datetime_obj: Datetime object to format
        datetime_format: Optional format string for strftime (default: DEFAULT_DATETIME_FORMAT)
    
    Returns:
        str: Formatted datetime string
    """
    if datetime_format is None:
        datetime_format = DEFAULT_DATETIME_FORMAT
    
    return datetime_obj.strftime(datetime_format)


def is_valid_date_format(date_string: str, date_format: Optional[str] = None) -> bool:
    """
    Checks if a string is in a valid date format.
    
    Args:
        date_string: String to check
        date_format: Optional format to validate against
    
    Returns:
        bool: True if the string is in a valid date format, False otherwise
    """
    try:
        parse_date(date_string, date_format)
        return True
    except ValueError:
        return False


def add_days(date_obj: Union[date, datetime], days: int) -> Union[date, datetime]:
    """
    Adds a specified number of days to a date.
    
    Args:
        date_obj: Date or datetime object
        days: Number of days to add (can be negative)
    
    Returns:
        Union[date, datetime]: A new date with the days added
    """
    return date_obj + timedelta(days=days)


def add_months(date_obj: Union[date, datetime], months: int) -> Union[date, datetime]:
    """
    Adds a specified number of months to a date.
    
    Args:
        date_obj: Date or datetime object
        months: Number of months to add (can be negative)
    
    Returns:
        Union[date, datetime]: A new date with the months added
    """
    return date_obj + relativedelta(months=months)


def add_years(date_obj: Union[date, datetime], years: int) -> Union[date, datetime]:
    """
    Adds a specified number of years to a date.
    
    Args:
        date_obj: Date or datetime object
        years: Number of years to add (can be negative)
    
    Returns:
        Union[date, datetime]: A new date with the years added
    """
    return date_obj + relativedelta(years=years)


def get_first_day_of_month(date_obj: Union[date, datetime]) -> date:
    """
    Gets the first day of the month for a given date.
    
    Args:
        date_obj: Date or datetime object
    
    Returns:
        date: The first day of the month
    """
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    return date(date_obj.year, date_obj.month, 1)


def get_last_day_of_month(date_obj: Union[date, datetime]) -> date:
    """
    Gets the last day of the month for a given date.
    
    Args:
        date_obj: Date or datetime object
    
    Returns:
        date: The last day of the month
    """
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    month = date_obj.month
    year = date_obj.year
    last_day = calendar.monthrange(year, month)[1]
    
    return date(year, month, last_day)


def date_diff_days(start_date: Union[date, datetime], end_date: Union[date, datetime]) -> int:
    """
    Calculates the difference in days between two dates.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        int: The number of days between the dates
    """
    # Extract date part if either is a datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    return (end_date - start_date).days


def date_diff_months(start_date: Union[date, datetime], end_date: Union[date, datetime]) -> int:
    """
    Calculates the difference in months between two dates.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        int: The number of months between the dates
    """
    # Extract date part if either is a datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    r = relativedelta(end_date, start_date)
    return r.years * 12 + r.months


def date_diff_years(start_date: Union[date, datetime], end_date: Union[date, datetime]) -> int:
    """
    Calculates the difference in years between two dates.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        int: The number of years between the dates
    """
    # Extract date part if either is a datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    return relativedelta(end_date, start_date).years


def is_date_between(date_obj: Union[date, datetime], 
                   start_date: Union[date, datetime], 
                   end_date: Union[date, datetime],
                   inclusive: bool = True) -> bool:
    """
    Checks if a date is between two other dates, inclusive or exclusive.
    
    Args:
        date_obj: Date to check
        start_date: Start date of the range
        end_date: End date of the range
        inclusive: Whether the range is inclusive of start and end dates
    
    Returns:
        bool: True if the date is between start_date and end_date, False otherwise
    """
    # Extract date part if any are datetimes
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    if inclusive:
        return start_date <= date_obj <= end_date
    else:
        return start_date < date_obj < end_date


def get_date_range(start_date: Union[date, datetime], 
                  end_date: Union[date, datetime], 
                  step_days: Optional[int] = None) -> List[date]:
    """
    Generates a list of dates between start_date and end_date.
    
    Args:
        start_date: Start date of the range
        end_date: End date of the range
        step_days: Optional step size in days (default: 1)
    
    Returns:
        List[date]: List of dates in the range
    """
    # Extract date part if either is a datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    if step_days is None:
        step_days = 1
    
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date = add_days(current_date, step_days)
    
    return dates


def get_month_range(start_date: Union[date, datetime], 
                   end_date: Union[date, datetime]) -> List[date]:
    """
    Generates a list of first days of months between start_date and end_date.
    
    Args:
        start_date: Start date of the range
        end_date: End date of the range
    
    Returns:
        List[date]: List of first days of months in the range
    """
    # Extract date part if either is a datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # Get the first day of the start month
    current_date = get_first_day_of_month(start_date)
    
    months = []
    
    while current_date <= end_date:
        months.append(current_date)
        current_date = add_months(current_date, 1)
    
    return months


def get_fiscal_quarter(date_obj: Union[date, datetime]) -> int:
    """
    Gets the fiscal quarter number for a date.
    
    Args:
        date_obj: Date object
    
    Returns:
        int: The fiscal quarter (1-4)
    """
    month = date_obj.month if isinstance(date_obj, date) else date_obj.date().month
    
    for quarter, (start_month, end_month) in FISCAL_QUARTERS.items():
        if start_month <= month <= end_month:
            return quarter
    
    # Should never reach here with standard quarters
    return 0


def get_quarter_start_date(date_obj: Union[date, datetime]) -> date:
    """
    Gets the start date of the fiscal quarter for a date.
    
    Args:
        date_obj: Date object
    
    Returns:
        date: The first day of the quarter
    """
    year = date_obj.year if isinstance(date_obj, date) else date_obj.date().year
    quarter = get_fiscal_quarter(date_obj)
    start_month = FISCAL_QUARTERS[quarter][0]
    
    return date(year, start_month, 1)


def get_quarter_end_date(date_obj: Union[date, datetime]) -> date:
    """
    Gets the end date of the fiscal quarter for a date.
    
    Args:
        date_obj: Date object
    
    Returns:
        date: The last day of the quarter
    """
    year = date_obj.year if isinstance(date_obj, date) else date_obj.date().year
    quarter = get_fiscal_quarter(date_obj)
    end_month = FISCAL_QUARTERS[quarter][1]
    
    # Get the last day of the end month
    month_end = get_last_day_of_month(date(year, end_month, 1))
    
    return month_end


def get_fiscal_year_start(date_obj: Union[date, datetime]) -> date:
    """
    Gets the start date of the fiscal year for a date.
    
    Args:
        date_obj: Date object
    
    Returns:
        date: The first day of the fiscal year
    """
    year = date_obj.year if isinstance(date_obj, date) else date_obj.date().year
    return date(year, 1, 1)


def get_fiscal_year_end(date_obj: Union[date, datetime]) -> date:
    """
    Gets the end date of the fiscal year for a date.
    
    Args:
        date_obj: Date object
    
    Returns:
        date: The last day of the fiscal year
    """
    year = date_obj.year if isinstance(date_obj, date) else date_obj.date().year
    return date(year, 12, 31)


def is_same_day(date1: Union[date, datetime], date2: Union[date, datetime]) -> bool:
    """
    Checks if two dates represent the same day.
    
    Args:
        date1: First date
        date2: Second date
    
    Returns:
        bool: True if the dates represent the same day, False otherwise
    """
    # Extract date part if either is a datetime
    if isinstance(date1, datetime):
        date1 = date1.date()
    if isinstance(date2, datetime):
        date2 = date2.date()
    
    return date1.year == date2.year and date1.month == date2.month and date1.day == date2.day


def get_date_format_for_locale(locale: str) -> str:
    """
    Returns the appropriate date format for a locale.
    
    Args:
        locale: Locale string (e.g., 'en-US', 'en-GB', 'fr-FR')
    
    Returns:
        str: The date format string for the locale
    """
    locale_formats = {
        'en-US': '%m/%d/%Y',  # MM/DD/YYYY
        'en-GB': '%d/%m/%Y',  # DD/MM/YYYY
        'fr-FR': '%d/%m/%Y',  # DD/MM/YYYY
        'de-DE': '%d.%m.%Y',  # DD.MM.YYYY
        'ja-JP': '%Y/%m/%d',  # YYYY/MM/DD
    }
    
    return locale_formats.get(locale, DEFAULT_DATE_FORMAT)


def get_days_until(target_date: Union[date, datetime]) -> int:
    """
    Calculates the number of days until a target date.
    
    Args:
        target_date: Target date
    
    Returns:
        int: The number of days until the target date
    """
    current_date = get_current_date()
    
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    
    return date_diff_days(current_date, target_date)


def get_next_business_day(date_obj: Union[date, datetime]) -> date:
    """
    Gets the next business day (skipping weekends) after a date.
    
    Args:
        date_obj: Date object
    
    Returns:
        date: The next business day
    """
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    next_day = add_days(date_obj, 1)
    
    # Check if the next day is a weekend (5=Saturday, 6=Sunday)
    weekday = next_day.weekday()
    
    if weekday == 5:  # Saturday
        next_day = add_days(next_day, 2)  # Skip to Monday
    elif weekday == 6:  # Sunday
        next_day = add_days(next_day, 1)  # Skip to Monday
    
    return next_day


def get_business_days_between(start_date: Union[date, datetime], 
                             end_date: Union[date, datetime]) -> int:
    """
    Calculates the number of business days between two dates.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        int: The number of business days between the dates
    """
    # Extract date part if either is a datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # Make sure start_date is before end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Check if current_date is a business day (weekday 0-4, Monday to Friday)
        if current_date.weekday() < 5:
            business_days += 1
        
        current_date = add_days(current_date, 1)
    
    return business_days


def is_leap_year(year: int) -> bool:
    """
    Checks if a year is a leap year.
    
    Args:
        year: Year to check
    
    Returns:
        bool: True if the year is a leap year, False otherwise
    """
    # Leap year is divisible by a 4 but not by 100, unless also divisible by 400
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def is_business_day(date_obj: Union[date, datetime]) -> bool:
    """
    Checks if a date is a business day (Monday-Friday).
    
    Args:
        date_obj: Date object
    
    Returns:
        bool: True if the date is a business day, False otherwise
    """
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    # Weekday returns 0-6 (Monday-Sunday)
    return date_obj.weekday() < 5