/**
 * Attorney Service
 * 
 * This service handles attorney-related API requests and data management,
 * providing functions to interact with the attorney endpoints of the backend API.
 */

import axios from 'axios'; // ^1.4.0
import { API_ROUTES, buildUrl, buildUrlWithParams } from '../api/apiRoutes';
import axiosInstance from '../api/axiosConfig';
import { 
  Attorney, 
  AttorneyPerformance, 
  CreateAttorneyDto as CreateAttorneyRequest,
  UpdateAttorneyDto as UpdateAttorneyRequest,
  AttorneySearchParams as AttorneyFilters
} from '../types/attorney';
import { PaginatedResponse } from '../types/common';

/**
 * Fetches a list of attorneys with optional filtering and pagination
 * 
 * @param filters - Filtering criteria for attorneys
 * @param paginationParams - Pagination parameters (page, limit)
 * @returns Promise resolving to paginated list of attorneys
 */
export const getAttorneys = async (
  filters?: AttorneyFilters,
  paginationParams?: { page?: number; limit?: number }
): Promise<PaginatedResponse<Attorney>> => {
  // Construct query parameters
  const queryParams = new URLSearchParams();
  
  // Add filters if provided
  if (filters) {
    if (filters.organizationId) queryParams.append('organizationId', filters.organizationId);
    if (filters.name) queryParams.append('name', filters.name);
    if (filters.staffClassId) queryParams.append('staffClassId', filters.staffClassId);
    if (filters.practiceArea) queryParams.append('practiceArea', filters.practiceArea);
    if (filters.officeId) queryParams.append('officeId', filters.officeId);
  }
  
  // Add pagination if provided
  if (paginationParams) {
    if (paginationParams.page) queryParams.append('page', paginationParams.page.toString());
    if (paginationParams.limit) queryParams.append('limit', paginationParams.limit.toString());
  }
  
  // Make request with query parameters
  const url = `${buildUrl(API_ROUTES.ATTORNEYS.BASE)}?${queryParams.toString()}`;
  const response = await axiosInstance.get<PaginatedResponse<Attorney>>(url);
  return response.data;
};

/**
 * Fetches a single attorney by ID
 * 
 * @param id - The ID of the attorney to fetch
 * @returns Promise resolving to attorney data
 */
export const getAttorneyById = async (id: string): Promise<Attorney> => {
  const url = buildUrlWithParams(API_ROUTES.ATTORNEYS.BY_ID, { id });
  const response = await axiosInstance.get<Attorney>(url);
  return response.data;
};

/**
 * Creates a new attorney
 * 
 * @param attorneyData - Data for the attorney to create
 * @returns Promise resolving to the newly created attorney
 */
export const createAttorney = async (attorneyData: CreateAttorneyRequest): Promise<Attorney> => {
  const url = buildUrl(API_ROUTES.ATTORNEYS.BASE);
  const response = await axiosInstance.post<Attorney>(url, attorneyData);
  return response.data;
};

/**
 * Updates an existing attorney
 * 
 * @param id - The ID of the attorney to update
 * @param attorneyData - Updated attorney data
 * @returns Promise resolving to the updated attorney
 */
export const updateAttorney = async (
  id: string, 
  attorneyData: UpdateAttorneyRequest
): Promise<Attorney> => {
  const url = buildUrlWithParams(API_ROUTES.ATTORNEYS.BY_ID, { id });
  const response = await axiosInstance.put<Attorney>(url, attorneyData);
  return response.data;
};

/**
 * Deletes an attorney by ID
 * 
 * @param id - The ID of the attorney to delete
 * @returns Promise resolving on successful deletion
 */
export const deleteAttorney = async (id: string): Promise<void> => {
  const url = buildUrlWithParams(API_ROUTES.ATTORNEYS.BY_ID, { id });
  await axiosInstance.delete(url);
};

/**
 * Fetches performance data for an attorney from UniCourt and internal sources
 * 
 * @param id - The ID of the attorney to get performance data for
 * @returns Promise resolving to attorney performance metrics
 */
export const getAttorneyPerformance = async (id: string): Promise<AttorneyPerformance> => {
  const url = buildUrlWithParams(API_ROUTES.ATTORNEYS.PERFORMANCE, { id });
  const response = await axiosInstance.get<AttorneyPerformance>(url);
  return response.data;
};

