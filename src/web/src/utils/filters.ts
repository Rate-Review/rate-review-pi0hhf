/**
 * Utility functions for filtering data in the Justice Bid application.
 * Provides flexible, type-safe filtering capabilities for rates, negotiations,
 * analytics, and other data types.
 * 
 * @version 1.0.0
 */

import { Rate, RateStatus } from '../types/rate';
import { Negotiation, NegotiationStatus } from '../types/negotiation';
import { Attorney } from '../types/attorney';
import { Organization } from '../types/organization';
import { formatCurrency } from './currency';
import { formatDate } from './date';
import isEqual from 'lodash/isEqual';

/**
 * Creates a type-safe filter function based on criteria object
 * @param criteria - Object with properties and their expected values
 * @returns A filter function that can be used with Array.filter()
 */
export function createFilterFunction<T>(criteria: Partial<T>): (item: T) => boolean {
  return (item: T) => {
    // Check if all criteria match
    for (const [key, value] of Object.entries(criteria)) {
      if (value === undefined || value === null) {
        continue; // Skip undefined or null criteria
      }

      const itemValue = item[key as keyof T];
      
      // Handle arrays
      if (Array.isArray(value)) {
        if (value.length === 0) {
          continue; // Skip empty array criteria
        }
        
        // If item value is an array, check if any value matches
        if (Array.isArray(itemValue)) {
          if (!value.some(v => itemValue.includes(v))) {
            return false;
          }
          continue;
        }
        
        // If item value is not an array, check if value includes item value
        if (!value.includes(itemValue)) {
          return false;
        }
        continue;
      }
      
      // Handle objects
      if (typeof value === 'object' && value !== null) {
        if (!isEqual(itemValue, value)) {
          return false;
        }
        continue;
      }
      
      // Handle date strings
      if (
        typeof value === 'string' && 
        typeof itemValue === 'string' && 
        (value.match(/^\d{4}-\d{2}-\d{2}/) || itemValue.match(/^\d{4}-\d{2}-\d{2}/))
      ) {
        const valueDate = new Date(value).setHours(0, 0, 0, 0);
        const itemDate = new Date(itemValue).setHours(0, 0, 0, 0);
        if (valueDate !== itemDate) {
          return false;
        }
        continue;
      }
      
      // Handle regular values
      if (itemValue !== value) {
        return false;
      }
    }
    
    return true;
  };
}

/**
 * Filters an array of rates based on provided criteria
 * @param rates - Array of rates to filter
 * @param filterCriteria - Criteria to filter by
 * @returns Filtered array of rates
 */
export function filterRates(rates: Rate[], filterCriteria: Partial<Rate>): Rate[] {
  const filterFn = createFilterFunction<Rate>(filterCriteria);
  return rates.filter(filterFn);
}

/**
 * Filters an array of negotiations based on provided criteria
 * @param negotiations - Array of negotiations to filter
 * @param filterCriteria - Criteria to filter by
 * @returns Filtered array of negotiations
 */
export function filterNegotiations(
  negotiations: Negotiation[], 
  filterCriteria: Partial<Negotiation>
): Negotiation[] {
  const filterFn = createFilterFunction<Negotiation>(filterCriteria);
  return negotiations.filter(filterFn);
}

/**
 * Filters an array of attorneys based on provided criteria
 * @param attorneys - Array of attorneys to filter
 * @param filterCriteria - Criteria to filter by
 * @returns Filtered array of attorneys
 */
export function filterAttorneys(
  attorneys: Attorney[], 
  filterCriteria: Partial<Attorney>
): Attorney[] {
  const filterFn = createFilterFunction<Attorney>(filterCriteria);
  return attorneys.filter(filterFn);
}

/**
 * Filters an array of organizations based on provided criteria
 * @param organizations - Array of organizations to filter
 * @param filterCriteria - Criteria to filter by
 * @returns Filtered array of organizations
 */
export function filterOrganizations(
  organizations: Organization[], 
  filterCriteria: Partial<Organization>
): Organization[] {
  const filterFn = createFilterFunction<Organization>(filterCriteria);
  return organizations.filter(filterFn);
}

/**
 * Creates a filter function for number ranges
 * @param min - Minimum value (inclusive)
 * @param max - Maximum value (inclusive)
 * @returns A filter function that checks if a value is within the specified range
 */
