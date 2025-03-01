/**
 * Centralized error handling for API requests in the Justice Bid application.
 * This module provides utilities for parsing error responses, categorizing errors,
 * determining retry strategies, and generating user-friendly error messages.
 */

import axios, { AxiosError } from 'axios';
import { isAxiosError } from 'axios';
import { ErrorType, ErrorResponse } from '../types/common';

/**
 * Maximum number of retry attempts for failed requests
 */
export const MAX_RETRY_ATTEMPTS = 3;

/**
 * Base delay in milliseconds for retry backoff calculation
 * @private
 */
const BASE_RETRY_DELAY_MS = 300;

/**
 * Maximum delay in milliseconds for retry backoff
 * @private
 */
const MAX_RETRY_DELAY_MS = 10000;

/**
 * Parses error responses from various formats into a standardized ErrorResponse structure
 * @param error - The original error object from any source
 * @returns A standardized error response object
 */
export function parseErrorResponse(error: unknown): ErrorResponse {
  if (isAxiosError(error)) {
    // Handle Axios errors which may contain response data
    if (error.response?.data) {
      const responseData = error.response.data;
      
      // Handle JSON:API error format
      if (responseData.errors && Array.isArray(responseData.errors)) {
        const firstError = responseData.errors[0];
        return {
          code: firstError.code || String(error.response.status),
          message: firstError.title || firstError.detail || error.message,
          details: firstError.source ? { source: firstError.source } : undefined
        };
      }
      
      // Handle standard REST API error format
      if (responseData.error || responseData.message) {
        return {
          code: responseData.code || responseData.error?.code || String(error.response.status),
          message: responseData.message || responseData.error?.message || error.message,
          details: responseData.details || responseData.error?.details
        };
      }
      
      // Handle simple string error message
      if (typeof responseData === 'string') {
        return {
          code: String(error.response.status),
          message: responseData
        };
      }
    }
    
    // Handle network errors (no response)
    if (isNetworkError(error)) {
      return {
        code: 'NETWORK_ERROR',
        message: 'Network error occurred. Please check your connection and try again.'
      };
    }
    
    // Default Axios error handling
    return {
      code: error.response ? String(error.response.status) : error.code || 'UNKNOWN_ERROR',
      message: error.message || 'An unknown error occurred'
    };
  }
  
  // Handle non-Axios errors
  if (error instanceof Error) {
    return {
      code: 'UNKNOWN_ERROR',
      message: error.message || 'An unknown error occurred'
    };
  }
  
  // Handle completely unknown errors
  return {
    code: 'UNKNOWN_ERROR',
    message: typeof error === 'string' ? error : 'An unknown error occurred'
  };
}

/**
 * Determines if an error is related to network connectivity issues
 * @param error - The error to check
 * @returns True if it's a network error, false otherwise
 */
export function isNetworkError(error: unknown): boolean {
  if (isAxiosError(error)) {
    // Check for specific network error codes
    if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
      return true;
    }
    
    // Check if response is not present (indicating network failure)
    if (!error.response) {
      return true;
    }
    
    // Check for network-related message content
    const networkErrorTerms = [
      'network error',
      'network timeout',
      'connection refused',
      'internet',
      'timeout',
      'cors',
      'socket'
    ];
    
    const errorMessage = error.message.toLowerCase();
    return networkErrorTerms.some(term => errorMessage.includes(term));
  }
  
  // For non-Axios errors, check message if available
  if (error instanceof Error) {
    const errorMessage = error.message.toLowerCase();
    return errorMessage.includes('network') || 
           errorMessage.includes('connection') ||
           errorMessage.includes('timeout') ||
           errorMessage.includes('internet');
  }
  
  return false;
}

/**
 * Determines if a failed request should be retried based on error type and retry count
 * @param error - The Axios error from a failed request
 * @param retryCount - The current retry attempt count
 * @returns True if the request should be retried, false otherwise
 */
