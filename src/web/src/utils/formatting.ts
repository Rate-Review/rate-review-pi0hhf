/**
 * Utility functions for formatting various data types for display in the
 * Justice Bid Rate Negotiation System.
 * 
 * @version 1.0.0
 */

import numeral from 'numeral'; // numeral: ^2.0.6
import dayjs from 'dayjs'; // dayjs: ^1.11.7
import { CURRENCIES, CurrencyCode } from '../constants/currencies';

/**
 * Formats a numeric value as currency with the appropriate symbol and decimal places
 * 
 * @param value - The number to format
 * @param currencyCode - The currency code (e.g., USD, EUR)
 * @param options - Formatting options
 * @returns Formatted currency string with symbol and correct decimal places
 */
export function formatCurrency(
  value: number,
  currencyCode: string = 'USD',
  options: {
    showSymbol?: boolean;
    minimumFractionDigits?: number;
    maximumFractionDigits?: number;
    placeholder?: string;
  } = {}
): string {
  const {
    showSymbol = true,
    minimumFractionDigits,
    maximumFractionDigits,
    placeholder = '-',
  } = options;

  if (value === null || value === undefined || isNaN(value)) {
    return placeholder;
  }

  // Get currency information
  const currency = CURRENCIES[currencyCode as CurrencyCode];
  const symbol = showSymbol ? (currency?.symbol || '$') : '';
  
  // Determine decimal places based on currency or options
  const decimalPlaces = maximumFractionDigits !== undefined
    ? maximumFractionDigits
    : currency?.decimalPlaces || 2;
  
  // Format number with numeral
  const format = `0,0.${Array(decimalPlaces + 1).join('0')}`;
  const formattedValue = numeral(value).format(format);
  
  // Determine symbol position based on currency's locale
  const symbolFirst = !currency?.defaultLocale || 
    ['en-US', 'en-GB', 'ja-JP'].includes(currency.defaultLocale);
  
  return symbolFirst
    ? `${symbol}${formattedValue}`
    : `${formattedValue} ${symbol}`;
}

/**
 * Formats a numeric value as a percentage with the % symbol
 * 
 * @param value - The number to format (e.g., 0.05 for 5%)
 * @param options - Formatting options
 * @returns Formatted percentage string
 */
export function formatPercentage(
  value: number,
  options: {
    showSymbol?: boolean;
    minimumFractionDigits?: number;
    maximumFractionDigits?: number;
    placeholder?: string;
  } = {}
): string {
  const {
    showSymbol = true,
    minimumFractionDigits = 1,
    maximumFractionDigits = 1,
    placeholder = '-',
  } = options;

  if (value === null || value === undefined || isNaN(value)) {
    return placeholder;
  }

  // Convert decimal to percentage (e.g., 0.05 -> 5)
  const percentValue = value * 100;
  
  // Format with numeral
  const format = `0,0.${Array(maximumFractionDigits + 1).join('0')}`;
  const formattedValue = numeral(percentValue).format(format);
  
  // Add percentage symbol if requested
  return showSymbol ? `${formattedValue}%` : formattedValue;
}

/**
 * Formats a numeric value with thousand separators and decimal places
 * 
 * @param value - The number to format
 * @param options - Formatting options
 * @returns Formatted number string
 */
export function formatNumber(
  value: number,
  options: {
    decimalPlaces?: number;
    useGrouping?: boolean;
    placeholder?: string;
  } = {}
): string {
  const {
    decimalPlaces = 0,
    useGrouping = true,
    placeholder = '-',
  } = options;

  if (value === null || value === undefined || isNaN(value)) {
    return placeholder;
  }

  // Format with numeral
  const format = useGrouping 
    ? `0,0${decimalPlaces > 0 ? `.${Array(decimalPlaces + 1).join('0')}` : ''}`
    : `0${decimalPlaces > 0 ? `.${Array(decimalPlaces + 1).join('0')}` : ''}`;
  
  return numeral(value).format(format);
}

/**
 * Formats a number in compact notation (e.g., 1.2M, 5.3K)
 * 
 * @param value - The number to format
 * @param options - Formatting options
 * @returns Compact number representation
 */
