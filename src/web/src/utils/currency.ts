/**
 * Utility functions for handling currency operations including formatting, 
 * conversion, and validation. Supports the multi-currency requirement of
 * the Justice Bid Rate Negotiation System.
 * 
 * @version 1.0.0
 */

import { CurrencyCode } from '../types';
import { 
  CURRENCY_SYMBOLS, 
  CURRENCY_DECIMAL_PLACES,
  DEFAULT_CURRENCY 
} from '../constants';
import { api } from '../services/api';

// Cache for exchange rates with expiration
interface ExchangeRatesCache {
  rates: Record<string, number>;
  timestamp: number;
  baseCurrency: CurrencyCode;
}

let exchangeRatesCache: ExchangeRatesCache | null = null;
const CACHE_EXPIRATION_TIME = 3600000; // 1 hour in milliseconds

/**
 * Formats a number as a currency string with the appropriate symbol and decimal places
 * 
 * @param amount - The amount to format
 * @param currencyCode - The currency code to use for formatting
 * @param options - Optional formatting options
 * @returns Formatted currency string with symbol and proper decimal places
 */
export function formatCurrency(
  amount: number,
  currencyCode: CurrencyCode,
  options: { includeSymbol?: boolean; locale?: string } = {}
): string {
  const symbol = CURRENCY_SYMBOLS[currencyCode] || '';
  const decimalPlaces = CURRENCY_DECIMAL_PLACES[currencyCode] || 2;
  
  // Apply default options
  const { includeSymbol = true, locale = 'en-US' } = options;
  
  // Format the number using Intl.NumberFormat for locale-aware formatting
  const formatter = new Intl.NumberFormat(locale, {
    minimumFractionDigits: decimalPlaces,
    maximumFractionDigits: decimalPlaces
  });
  
  const formattedAmount = formatter.format(amount);
  
  // Add the currency symbol if requested
  return includeSymbol ? `${symbol}${formattedAmount}` : formattedAmount;
}

/**
 * Parses a currency string input into a number value
 * 
 * @param input - The currency string to parse
 * @param currencyCode - The currency code to use for parsing
 * @returns Parsed number value from the currency input string
 */
export function parseCurrencyInput(input: string, currencyCode: CurrencyCode): number {
  // Get the currency symbol
  const symbol = CURRENCY_SYMBOLS[currencyCode] || '';
  
  // Remove currency symbol and any non-numeric characters except decimal separator
  let cleanedInput = input.replace(symbol, '').trim();
  
  // Handle different decimal separators based on locale
  // For simplicity, we accept both dots and commas as decimal separators
  const hasCommaDecimal = cleanedInput.indexOf(',') > -1 && 
                         (cleanedInput.indexOf('.') === -1 || 
                          cleanedInput.indexOf(',') < cleanedInput.indexOf('.'));
  
  if (hasCommaDecimal) {
    // Replace comma with dot for proper parsing
    cleanedInput = cleanedInput.replace(/\./g, '').replace(',', '.');
  } else {
    // Remove all commas (thousand separators) and keep dots
    cleanedInput = cleanedInput.replace(/,/g, '');
  }
  
  // Remove any remaining non-numeric characters except the decimal point
  cleanedInput = cleanedInput.replace(/[^\d.-]/g, '');
  
  // Parse the cleaned string to a number
  const parsedValue = parseFloat(cleanedInput);
  
  // Return 0 if parsing failed
  return isNaN(parsedValue) ? 0 : parsedValue;
}

/**
 * Converts an amount from one currency to another using exchange rates
 * 
 * @param amount - The amount to convert
 * @param fromCurrency - Source currency code
 * @param toCurrency - Target currency code
 * @param exchangeRates - Object containing exchange rates
 * @returns Converted amount in the target currency
 */
export function convertCurrency(
  amount: number,
  fromCurrency: CurrencyCode,
  toCurrency: CurrencyCode,
  exchangeRates: Record<string, number>
): number {
  // If currencies are the same, no conversion needed
  if (fromCurrency === toCurrency) {
    return amount;
  }
  
  // Get exchange rate
  const exchangeRate = calculateExchangeRate(fromCurrency, toCurrency, exchangeRates);
  
  if (!exchangeRate) {
    throw new Error(`Exchange rate not available for conversion from ${fromCurrency} to ${toCurrency}`);
  }
  
  // Convert amount using exchange rate
  const convertedAmount = amount * exchangeRate;
  
  // Return with proper precision based on target currency
  const decimalPlaces = CURRENCY_DECIMAL_PLACES[toCurrency] || 2;
  const factor = Math.pow(10, decimalPlaces);
  return Math.round(convertedAmount * factor) / factor;
}

