import {
  format,
  parse,
  isValid,
  addDays,
  addMonths,
  addYears,
  differenceInDays,
  differenceInMonths,
  differenceInYears,
  isBefore,
  isAfter,
  isSameDay
} from 'date-fns'; // date-fns v2.29.3

// Constants for date formats
export const DATE_FORMAT = 'yyyy-MM-dd';
export const DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss';
export const DISPLAY_DATE_FORMAT = 'MMM d, yyyy';
export const DISPLAY_DATETIME_FORMAT = 'MMM d, yyyy h:mm a';
export const DEFAULT_LOCALE = 'en-US';

/**
 * Formats a date object or string into a standardized string format
 * @param date - The date to format
 * @param formatStr - The format string to use
 * @param locale - The locale to use for formatting
 * @returns Formatted date string or empty string if input is invalid
 */
export const formatDate = (
  date: Date | string | null | undefined,
  formatStr: string = DATE_FORMAT,
  locale: string = DEFAULT_LOCALE
): string => {
  if (date === null || date === undefined) {
    return '';
  }

  let dateObj: Date;
  if (typeof date === 'string') {
    dateObj = new Date(date);
  } else {
    dateObj = date;
  }

  if (!isValid(dateObj)) {
    return '';
  }

  return format(dateObj, formatStr, { locale: { code: locale } as Locale });
};

/**
 * Formats a date for display using the application's standard display format
 * @param date - The date to format
 * @param locale - The locale to use for formatting
 * @returns Date formatted for display (e.g., 'Mar 15, 2023')
 */
export const formatDisplayDate = (
  date: Date | string | null | undefined,
  locale: string = DEFAULT_LOCALE
): string => {
  return formatDate(date, DISPLAY_DATE_FORMAT, locale);
};

/**
 * Parses a date string into a Date object
 * @param dateStr - The date string to parse
 * @param formatStr - The format of the date string
 * @returns Parsed Date object or null if parsing fails
 */
export const parseDate = (
  dateStr: string | null | undefined,
  formatStr: string = DATE_FORMAT
): Date | null => {
  if (!dateStr) {
    return null;
  }

  try {
    const parsedDate = parse(dateStr, formatStr, new Date());
    return isValid(parsedDate) ? parsedDate : null;
  } catch (error) {
    return null;
  }
};

/**
 * Checks if a value is a valid date
 * @param date - The value to check
 * @returns True if the input is a valid date, false otherwise
 */
export const isValidDate = (date: any): boolean => {
  if (date === null || date === undefined) {
    return false;
  }

  if (date instanceof Date) {
    return isValid(date);
  }

  if (typeof date === 'string') {
    const dateObj = new Date(date);
    return isValid(dateObj);
  }

  return false;
};

/**
 * Calculates the number of days remaining until a target date
 * @param targetDate - The target date
 * @returns Number of days remaining (negative if target date is in the past)
 */
export const calculateDaysRemaining = (targetDate: Date | string): number => {
  const target = typeof targetDate === 'string' ? new Date(targetDate) : targetDate;
  
  // Set current date to midnight to ensure consistent day calculations
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  
  return differenceInDays(target, now);
};

/**
 * Checks if a date falls within a specified date range
 * @param date - The date to check
 * @param startDate - The start of the range
 * @param endDate - The end of the range
 * @returns True if the date is within the range (inclusive), false otherwise
 */
export const isWithinDateRange = (
  date: Date | string,
  startDate: Date | string,
  endDate: Date | string
): boolean => {
  const checkDate = typeof date === 'string' ? new Date(date) : date;
  const start = typeof startDate === 'string' ? new Date(startDate) : startDate;
  const end = typeof endDate === 'string' ? new Date(endDate) : endDate;

  return (isAfter(checkDate, start) || isSameDay(checkDate, start)) && 
         (isBefore(checkDate, end) || isSameDay(checkDate, end));
};

/**
 * Checks if the current date is within a submission window defined by month and day ranges
 * @param startMonth - Starting month (1-12)
 * @param startDay - Starting day of month
 * @param endMonth - Ending month (1-12)
 * @param endDay - Ending day of month
 * @returns True if current date is within the submission window, false otherwise
 */
export const isWithinSubmissionWindow = (
  startMonth: number,
  startDay: number,
  endMonth: number,
  endDay: number
): boolean => {
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  
  // Create start and end dates for the current year
  let startDate = new Date(currentYear, startMonth - 1, startDay);
  let endDate = new Date(currentYear, endMonth - 1, endDay);
  
  // If the end month is before the start month, it spans across year boundary
  if (endMonth < startMonth || (endMonth === startMonth && endDay < startDay)) {
    endDate.setFullYear(currentYear + 1);
  }
  
  return isWithinDateRange(currentDate, startDate, endDate);
};

/**
 * Adds a duration to a date
 * @param date - The base date
 * @param amount - The amount to add
 * @param unit - The unit of time ('days', 'months', or 'years')
 * @returns New date with the duration added
 */
