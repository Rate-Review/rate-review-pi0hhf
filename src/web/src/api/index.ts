/**
 * Main entry point for the API module that exports all API-related functionality,
 * providing a centralized interface for making API calls, handling errors, and
 * configuring API behavior for the Justice Bid Rate Negotiation System.
 */

import { API_ROUTES } from './apiRoutes';
import { handleApiError } from './errorHandling';
import axiosInstance from './axiosConfig';
import { setupInterceptors } from './interceptors';
import { setupMockServiceWorker } from './mockServiceWorker';
import queryClient from './queryClient';

/**
 * Initializes the API configuration, sets up interceptors, and optionally initializes
 * mock service worker for development and testing.
 * @param enableMocks - Boolean to enable or disable mock service worker
 */
export function initializeApi(enableMocks?: boolean): void {
  // LD1: Call setupInterceptors to configure request and response interceptors
  setupInterceptors(axiosInstance);

  // LD1: If enableMocks is true, call setupMockServiceWorker to initialize mock service worker
  if (enableMocks) {
    setupMockServiceWorker();
  }

  // LD1: Configure any global API settings
  // For example, setting a default error handler or base URL
}

// IE3: Export API endpoint routes for use in services
export { API_ROUTES };

// IE3: Export error handling function for standardized API error processing
export { handleApiError };

// IE3: Export configured Axios instance for making API requests
export { axiosInstance };

// IE3: Export function to set up request and response interceptors
export { setupInterceptors };

// IE3: Export function to initialize mock service worker for development and testing
export { setupMockServiceWorker };

// IE3: Export configured React Query client for data fetching and caching
export { queryClient };

// IE3: Export function to initialize API configurations, interceptors, and optional mocks
export { initializeApi };