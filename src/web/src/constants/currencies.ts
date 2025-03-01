/**
 * Constants and utilities for multi-currency support throughout the application.
 * Supports rate management and analytics features with proper currency
 * formatting and conversion capabilities.
 * 
 * @version 1.0.0
 */

/**
 * Default currency code used when none is specified
 */
export const DEFAULT_CURRENCY = 'USD';

/**
 * Enum of supported currency codes
 */
export enum CurrencyCode {
  USD = 'USD',
  EUR = 'EUR',
  GBP = 'GBP',
  JPY = 'JPY',
  CAD = 'CAD',
}

/**
 * Interface defining the structure of a currency object
 */
export interface Currency {
  code: CurrencyCode;
  name: string;
  symbol: string;
  decimalPlaces: number;
  defaultLocale: string;
}

/**
 * Record of all supported currencies with their properties
 */
export const CURRENCIES: Record<CurrencyCode, Currency> = {
  [CurrencyCode.USD]: {
    code: CurrencyCode.USD,
    name: 'US Dollar',
    symbol: '$',
    decimalPlaces: 2,
    defaultLocale: 'en-US',
  },
  [CurrencyCode.EUR]: {
    code: CurrencyCode.EUR,
    name: 'Euro',
    symbol: '€',
    decimalPlaces: 2,
    defaultLocale: 'fr-FR',
  },
  [CurrencyCode.GBP]: {
    code: CurrencyCode.GBP,
    name: 'British Pound',
    symbol: '£',
    decimalPlaces: 2,
    defaultLocale: 'en-GB',
  },
  [CurrencyCode.JPY]: {
    code: CurrencyCode.JPY,
    name: 'Japanese Yen',
    symbol: '¥',
    decimalPlaces: 0, // JPY typically doesn't use decimal places
    defaultLocale: 'ja-JP',
  },
  [CurrencyCode.CAD]: {
    code: CurrencyCode.CAD,
    name: 'Canadian Dollar',
    symbol: 'CA$',
    decimalPlaces: 2,
    defaultLocale: 'en-CA',
  },
};

/**
 * List of currencies formatted for dropdown components
 */
export const CURRENCY_OPTIONS = Object.values(CURRENCIES).map(currency => ({
  value: currency.code,
  label: `${currency.code} - ${currency.name}`,
}));

/**
 * Formatting rules for currencies based on locale
 */
export const CURRENCY_FORMAT_LOCALE: Record<string, { 
  symbolFirst: boolean; 
  thousandsSeparator: string; 
  decimalSeparator: string;
}> = {
  'en-US': {
    symbolFirst: true,
    thousandsSeparator: ',',
    decimalSeparator: '.',
  },
  'en-GB': {
    symbolFirst: true,
    thousandsSeparator: ',',
    decimalSeparator: '.',
  },
  'fr-FR': {
    symbolFirst: false,
    thousandsSeparator: ' ',
    decimalSeparator: ',',
  },
  'de-DE': {
    symbolFirst: false,
    thousandsSeparator: '.',
    decimalSeparator: ',',
  },
  'ja-JP': {
    symbolFirst: true,
    thousandsSeparator: ',',
    decimalSeparator: '.',
  },
};

/**
 * Helper function that returns the symbol for a given currency code
 * 
 * @param code - The currency code
 * @returns The currency symbol for the given code
 */
export function getCurrencySymbol(code: CurrencyCode): string {
  return CURRENCIES[code]?.symbol || '';
}

/**
 * Helper function to format a number as a currency string based on code and locale
 * 
 * @param amount - The amount to format
 * @param currencyCode - The currency code
 * @param locale - The locale to use for formatting (defaults to currency's default locale)
 * @returns The formatted currency string
 */
export function formatCurrency(amount: number, currencyCode: CurrencyCode, locale?: string): string {
  const currency = CURRENCIES[currencyCode];
  if (!currency) {
    return amount.toString();
  }

  const useLocale = locale || currency.defaultLocale;
  const format = CURRENCY_FORMAT_LOCALE[useLocale] || CURRENCY_FORMAT_LOCALE['en-US'];
  
  // Format the number with appropriate decimals
  const formattedNumber = amount.toFixed(currency.decimalPlaces);
  
  // Split into parts
  const parts = formattedNumber.split('.');
  
  // Format thousands
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, format.thousandsSeparator);
  
  // Join with decimal separator if needed
  const formattedAmount = parts.length > 1 
    ? parts.join(format.decimalSeparator)
    : parts[0];
  
  // Add symbol in correct position
  return format.symbolFirst 
    ? `${currency.symbol}${formattedAmount}`
    : `${formattedAmount} ${currency.symbol}`;
}