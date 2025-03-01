/**
 * Core API service module that provides standardized methods for making HTTP requests
 * to the Justice Bid backend API. It abstracts the underlying HTTP client implementation (Axios)
 * and provides consistent request/response handling, error processing, and retry logic.
 * 
 * @version 1.0.0
 */

import axiosInstance from '../api/axiosConfig';
import { parseErrorResponse, shouldRetryRequest, calculateRetryDelay } from '../api/errorHandling';
import { API_ROUTES, buildUrl, buildUrlWithParams } from '../api/apiRoutes';
import { 
  ApiResponse, 
  ErrorResponse,
  PaginationParams,
  PaginatedResponse,
  SortParams,
  FilterParams
} from '../types/common';
import { 
  AxiosRequestConfig, 
  AxiosResponse,
  AxiosError
} from 'axios'; // ^1.4.0

// Maximum number of retry attempts for failed requests
export const MAX_RETRIES = 3;

/**
 * Core request function that handles all API requests with retries and error handling
 * @param method - HTTP method (GET, POST, PUT, PATCH, DELETE)
 * @param url - API endpoint URL
 * @param data - Request body data (for POST, PUT, PATCH)
 * @param config - Additional Axios request configuration
 * @param retryCount - Current retry attempt count
 * @returns Promise resolving to the API response
 */
async function request(
  method: string,
  url: string,
  data?: any,
  config: AxiosRequestConfig = {},
  retryCount = 0
): Promise<AxiosResponse> {
  // Combine request configuration
  const requestConfig: AxiosRequestConfig = {
    ...config,
    method,
    url,
    data
  };

  try {
    // Make the API request
    const response = await axiosInstance(requestConfig);
    return response;
  } catch (error) {
    // Cast error to AxiosError for type safety
    const axiosError = error as AxiosError;
    
    // Check if we should retry the request
    if (shouldRetryRequest(axiosError, retryCount)) {
      // Calculate delay before retrying
      const delay = calculateRetryDelay(retryCount);
      
      // Wait for the calculated delay
      await new Promise(resolve => setTimeout(resolve, delay));
      
      // Retry the request with incremented retry count
      return request(method, url, data, config, retryCount + 1);
    }
    
    // If we shouldn't retry or have exhausted retries, parse and throw the error
    const parsedError = parseErrorResponse(error);
    throw parsedError;
  }
}

/**
 * Makes a GET request to the specified API endpoint
 * @param url - API endpoint URL
 * @param config - Additional Axios request configuration
 * @returns Promise resolving to the response data
 */
async function get<T = any>(url: string, config: AxiosRequestConfig = {}): Promise<T> {
  const response = await request('GET', url, undefined, config);
  return response.data;
}

/**
 * Makes a POST request to the specified API endpoint
 * @param url - API endpoint URL
 * @param data - Request body data
 * @param config - Additional Axios request configuration
 * @returns Promise resolving to the response data
 */
async function post<T = any>(url: string, data?: any, config: AxiosRequestConfig = {}): Promise<T> {
  const response = await request('POST', url, data, config);
  return response.data;
}

/**
 * Makes a PUT request to the specified API endpoint
 * @param url - API endpoint URL
 * @param data - Request body data
 * @param config - Additional Axios request configuration
 * @returns Promise resolving to the response data
 */
async function put<T = any>(url: string, data?: any, config: AxiosRequestConfig = {}): Promise<T> {
  const response = await request('PUT', url, data, config);
  return response.data;
}

/**
 * Makes a PATCH request to the specified API endpoint
 * @param url - API endpoint URL
 * @param data - Request body data
 * @param config - Additional Axios request configuration
 * @returns Promise resolving to the response data
 */
async function patch<T = any>(url: string, data?: any, config: AxiosRequestConfig = {}): Promise<T> {
  const response = await request('PATCH', url, data, config);
  return response.data;
}

/**
 * Makes a DELETE request to the specified API endpoint
 * @param url - API endpoint URL
 * @param config - Additional Axios request configuration
 * @returns Promise resolving to the response data
 */
async function del<T = any>(url: string, config: AxiosRequestConfig = {}): Promise<T> {
  const response = await request('DELETE', url, undefined, config);
  return response.data;
}

/**
 * Makes a GET request for paginated data with support for pagination, sorting, and filtering
 * @param url - API endpoint URL
 * @param paginationParams - Pagination parameters (page, pageSize)
 * @param sortParams - Optional sorting parameters
 * @param filterParams - Optional filtering parameters
 * @param config - Additional Axios request configuration
 * @returns Promise resolving to paginated response with items and metadata
 */
async function getPaginated<T = any>(
  url: string,
  paginationParams: PaginationParams,
  sortParams?: SortParams,
  filterParams?: FilterParams[],
  config: AxiosRequestConfig = {}
): Promise<PaginatedResponse<T>> {
  // Construct query parameters
  const params: Record<string, any> = {
    page: paginationParams.page,
    pageSize: paginationParams.pageSize
  };

  // Add sort parameters if provided
  if (sortParams) {
    params.sortField = sortParams.field;
    params.sortDirection = sortParams.direction;
  }

  // Add filter parameters if provided
  if (filterParams && filterParams.length > 0) {
    params.filters = JSON.stringify(filterParams);
  }

  // Update request config with params
  const updatedConfig = {
    ...config,
    params
  };

  // Make the request
  return get<PaginatedResponse<T>>(url, updatedConfig);
}

/**
 * Uploads a file to the specified API endpoint with progress tracking
 * @param url - API endpoint URL
 * @param file - File to upload
 * @param additionalData - Additional form data to include with the file
 * @param onProgress - Optional callback for tracking upload progress
 * @returns Promise resolving to the upload response data
 */
async function uploadFile<T = any>(
  url: string,
  file: File,
  additionalData: Record<string, any> = {},
  onProgress?: (progress: number) => void
): Promise<T> {
  // Create form data
  const formData = new FormData();
  formData.append('file', file);

  // Add any additional data to form data
  Object.entries(additionalData).forEach(([key, value]) => {
    formData.append(key, typeof value === 'object' ? JSON.stringify(value) : String(value));
  });

  // Configure request for form data and progress tracking
  const config: AxiosRequestConfig = {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  };

  // Add upload progress tracking if callback provided
  if (onProgress) {
    config.onUploadProgress = (progressEvent) => {
      if (progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentCompleted);
      }
    };
  }

  // Make the upload request
  return post<T>(url, formData, config);
}

/**
 * Downloads a file from the specified API endpoint
 * @param url - API endpoint URL
 * @param filename - Name to save the downloaded file as
 * @param config - Additional Axios request configuration
 * @returns Promise resolving to the file blob
 */
async function downloadFile(
  url: string,
  filename: string,
  config: AxiosRequestConfig = {}
): Promise<Blob> {
  // Configure request for blob response
  const downloadConfig: AxiosRequestConfig = {
    ...config,
    responseType: 'blob'
  };

  // Request the file
  const blob = await get<Blob>(url, downloadConfig);

  // Create a download link and trigger the download
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();

  // Clean up
  link.parentNode?.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);

  return blob;
}

/**
 * API service object providing standardized methods for API communication
 */
export const api = {
  get,
  post,
  put,
  patch,
  delete: del, // Using 'del' for the function name to avoid keyword collision
  getPaginated,
  uploadFile,
  downloadFile,
  buildUrl,
  buildUrlWithParams
};

export { MAX_RETRIES };