export function shouldRetryRequest(error: AxiosError, retryCount: number): boolean {
  // Don't retry if we've exceeded maximum attempts
  if (retryCount >= MAX_RETRY_ATTEMPTS) {
    return false;
  }
  
  // Retry network errors
  if (isNetworkError(error)) {
    return true;
  }
  
  // Retry specific status codes
  if (error.response) {
    const status = error.response.status;
    
    // Retry on request timeout or rate limiting
    if (status === 408 || status === 429) {
      return true;
    }
    
    // Retry on server errors (5xx)
    if (status >= 500 && status < 600) {
      return true;
    }
  }
  
  return false;
}

/**
 * Categorizes errors into specific error types for consistent handling
 * @param error - The error object to categorize
 * @returns Categorized error type from the ErrorType enum
 */
export function getErrorType(error: AxiosError | Error): ErrorType {
  // First, check for network errors
  if (isNetworkError(error)) {
    return ErrorType.NETWORK_ERROR;
  }
  
  // Then check for Axios errors with response status
  if (isAxiosError(error) && error.response) {
    const status = error.response.status;
    
    // Categorize based on status code
    if (status === 400) {
      return ErrorType.VALIDATION_ERROR;
    } else if (status === 401) {
      return ErrorType.AUTHENTICATION_ERROR;
    } else if (status === 403) {
      return ErrorType.AUTHORIZATION_ERROR;
    } else if (status === 404) {
      return ErrorType.NOT_FOUND_ERROR;
    } else if (status >= 500) {
      return ErrorType.SERVER_ERROR;
    }
  }
  
  // Default to server error for uncategorized errors
  return ErrorType.SERVER_ERROR;
}

/**
 * Generates a user-friendly error message based on the error type and details
 * @param error - The standardized error response
 * @returns User-friendly error message for display
 */
export function getErrorMessage(error: ErrorResponse): string {
  // If we have a specific user-friendly message, use it
  if (error.message && !error.message.includes('unknown error')) {
    return error.message;
  }
  
  // Generate messages based on error code or type
  switch (error.code) {
    case 'NETWORK_ERROR':
      return 'Unable to connect to the server. Please check your internet connection and try again.';
    
    case '400':
      if (error.details && typeof error.details === 'object') {
        // Handle validation errors with field details
        const fields = Object.keys(error.details);
        if (fields.length) {
          const fieldErrors = fields.map(field => {
            const message = error.details?.[field];
            return `${field}: ${message}`;
          }).join('; ');
          
          return `Validation error: ${fieldErrors}`;
        }
      }
      return 'The request contains invalid data. Please check your inputs and try again.';
    
    case '401':
      return 'You are not authenticated. Please log in and try again.';
    
    case '403':
      return 'You do not have permission to perform this action.';
    
    case '404':
      return 'The requested resource was not found.';
    
    case '429':
      return 'Too many requests. Please wait a moment before trying again.';
    
    default:
      // Handle 5xx errors
      if (error.code.startsWith('5')) {
        return 'A server error occurred. Please try again later or contact support if the problem persists.';
      }
      
      // Default message
      return error.message || 'An unexpected error occurred. Please try again.';
  }
}

/**
 * Calculates exponential backoff delay with jitter for retrying failed requests
 * @param retryCount - The current retry attempt count
 * @returns Delay in milliseconds before retrying
 */
export function calculateRetryDelay(retryCount: number): number {
  // Calculate base delay using exponential backoff: 2^retryCount * baseMs
  const baseDelay = Math.pow(2, retryCount) * BASE_RETRY_DELAY_MS;
  
  // Add random jitter (±30%) to prevent synchronized retry storms
  const jitterFactor = 0.7 + Math.random() * 0.6; // Random value between 0.7 and 1.3
  const delay = baseDelay * jitterFactor;
  
  // Cap the maximum delay
  return Math.min(delay, MAX_RETRY_DELAY_MS);
}