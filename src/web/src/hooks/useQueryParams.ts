import { useSearchParams } from 'react-router-dom'; // v6.4.0
import { useCallback, useMemo } from 'react'; // v18.0.0

/**
 * Custom hook for working with URL query parameters in a type-safe manner.
 * Designed for use in data tables, analytics views, and other filterable components
 * in the Justice Bid system.
 * 
 * @param defaultParams - Default parameter values to use when URL parameters are not present
 * @returns Object containing parsed parameters and utility functions to manipulate them
 */
function useQueryParams(defaultParams: Record<string, any> = {}) {
  const [searchParams, setSearchParams] = useSearchParams();

  /**
   * Parses a query parameter string to its appropriate type
   * Handles conversion of string parameters to number, boolean, array, or object
   */
  const parseQueryParam = (value: string): any => {
    // Handle empty values
    if (!value) return '';

    // Try to parse as JSON (for arrays and objects)
    try {
      return JSON.parse(value);
    } catch (e) {
      // Not valid JSON, continue with other type checks
    }

    // Handle boolean values
    if (value === 'true') return true;
    if (value === 'false') return false;

    // Handle numeric values
    if (!isNaN(Number(value)) && value.trim() !== '') {
      return Number(value);
    }

    // Default to string
    return value;
  };

  /**
   * Stringifies a parameter value for URL storage
   * Handles arrays and objects by using JSON.stringify
   */
  const stringifyQueryParam = (value: any): string => {
    if (value === null || value === undefined) {
      return '';
    }

    if (typeof value === 'object') {
      return JSON.stringify(value);
    }

    return String(value);
  };

  /**
   * Parse current URL parameters and merge with defaults
   */
  const params = useMemo(() => {
    const result: Record<string, any> = { ...defaultParams };
    
    // Convert URL search params to object with proper type conversion
    Array.from(searchParams.entries()).forEach(([key, value]) => {
      result[key] = parseQueryParam(value);
    });
    
    return result;
  }, [searchParams, defaultParams]);

  /**
   * Sets a single query parameter
   */
  const setParam = useCallback((key: string, value: any) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev);
      
      // Remove the parameter if value is null or undefined
      if (value === null || value === undefined) {
        newParams.delete(key);
      } else {
        newParams.set(key, stringifyQueryParam(value));
      }
      
      return newParams;
    });
  }, [setSearchParams]);

  /**
   * Sets multiple query parameters, replacing all existing ones
   */
  const setParams = useCallback((newParams: Record<string, any>) => {
    const params = new URLSearchParams();
    
    // Add all new parameters
    Object.entries(newParams).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        params.set(key, stringifyQueryParam(value));
      }
    });
    
    setSearchParams(params);
  }, [setSearchParams]);

  /**
   * Merges new parameters with existing ones
   */
  const mergeParams = useCallback((newParams: Record<string, any>) => {
    setSearchParams(prev => {
      const params = new URLSearchParams(prev);
      
      // Update or add new parameters
      Object.entries(newParams).forEach(([key, value]) => {
        if (value === null || value === undefined) {
          params.delete(key);
        } else {
          params.set(key, stringifyQueryParam(value));
        }
      });
      
      return params;
    });
  }, [setSearchParams]);

  /**
   * Removes a specific parameter
   */
  const removeParam = useCallback((key: string) => {
    setSearchParams(prev => {
      const params = new URLSearchParams(prev);
      params.delete(key);
      return params;
    });
  }, [setSearchParams]);

  /**
   * Clears all parameters
   */
  const clearParams = useCallback(() => {
    setSearchParams(new URLSearchParams());
  }, [setSearchParams]);

  return {
    params,
    setParam,
    setParams,
    mergeParams,
    removeParam,
    clearParams
  };
}

export default useQueryParams;