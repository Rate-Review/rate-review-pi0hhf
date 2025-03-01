/**
 * Utility functions for form validation, rate validation, and data validation
 * throughout the Justice Bid Rate Negotiation System application.
 * 
 * @version 1.0.0
 */

import { formatCurrency } from '../utils/currency';
import { isValidDateString, parseDate } from '../utils/date';
import { RATE_CONSTANTS } from '../constants/rates';
import { SUPPORTED_CURRENCIES } from '../constants/currencies';
import isEmail from 'validator/lib/isEmail'; // validator v13.7.0

/**
 * Validates that a field has a value (not empty, null or undefined)
 * @param value - Any value to check
 * @returns True if the value is not empty, null or undefined
 */
export function isRequired(value: any): boolean {
  if (value === null || value === undefined) {
    return false;
  }
  
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  
  return true;
}

/**
 * Validates email address format
 * @param email - Email address to validate
 * @returns True if the email is valid
 */
export function validateEmail(email: string): boolean {
  return isEmail(email);
}

/**
 * Validates password strength based on requirements
 * @param password - Password to validate
 * @returns Object containing isValid boolean and error message if invalid
 */
export function validatePassword(password: string): { isValid: boolean; error?: string } {
  // Check minimum length requirement (12 characters)
  if (password.length < 12) {
    return {
      isValid: false,
      error: 'Password must be at least 12 characters long'
    };
  }
  
  // Check complexity requirements (3 of 4 character types)
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumbers = /[0-9]/.test(password);
  const hasSymbols = /[^A-Za-z0-9]/.test(password);
  
  const complexityCount = [hasUppercase, hasLowercase, hasNumbers, hasSymbols]
    .filter(Boolean).length;
  
  if (complexityCount < 3) {
    return {
      isValid: false,
      error: 'Password must contain at least 3 of the following: uppercase letters, lowercase letters, numbers, and symbols'
    };
  }
  
  return { isValid: true };
}

/**
 * Validates that a rate increase is within allowed percentage
 * @param currentRate - Current rate amount
 * @param proposedRate - Proposed rate amount
 * @param maxIncreasePercentage - Maximum allowed increase percentage (optional)
 * @returns Object containing isValid boolean and error message if invalid
 */
export function validateRateIncrease(
  currentRate: number,
  proposedRate: number,
  maxIncreasePercentage?: number
): { isValid: boolean; error?: string } {
  if (currentRate <= 0) {
    return {
      isValid: false,
      error: 'Current rate must be greater than zero'
    };
  }
  
  if (proposedRate <= 0) {
    return {
      isValid: false,
      error: 'Proposed rate must be greater than zero'
    };
  }
  
  // Calculate percentage increase
  const percentageIncrease = ((proposedRate - currentRate) / currentRate) * 100;
  
  // If no increase or decrease, it's valid
  if (percentageIncrease <= 0) {
    return { isValid: true };
  }
  
  // Use provided max increase or fall back to constant
  const maxAllowed = maxIncreasePercentage !== undefined 
    ? maxIncreasePercentage 
    : RATE_CONSTANTS.MAX_RATE_INCREASE_PERCENTAGE;
  
  if (percentageIncrease > maxAllowed) {
    const formattedCurrent = formatCurrency(currentRate, 'USD');
    const formattedProposed = formatCurrency(proposedRate, 'USD');
    
    return {
      isValid: false,
      error: `Rate increase of ${percentageIncrease.toFixed(2)}% exceeds maximum allowed increase of ${maxAllowed}%. (${formattedCurrent} to ${formattedProposed})`
    };
  }
  
  return { isValid: true };
}

/**
 * Validates that a date range is valid (end date is after start date)
 * @param startDate - Start date string
 * @param endDate - End date string
 * @returns Object containing isValid boolean and error message if invalid
 */
export function validateDateRange(
  startDate: string,
  endDate: string
): { isValid: boolean; error?: string } {
  // Check if both dates are valid
  if (!isValidDateString(startDate)) {
    return {
      isValid: false,
      error: 'Start date is invalid'
    };
  }
  
  if (!isValidDateString(endDate)) {
    return {
      isValid: false,
      error: 'End date is invalid'
    };
  }
  
  // Parse dates
  const start = parseDate(startDate);
  const end = parseDate(endDate);
  
  if (!start || !end) {
    return {
      isValid: false,
      error: 'Unable to parse date values'
    };
  }
  
  // Validate end date is after start date
  if (end <= start) {
    return {
      isValid: false,
      error: 'End date must be after start date'
    };
  }
  
  return { isValid: true };
}

/**
 * Validates that an effective date meets the notice period requirement
 * @param effectiveDate - Effective date string to validate
 * @param noticePeriodDays - Required notice period in days
 * @returns Object containing isValid boolean and error message if invalid
 */
export function validateEffectiveDate(
  effectiveDate: string,
  noticePeriodDays: number
): { isValid: boolean; error?: string } {
  if (!isValidDateString(effectiveDate)) {
    return {
      isValid: false,
      error: 'Effective date is invalid'
    };
  }
  
  const effective = parseDate(effectiveDate);
  
  if (!effective) {
    return {
      isValid: false,
      error: 'Unable to parse effective date'
    };
  }
  
  // Calculate minimum allowed effective date
  const today = new Date();
  const minEffectiveDate = new Date();
  minEffectiveDate.setDate(today.getDate() + noticePeriodDays);
  
  // Set times to midnight for proper comparison
  effective.setHours(0, 0, 0, 0);
  minEffectiveDate.setHours(0, 0, 0, 0);
  
  if (effective < minEffectiveDate) {
    return {
      isValid: false,
      error: `Effective date must be at least ${noticePeriodDays} days from today`
    };
  }
  
  return { isValid: true };
}