export const addDuration = (
  date: Date | string,
  amount: number,
  unit: 'days' | 'months' | 'years'
): Date => {
  const baseDate = typeof date === 'string' ? new Date(date) : date;
  
  switch (unit) {
    case 'days':
      return addDays(baseDate, amount);
    case 'months':
      return addMonths(baseDate, amount);
    case 'years':
      return addYears(baseDate, amount);
    default:
      return baseDate;
  }
};

/**
 * Calculates the difference between two dates in specified units
 * @param dateA - First date
 * @param dateB - Second date
 * @param unit - The unit of time ('days', 'months', or 'years')
 * @returns Difference between dates in the specified unit
 */
export const getDateDifference = (
  dateA: Date | string,
  dateB: Date | string,
  unit: 'days' | 'months' | 'years'
): number => {
  const firstDate = typeof dateA === 'string' ? new Date(dateA) : dateA;
  const secondDate = typeof dateB === 'string' ? new Date(dateB) : dateB;
  
  switch (unit) {
    case 'days':
      return differenceInDays(firstDate, secondDate);
    case 'months':
      return differenceInMonths(firstDate, secondDate);
    case 'years':
      return differenceInYears(firstDate, secondDate);
    default:
      return 0;
  }
};

/**
 * Checks if a rate is currently in a frozen period based on effective date and freeze period
 * @param effectiveDate - The date the rate became effective
 * @param freezePeriodMonths - The number of months the rate is frozen
 * @returns True if the rate is still in the freeze period, false otherwise
 */
export const isRateFrozen = (
  effectiveDate: Date | string,
  freezePeriodMonths: number
): boolean => {
  const effectiveDateTime = typeof effectiveDate === 'string' ? new Date(effectiveDate) : effectiveDate;
  const freezeEndDate = addMonths(effectiveDateTime, freezePeriodMonths);
  const currentDate = new Date();
  
  return isBefore(currentDate, freezeEndDate);
};

/**
 * Checks if a proposed effective date meets the notice period requirement
 * @param proposedEffectiveDate - The proposed date for the rate to become effective
 * @param noticeRequiredDays - The required notice period in days
 * @returns True if the notice period requirement is met, false otherwise
 */
export const meetsNoticeRequirement = (
  proposedEffectiveDate: Date | string,
  noticeRequiredDays: number
): boolean => {
  const effectiveDate = typeof proposedEffectiveDate === 'string' ? 
    new Date(proposedEffectiveDate) : proposedEffectiveDate;
  
  const currentDate = new Date();
  const minimumEffectiveDate = addDays(currentDate, noticeRequiredDays);
  
  return isAfter(effectiveDate, minimumEffectiveDate) || isSameDay(effectiveDate, minimumEffectiveDate);
};

/**
 * Calculates the earliest allowed effective date based on the notice period requirement
 * @param noticeRequiredDays - The required notice period in days
 * @returns Earliest allowed effective date
 */
export const getEarliestAllowedEffectiveDate = (
  noticeRequiredDays: number
): Date => {
  const currentDate = new Date();
  return addDays(currentDate, noticeRequiredDays);
};

/**
 * Gets the start date of the fiscal year for a given date
 * @param date - The reference date
 * @param fiscalYearStartMonth - The month (1-12) when the fiscal year starts
 * @param fiscalYearStartDay - The day of the month when the fiscal year starts
 * @returns Start date of the fiscal year containing the input date
 */
export const fiscalYearStartDate = (
  date: Date | string,
  fiscalYearStartMonth: number,
  fiscalYearStartDay: number
): Date => {
  const referenceDate = typeof date === 'string' ? new Date(date) : date;
  let year = referenceDate.getFullYear();
  
  // Create fiscal year start date for the same year
  const fiscalStart = new Date(year, fiscalYearStartMonth - 1, fiscalYearStartDay);
  
  // If the reference date is before the fiscal year start in the same year,
  // then it's in the previous fiscal year
  if (isBefore(referenceDate, fiscalStart)) {
    year -= 1;
    return new Date(year, fiscalYearStartMonth - 1, fiscalYearStartDay);
  }
  
  return fiscalStart;
};

/**
 * Gets the end date of the fiscal year for a given date
 * @param date - The reference date
 * @param fiscalYearStartMonth - The month (1-12) when the fiscal year starts
 * @param fiscalYearStartDay - The day of the month when the fiscal year starts
 * @returns End date of the fiscal year containing the input date
 */
export const fiscalYearEndDate = (
  date: Date | string,
  fiscalYearStartMonth: number,
  fiscalYearStartDay: number
): Date => {
  // Get fiscal year start date
  const fyStart = fiscalYearStartDate(date, fiscalYearStartMonth, fiscalYearStartDay);
  
  // Fiscal year end is one day before the start of the next fiscal year
  const nextYearStart = addYears(fyStart, 1);
  return addDays(nextYearStart, -1);
};