export function createRangeFilter(min?: number, max?: number): (value: number) => boolean {
  return (value: number) => {
    if (min !== undefined && value < min) {
      return false;
    }
    if (max !== undefined && value > max) {
      return false;
    }
    return true;
  };
}

/**
 * Creates a filter function for date ranges
 * @param startDate - Start date (inclusive)
 * @param endDate - End date (inclusive)
 * @returns A filter function that checks if a date is within the specified range
 */
export function createDateRangeFilter(
  startDate?: Date, 
  endDate?: Date
): (date: Date | string) => boolean {
  return (date: Date | string) => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    // Set time to midnight for consistent comparison
    const dateValue = new Date(dateObj).setHours(0, 0, 0, 0);
    
    if (startDate !== undefined) {
      const startValue = new Date(startDate).setHours(0, 0, 0, 0);
      if (dateValue < startValue) {
        return false;
      }
    }
    
    if (endDate !== undefined) {
      const endValue = new Date(endDate).setHours(0, 0, 0, 0);
      if (dateValue > endValue) {
        return false;
      }
    }
    
    return true;
  };
}

/**
 * Creates a filter function for multi-select values
 * @param selectedValues - Array of selected values
 * @returns A filter function that checks if a value is in the selected values
 */
export function createMultiSelectFilter<T>(selectedValues: T[]): (value: T) => boolean {
  // If no values are selected, don't filter
  if (selectedValues.length === 0) {
    return () => true;
  }
  
  return (value: T) => selectedValues.includes(value);
}

/**
 * Creates a filter function for text search
 * @param searchText - Text to search for
 * @param caseSensitive - Whether the search should be case sensitive
 * @returns A filter function that checks if a string contains the search text
 */
export function createTextFilter(
  searchText: string, 
  caseSensitive: boolean = false
): (text: string) => boolean {
  // If search text is empty, don't filter
  if (!searchText || searchText.trim() === '') {
    return () => true;
  }
  
  const processedSearchText = caseSensitive ? searchText : searchText.toLowerCase();
  
  return (text: string) => {
    if (!text) {
      return false;
    }
    
    const processedText = caseSensitive ? text : text.toLowerCase();
    return processedText.includes(processedSearchText);
  };
}

/**
 * Generic function to apply multiple filters to an array of items
 * @param items - Array of items to filter
 * @param filters - Array of filter functions to apply
 * @returns Filtered array of items
 */
export function applyFilters<T>(items: T[], filters: ((item: T) => boolean)[]): T[] {
  return items.filter(item => filters.every(filter => filter(item)));
}

/**
 * Extracts unique values from an array of objects for use as filter options
 * @param items - Array of items
 * @param property - Property name to extract values from
 * @returns Array of unique values for the specified property
 */
export function getFilterOptions<T, K extends keyof T>(
  items: T[], 
  property: K
): T[K][] {
  const values = items.map(item => item[property]);
  
  // Filter out duplicates and null/undefined values
  return [...new Set(values)].filter(value => value !== null && value !== undefined) as T[K][];
}

/**
 * Creates a URL query parameter string from filter criteria
 * @param filterCriteria - Filter criteria object
 * @returns Encoded query parameter string
 */
export function createFilterParam(filterCriteria: Record<string, any>): string {
  const params = new URLSearchParams();
  
  for (const [key, value] of Object.entries(filterCriteria)) {
    if (value === null || value === undefined) {
      continue;
    }
    
    // Handle arrays and objects by JSON stringifying them
    if (typeof value === 'object') {
      params.append(key, JSON.stringify(value));
    } else {
      params.append(key, String(value));
    }
  }
  
  return params.toString();
}

/**
 * Parses a URL query parameter string back into filter criteria
 * @param paramString - URL query parameter string
 * @returns Filter criteria object
 */
export function parseFilterParam(paramString: string): Record<string, any> {
  const params = new URLSearchParams(paramString);
  const filterCriteria: Record<string, any> = {};
  
  params.forEach((value, key) => {
    // Try to parse JSON values
    try {
      if (value.startsWith('[') || value.startsWith('{')) {
        filterCriteria[key] = JSON.parse(value);
      } else {
        filterCriteria[key] = value;
      }
    } catch {
      // If parsing fails, use the raw string value
      filterCriteria[key] = value;
    }
  });
  
  return filterCriteria;
}