/**
 * Validates that a currency code is supported by the system
 * @param currencyCode - Currency code to validate
 * @returns True if the currency code is supported
 */
export function validateCurrency(currencyCode: string): boolean {
  return SUPPORTED_CURRENCIES.includes(currencyCode);
}

/**
 * Validates that a value is a number or can be parsed as a number
 * @param value - Value to validate
 * @returns True if the value is numeric
 */
export function validateNumeric(value: any): boolean {
  if (typeof value === 'number') {
    return !isNaN(value) && isFinite(value);
  }
  
  if (typeof value === 'string') {
    // Remove commas and other formatting characters and try parsing
    const cleanedValue = value.replace(/,/g, '').replace(/\s/g, '');
    const num = parseFloat(cleanedValue);
    return !isNaN(num) && isFinite(num);
  }
  
  return false;
}

/**
 * Validates that a value is a positive number
 * @param value - Value to validate
 * @returns True if the value is a positive number
 */
export function validatePositiveNumber(value: any): boolean {
  if (!validateNumeric(value)) {
    return false;
  }
  
  const num = typeof value === 'string' ? parseFloat(value.replace(/,/g, '')) : value;
  return num > 0;
}

/**
 * Validates an entire rate submission against client rate rules
 * @param submission - Rate submission data
 * @param rateRules - Client rate rules
 * @returns Object containing overall validity and specific validation errors
 */
export function validateRateSubmission(
  submission: any,
  rateRules: any
): { isValid: boolean; errors: Record<string, string[]> } {
  const errors: Record<string, string[]> = {};
  
  // Validate rate freeze period compliance
  if (rateRules.freezePeriod && submission.rates && submission.rates.length > 0) {
    const freezeViolations = submission.rates.filter((rate: any) => {
      // Check if any existing rates are still in freeze period
      if (rate.currentRate && rate.lastEffectiveDate) {
        const lastEffective = parseDate(rate.lastEffectiveDate);
        if (lastEffective) {
          const freezeEndDate = new Date(lastEffective);
          freezeEndDate.setMonth(freezeEndDate.getMonth() + rateRules.freezePeriod);
          
          const today = new Date();
          return today < freezeEndDate;
        }
      }
      return false;
    });
    
    if (freezeViolations.length > 0) {
      errors.freezePeriod = freezeViolations.map((rate: any) => 
        `Rate for ${rate.attorneyName || 'attorney'} is still in ${rateRules.freezePeriod}-month freeze period`
      );
    }
  }
  
  // Validate notice period compliance
  if (rateRules.noticeRequired && submission.effectiveDate) {
    const noticeResult = validateEffectiveDate(
      submission.effectiveDate,
      rateRules.noticeRequired
    );
    
    if (!noticeResult.isValid) {
      errors.noticePeriod = [noticeResult.error || 'Notice period requirement not met'];
    }
  }
  
  // Validate maximum rate increase compliance
  if (rateRules.maxIncreasePercent && submission.rates && submission.rates.length > 0) {
    const increaseViolations = submission.rates
      .filter((rate: any) => rate.currentRate && rate.proposedRate)
      .map((rate: any) => {
        const result = validateRateIncrease(
          rate.currentRate,
          rate.proposedRate,
          rateRules.maxIncreasePercent
        );
        
        return {
          rate,
          result
        };
      })
      .filter(item => !item.result.isValid);
    
    if (increaseViolations.length > 0) {
      errors.rateIncrease = increaseViolations.map(item => 
        `${item.rate.attorneyName || 'Attorney'}: ${item.result.error}`
      );
    }
  }
  
  // Validate submission window compliance if applicable
  if (rateRules.submissionWindow) {
    const { startMonth, startDay, endMonth, endDay } = rateRules.submissionWindow;
    
    // Check if current date is within submission window
    const today = new Date();
    const currentYear = today.getFullYear();
    
    let startDate = new Date(currentYear, startMonth - 1, startDay);
    let endDate = new Date(currentYear, endMonth - 1, endDay);
    
    // Handle case where submission window spans year boundary (e.g., Nov to Feb)
    if (endMonth < startMonth || (endMonth === startMonth && endDay < startDay)) {
      if (today < startDate) {
        // We're in the early part of the year, endDate is this year, startDate is prev year
        startDate.setFullYear(currentYear - 1);
      } else {
        // We're in the later part of the year, endDate is next year
        endDate.setFullYear(currentYear + 1);
      }
    }
    
    // Check if today is outside submission window
    if (today < startDate || today > endDate) {
      const formatter = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' });
      const formattedStart = formatter.format(startDate);
      const formattedEnd = formatter.format(endDate);
      
      errors.submissionWindow = [
        `Rates can only be submitted during the window of ${formattedStart} - ${formattedEnd}`
      ];
    }
  }
  
  // Determine overall validity
  const isValid = Object.keys(errors).length === 0;
  
  return {
    isValid,
    errors
  };
}

/**
 * Creates a validator function with a specific validation rule
 * @param validationFn - Function that performs the validation
 * @param errorMessage - Error message if validation fails
 * @returns A function that returns null if valid or an error message if invalid
 */
export function createValidator(
  validationFn: (value: any) => boolean,
  errorMessage: string
): (value: any) => string | null {
  return (value: any) => {
    return validationFn(value) ? null : errorMessage;
  };
}