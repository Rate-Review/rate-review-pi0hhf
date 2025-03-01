/**
 * Axios Configuration
 * 
 * Configures the Axios HTTP client with defaults, interceptors, and authentication
 * token handling for the Justice Bid application.
 */

import axios, { 
  AxiosInstance, 
  AxiosRequestConfig, 
  AxiosError,
  InternalAxiosRequestConfig,
  AxiosResponse
} from 'axios'; // ^1.4.0

import { API_ROUTES } from './apiRoutes';
import { handleApiError } from './errorHandling';

// Default timeout for API requests in milliseconds
const API_TIMEOUT = 30000;

// Key used to store authentication token in localStorage
const TOKEN_STORAGE_KEY = 'justice_bid_auth_token';

// Default headers to be included with all API requests
const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};

/**
 * Default configuration for Axios instance
 */
const axiosDefaultConfig: AxiosRequestConfig = {
  baseURL: process.env.REACT_APP_API_URL || '/api/v1',
  timeout: API_TIMEOUT,
  headers: DEFAULT_HEADERS
};

/**
 * Configured Axios instance for making API requests
 */
const axiosInstance: AxiosInstance = axios.create(axiosDefaultConfig);

/**
 * Sets the JWT authentication token in local storage and as default header for all API requests
 * @param token - JWT token string
 */
export const setAuthToken = (token: string): void => {
  // Store token in localStorage for persistence across page refreshes
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
  
  // Set Authorization header with Bearer token format for all future API requests
  axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

/**
 * Removes the JWT authentication token from local storage and default headers
 */
export const removeAuthToken = (): void => {
  // Remove token from localStorage
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  
  // Remove Authorization header from default headers
  delete axiosInstance.defaults.headers.common['Authorization'];
};

/**
 * Retrieves the current JWT authentication token from local storage
 * @returns The authentication token or null if not set
 */
export const getAuthToken = (): string | null => {
  // Retrieve token from localStorage
  return localStorage.getItem(TOKEN_STORAGE_KEY);
};

/**
 * Axios request interceptor that adds authentication token to outgoing requests
 * @param config - The Axios request configuration
 * @returns Modified request configuration with auth token
 */
const requestInterceptor = (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  // Get the authentication token from storage
  const token = getAuthToken();
  
  // If a token exists, add it to the Authorization header
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Return the modified config object
  return config;
};

/**
 * Axios response interceptor that processes successful responses
 * @param response - The Axios response object
 * @returns The processed response object
 */
const responseInterceptor = (response: AxiosResponse): AxiosResponse => {
  // Process successful responses
  return response;
};

/**
 * Axios error interceptor that handles error responses
 * @param error - The Axios error object
 * @returns Rejected promise with processed error
 */
const errorInterceptor = (error: AxiosError): Promise<never> => {
  // Process error using handleApiError utility
  return Promise.reject(handleApiError(error));
};

// Add request interceptor
axiosInstance.interceptors.request.use(requestInterceptor);

// Add response interceptors
axiosInstance.interceptors.response.use(responseInterceptor, errorInterceptor);

// Initialize auth token from localStorage if it exists
const token = getAuthToken();
if (token) {
  axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

export default axiosInstance;
export { setAuthToken, removeAuthToken, getAuthToken };