export function formatCompactNumber(
  value: number,
  options: {
    maxDecimalPlaces?: number;
    placeholder?: string;
  } = {}
): string {
  const {
    maxDecimalPlaces = 1,
    placeholder = '-',
  } = options;

  if (value === null || value === undefined || isNaN(value)) {
    return placeholder;
  }

  const absValue = Math.abs(value);
  
  // Determine the appropriate suffix based on magnitude
  let suffix = '';
  let divider = 1;
  
  if (absValue >= 1_000_000_000) {
    suffix = 'B';
    divider = 1_000_000_000;
  } else if (absValue >= 1_000_000) {
    suffix = 'M';
    divider = 1_000_000;
  } else if (absValue >= 1_000) {
    suffix = 'K';
    divider = 1_000;
  }
  
  // No need for compact format for small numbers
  if (divider === 1) {
    return formatNumber(value, { decimalPlaces: maxDecimalPlaces });
  }
  
  // Format the number with the appropriate decimal places
  const compactValue = value / divider;
  const format = `0,0.${Array(maxDecimalPlaces + 1).join('0')}`;
  
  return `${numeral(compactValue).format(format)}${suffix}`;
}

/**
 * Formats a date object or string into a specified date format
 * 
 * @param date - The date to format
 * @param format - The format string (defaults to 'MM/DD/YYYY')
 * @returns Formatted date string
 */
export function formatDate(
  date: Date | string | number,
  format: string = 'MM/DD/YYYY'
): string {
  if (!date) {
    return '-';
  }
  
  return dayjs(date).format(format);
}

/**
 * Formats a rate change value with appropriate styling indicators (positive/negative)
 * 
 * @param currentRate - The current rate value
 * @param proposedRate - The proposed rate value
 * @param options - Formatting options
 * @returns Formatted rate change with value and indicator
 */
export function formatRateChange(
  currentRate: number,
  proposedRate: number,
  options: {
    includeSymbol?: boolean;
    colorCode?: boolean;
    decimalPlaces?: number;
  } = {}
): { 
  value: string; 
  indicator: 'positive' | 'negative' | 'neutral';
  color?: string;
} {
  const {
    includeSymbol = true,
    colorCode = false,
    decimalPlaces = 1,
  } = options;

  if (
    currentRate === null || 
    currentRate === undefined || 
    isNaN(currentRate) ||
    proposedRate === null || 
    proposedRate === undefined || 
    isNaN(proposedRate) ||
    currentRate === 0
  ) {
    return {
      value: '-',
      indicator: 'neutral'
    };
  }

  // Calculate the percentage change
  const changePercent = ((proposedRate - currentRate) / currentRate) * 100;
  
  // Determine the change indicator
  const indicator: 'positive' | 'negative' | 'neutral' = 
    changePercent > 0 ? 'positive' : 
    changePercent < 0 ? 'negative' : 'neutral';
  
  // Format the percentage
  const formattedValue = formatPercentage(changePercent / 100, {
    showSymbol: includeSymbol,
    maximumFractionDigits: decimalPlaces,
    minimumFractionDigits: decimalPlaces,
  });
  
  // Determine color if requested
  const color = colorCode 
    ? indicator === 'positive' 
      ? '#38A169' // Green
      : indicator === 'negative' 
        ? '#E53E3E' // Red
        : undefined 
    : undefined;
  
  return {
    value: indicator === 'positive' ? `+${formattedValue}` : formattedValue,
    indicator,
    ...(color ? { color } : {})
  };
}

/**
 * Truncates text to a specified length with ellipsis
 * 
 * @param text - The text to truncate
 * @param maxLength - Maximum length before truncation
 * @param options - Truncation options
 * @returns Truncated text string
 */
export function truncateText(
  text: string,
  maxLength: number,
  options: {
    ellipsisChar?: string;
    position?: 'end' | 'middle' | 'start';
  } = {}
): string {
  const {
    ellipsisChar = '...',
    position = 'end',
  } = options;

  if (!text || text.length <= maxLength) {
    return text || '';
  }
  
  const ellipsisLength = ellipsisChar.length;
  
  if (position === 'middle') {
    const charsToShow = maxLength - ellipsisLength;
    const frontChars = Math.ceil(charsToShow / 2);
    const backChars = Math.floor(charsToShow / 2);
    
    return text.substr(0, frontChars) + ellipsisChar + text.substr(text.length - backChars);
  } else if (position === 'start') {
    return ellipsisChar + text.substr(-(maxLength - ellipsisLength));
  } else {
    // Default: 'end'
    return text.substr(0, maxLength - ellipsisLength) + ellipsisChar;
  }
}

/**
 * Converts camelCase or snake_case text to Title Case
 * 
 * @param text - The text to convert
 * @returns Title Case text
 */
export function camelToTitle(text: string): string {
  if (!text) return '';
  
  // Handle snake_case first
  const spacedText = text.replace(/_/g, ' ');
  
  // Then handle camelCase by adding spaces before capital letters
  const withSpaces = spacedText.replace(/([A-Z])/g, ' $1');
  
  // Split into words, capitalize first letter, and join
  return withSpaces
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
    .trim();
}