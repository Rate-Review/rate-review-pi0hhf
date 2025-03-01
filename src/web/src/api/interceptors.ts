/**
 * Axios Interceptors Configuration
 *
 * Configures Axios interceptors for request and response handling across the Justice Bid Rate Negotiation System.
 * Implements authentication token management, error handling, and token refresh logic.
 *
 * @version 1.0.0
 */

import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError, // axios v1.4.0
  InternalAxiosRequestConfig
} from 'axios'; // axios v1.4.0
import { handleApiError } from './errorHandling';
import { getStoredAuthToken, setAuthToken, clearAuthToken } from '../utils/storage';
import { refreshAuthToken } from '../services/auth';
import { store } from '../store';

/**
 * Configures and applies request and response interceptors to an Axios instance.
 * @param axiosInstance - The Axios instance to configure.
 */
export const setupInterceptors = (axiosInstance: AxiosInstance): void => {
  // Apply request interceptor to handle authentication and request configuration
  axiosInstance.interceptors.request.use(
    requestInterceptor,
    (error: AxiosError) => Promise.reject(error)
  );

  // Apply response interceptor to handle successful responses
  axiosInstance.interceptors.response.use(
    responseInterceptor,
    errorInterceptor
  );
};

/**
 * Handles outgoing API requests by adding authentication headers and other configurations.
 * @param config - The Axios request configuration.
 * @returns Modified request configuration with auth token and timeout.
 */
export const requestInterceptor = async (config: InternalAxiosRequestConfig): Promise<InternalAxiosRequestConfig> => {
  // Retrieve authentication token from storage
  const token = getStoredAuthToken();

  // Add Authorization header with Bearer token if available
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Set default timeout for the request (30 seconds)
  config.timeout = 30000;

  // Return modified request configuration
  return config;
};

/**
 * Handles successful API responses.
 * @param response - The Axios response object.
 * @returns The processed response.
 */
export const responseInterceptor = async (response: AxiosResponse): Promise<AxiosResponse> => {
  // Return the response data for successful requests
  return response;
};

/**
 * Handles errors from API responses including token refresh for authentication failures.
 * @param error - The Axios error object.
 * @returns Resolved with retried request or rejected with handled error.
 */
export const errorInterceptor = async (error: AxiosError): Promise<any> => {
  // Check if error is due to expired authentication token (401 error)
  if (isTokenExpiredError(error)) {
    try {
      // Attempt to refresh the token
      const newToken = await refreshAuthToken();

      // If token refresh is successful, retry the original request with the new token
      return createRequestRetry(error.config, newToken.token);
    } catch (refreshError) {
      // If token refresh fails, process the error using handleApiError
      return Promise.reject(handleApiError(refreshError as AxiosError));
    }
  }

  // If error is not related to authentication, process the error using handleApiError
  return Promise.reject(handleApiError(error));
};

/**
 * Determines if an error is due to an expired authentication token.
 * @param error - The Axios error object.
 * @returns True if the error is due to an expired token, false otherwise.
 */
export const isTokenExpiredError = (error: AxiosError): boolean => {
  // Check if error status is 401 (Unauthorized)
  if (error.response?.status === 401) {
    // Examine error response for specific token expiration indicators
    const errorMessage = error.response.data?.message;
    return errorMessage === 'Token expired' || errorMessage === 'Invalid token';
  }

  return false;
};

/**
 * Creates a function to retry a failed request with updated configuration.
 * @param config - The original Axios request configuration.
 * @param newToken - The new authentication token.
 * @returns Response from the retried request.
 */
export const createRequestRetry = (config: AxiosRequestConfig | undefined, newToken: string): Promise<AxiosResponse> => {
  if (!config) {
    return Promise.reject(new Error('Original request config is missing'));
  }
  // Create a new request configuration based on the original
  const retryConfig: AxiosRequestConfig = {
    ...config,
    headers: {
      ...config.headers,
      Authorization: `Bearer ${newToken}`, // Update the Authorization header with the new token
    },
  };

  // Execute a new request with the updated configuration
  const axiosInstance = axios.create(); // Create a new axios instance to avoid modifying the default one
  setupInterceptors(axiosInstance); // Apply interceptors to the new instance

  return axiosInstance(retryConfig); // Return the response from the new request
};