/**
 * Searches for attorneys by name, bar date, or other criteria
 * 
 * @param searchTerm - Text to search for in attorney names or other fields
 * @param filters - Additional filtering criteria
 * @param paginationParams - Pagination parameters
 * @returns Promise resolving to paginated list of matching attorneys
 */
export const searchAttorneys = async (
  searchTerm: string,
  filters?: AttorneyFilters,
  paginationParams?: { page?: number; limit?: number }
): Promise<PaginatedResponse<Attorney>> => {
  // Construct query parameters
  const queryParams = new URLSearchParams();
  queryParams.append('q', searchTerm);
  
  // Add filters if provided
  if (filters) {
    if (filters.organizationId) queryParams.append('organizationId', filters.organizationId);
    if (filters.staffClassId) queryParams.append('staffClassId', filters.staffClassId);
    if (filters.practiceArea) queryParams.append('practiceArea', filters.practiceArea);
    if (filters.officeId) queryParams.append('officeId', filters.officeId);
  }
  
  // Add pagination if provided
  if (paginationParams) {
    if (paginationParams.page) queryParams.append('page', paginationParams.page.toString());
    if (paginationParams.limit) queryParams.append('limit', paginationParams.limit.toString());
  }
  
  // Make request with query parameters
  const url = `${buildUrl(API_ROUTES.ATTORNEYS.BASE)}/search?${queryParams.toString()}`;
  const response = await axiosInstance.get<PaginatedResponse<Attorney>>(url);
  return response.data;
};

/**
 * Fetches rates for a specific attorney
 * 
 * @param id - The ID of the attorney
 * @param filters - Optional filters for rate data (e.g., effective dates, status)
 * @returns Promise resolving to array of rate records
 */
export const getAttorneyRates = async (
  id: string,
  filters?: object
): Promise<Array<object>> => {
  // Construct query parameters for filters
  const queryParams = new URLSearchParams();
  
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      queryParams.append(key, String(value));
    });
  }
  
  const url = `${buildUrlWithParams(API_ROUTES.ATTORNEYS.BY_ID, { id })}/rates?${queryParams.toString()}`;
  const response = await axiosInstance.get<Array<object>>(url);
  return response.data;
};

/**
 * Imports multiple attorneys from a data source
 * 
 * @param attorneysData - Array of attorney data to import
 * @returns Promise resolving to import results summary
 */
export const bulkImportAttorneys = async (
  attorneysData: Array<CreateAttorneyRequest>
): Promise<{ success: number; failed: number; errors: Array<object> }> => {
  const url = `${buildUrl(API_ROUTES.ATTORNEYS.BASE)}/bulk-import`;
  const response = await axiosInstance.post<{ success: number; failed: number; errors: Array<object> }>(
    url,
    { attorneys: attorneysData }
  );
  return response.data;
};

/**
 * Maps an attorney to a UniCourt attorney record
 * 
 * @param attorneyId - The ID of the attorney to map
 * @param unicourtId - The UniCourt ID to map to
 * @returns Promise resolving to updated attorney with UniCourt mapping
 */
export const mapUniCourtAttorney = async (
  attorneyId: string,
  unicourtId: string
): Promise<Attorney> => {
  const url = buildUrl(API_ROUTES.INTEGRATIONS.UNICOURT.MAPPING);
  const response = await axiosInstance.post<Attorney>(url, {
    attorneyId,
    unicourtId
  });
  return response.data;
};

/**
 * Fetches attorneys filtered by staff class
 * 
 * @param staffClassId - The ID of the staff class to filter by
 * @param paginationParams - Pagination parameters
 * @returns Promise resolving to paginated list of attorneys in the staff class
 */
export const getAttorneysByStaffClass = async (
  staffClassId: string,
  paginationParams?: { page?: number; limit?: number }
): Promise<PaginatedResponse<Attorney>> => {
  // Construct query parameters
  const queryParams = new URLSearchParams();
  queryParams.append('staffClassId', staffClassId);
  
  // Add pagination if provided
  if (paginationParams) {
    if (paginationParams.page) queryParams.append('page', paginationParams.page.toString());
    if (paginationParams.limit) queryParams.append('limit', paginationParams.limit.toString());
  }
  
  const url = `${buildUrl(API_ROUTES.ATTORNEYS.BASE)}?${queryParams.toString()}`;
  const response = await axiosInstance.get<PaginatedResponse<Attorney>>(url);
  return response.data;
};