/**
 * Fetches current exchange rates from the API and caches them
 * 
 * @param baseCurrency - The base currency for exchange rates
 * @returns Promise resolving to object containing exchange rates
 */
export async function getExchangeRates(
  baseCurrency: CurrencyCode = DEFAULT_CURRENCY as CurrencyCode
): Promise<Record<string, number>> {
  // Check if cached exchange rates exist and are not expired
  const currentTime = Date.now();
  if (
    exchangeRatesCache &&
    exchangeRatesCache.baseCurrency === baseCurrency &&
    currentTime - exchangeRatesCache.timestamp < CACHE_EXPIRATION_TIME
  ) {
    return exchangeRatesCache.rates;
  }
  
  // Fetch fresh exchange rates from API
  try {
    const response = await api.getExchangeRates(baseCurrency);
    
    // Cache the response
    exchangeRatesCache = {
      rates: response,
      timestamp: currentTime,
      baseCurrency
    };
    
    return response;
  } catch (error) {
    // If API call fails and we have expired cache, return it with a console warning
    if (exchangeRatesCache) {
      console.warn('Failed to fetch exchange rates, using expired cache.');
      return exchangeRatesCache.rates;
    }
    
    // Otherwise, rethrow the error
    throw error;
  }
}

/**
 * Validates if a string is a valid currency code
 * 
 * @param code - The currency code to validate
 * @returns True if the code is a valid currency code, false otherwise
 */
export function isValidCurrencyCode(code: string): boolean {
  return Object.values(CurrencyCode).includes(code as CurrencyCode);
}

/**
 * Gets the symbol for a given currency code
 * 
 * @param currencyCode - The currency code
 * @returns Currency symbol for the given currency code
 */
export function getSymbolForCurrency(currencyCode: CurrencyCode): string {
  return CURRENCY_SYMBOLS[currencyCode] || '$'; // Default to $ if not found
}

/**
 * Gets the number of decimal places for a given currency code
 * 
 * @param currencyCode - The currency code
 * @returns Number of decimal places for the given currency code
 */
export function getDecimalPlacesForCurrency(currencyCode: CurrencyCode): number {
  return CURRENCY_DECIMAL_PLACES[currencyCode] || 2; // Default to 2 if not found
}

/**
 * Compares two currency values after converting to the same currency
 * 
 * @param amount1 - First amount
 * @param currency1 - Currency code for first amount
 * @param amount2 - Second amount
 * @param currency2 - Currency code for second amount
 * @param exchangeRates - Object containing exchange rates
 * @returns Comparison result: negative if amount1 < amount2, positive if amount1 > amount2, 0 if equal
 */
export function compareCurrencyValues(
  amount1: number,
  currency1: CurrencyCode,
  amount2: number,
  currency2: CurrencyCode,
  exchangeRates: Record<string, number>
): number {
  // If currencies are the same, directly compare amounts
  if (currency1 === currency2) {
    return amount1 - amount2;
  }
  
  // Convert both to a common currency (using the default currency)
  const commonCurrency = DEFAULT_CURRENCY as CurrencyCode;
  
  const convertedAmount1 = convertCurrency(amount1, currency1, commonCurrency, exchangeRates);
  const convertedAmount2 = convertCurrency(amount2, currency2, commonCurrency, exchangeRates);
  
  // Compare the converted amounts
  return convertedAmount1 - convertedAmount2;
}

/**
 * Calculates the exchange rate between two currencies
 * 
 * @param fromCurrency - Source currency code
 * @param toCurrency - Target currency code
 * @param exchangeRates - Object containing exchange rates
 * @returns Exchange rate from the source currency to the target currency
 */
export function calculateExchangeRate(
  fromCurrency: CurrencyCode,
  toCurrency: CurrencyCode,
  exchangeRates: Record<string, number>
): number {
  // If currencies are the same, rate is 1
  if (fromCurrency === toCurrency) {
    return 1;
  }
  
  // If the exchangeRates are based on fromCurrency, get the direct rate
  if (exchangeRates[toCurrency]) {
    return exchangeRates[toCurrency];
  }
  
  // If the exchangeRates are based on toCurrency, get the inverse rate
  if (exchangeRates[fromCurrency]) {
    return 1 / exchangeRates[fromCurrency];
  }
  
  // If neither direct mapping exists, convert through base currency (usually USD)
  const baseCurrency = Object.keys(exchangeRates)[0];
  
  if (exchangeRates[fromCurrency] && exchangeRates[toCurrency]) {
    // Calculate cross rate
    return exchangeRates[toCurrency] / exchangeRates[fromCurrency];
  }
  
  throw new Error(`Exchange rate not available for conversion from ${fromCurrency} to ${toCurrency}`);
}