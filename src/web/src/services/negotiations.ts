/**
 * Negotiations Service
 * 
 * This service provides functions for interacting with the Rate Negotiation API endpoints.
 * It handles all API calls related to rate negotiations between law firms and clients, including
 * creating negotiations, submitting rate proposals, counter-proposals, approvals, and rejections.
 *
 * @version 1.0.0
 */

import axiosInstance from '../api/axiosConfig';
import { API_ROUTES, buildUrl, buildUrlWithParams } from '../api/apiRoutes';
import {
  Negotiation,
  NegotiationSummary,
  NegotiationFilters,
  CreateNegotiationRequest,
  UpdateNegotiationRequest,
  SubmitRateProposalRequest,
  SubmitCounterProposalRequest,
  SubmitBulkActionRequest,
  NegotiationApprovalRequest,
  AIRecommendation
} from '../types/negotiation';
import { ApiResponse, PaginationParams, SortParams } from '../types/common';

/**
 * Fetches a list of negotiations with optional filtering, pagination, and sorting
 *
 * @param filters - Optional criteria to filter negotiations
 * @param pagination - Pagination parameters (page, pageSize)
 * @param sort - Sorting parameters (field, direction)
 * @returns Promise resolving to negotiation summaries and pagination data
 */
const getNegotiations = async (
  filters?: NegotiationFilters,
  pagination?: PaginationParams,
  sort?: SortParams
): Promise<ApiResponse<{ negotiations: NegotiationSummary[]; pagination: any }>> => {
  try {
    // Construct query parameters from filters, pagination, and sort
    const params = {
      ...filters,
      ...pagination,
      ...sort
    };

    // Make GET request to fetch negotiations with query parameters
    const response = await axiosInstance.get(
      buildUrl(API_ROUTES.NEGOTIATIONS.BASE),
      { params }
    );

    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Fetches a single negotiation by its ID with detailed information
 *
 * @param id - Negotiation ID to retrieve
 * @returns Promise resolving to detailed negotiation data
 */
const getNegotiationById = async (
  id: string
): Promise<ApiResponse<{ negotiation: Negotiation }>> => {
  try {
    // Construct URL with negotiation ID
    const url = buildUrlWithParams(API_ROUTES.NEGOTIATIONS.BY_ID, { id });
    
    // Make GET request to fetch negotiation details
    const response = await axiosInstance.get(url);
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Creates a new negotiation (rate request)
 *
 * @param data - Negotiation creation request data
 * @returns Promise resolving to the created negotiation
 */
const createNegotiation = async (
  data: CreateNegotiationRequest
): Promise<ApiResponse<{ negotiation: Negotiation }>> => {
  try {
    // Make POST request to create a new negotiation
    const response = await axiosInstance.post(
      buildUrl(API_ROUTES.NEGOTIATIONS.BASE),
      data
    );
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Updates an existing negotiation's general details
 *
 * @param id - Negotiation ID to update
 * @param data - Updated negotiation data
 * @returns Promise resolving to the updated negotiation
 */
const updateNegotiation = async (
  id: string,
  data: UpdateNegotiationRequest
): Promise<ApiResponse<{ negotiation: Negotiation }>> => {
  try {
    // Construct URL with negotiation ID
    const url = buildUrlWithParams(API_ROUTES.NEGOTIATIONS.BY_ID, { id });
    
    // Make PUT request to update negotiation details
    const response = await axiosInstance.put(url, data);
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Updates the status of a negotiation
 *
 * @param id - Negotiation ID to update
 * @param status - New status value
 * @returns Promise resolving to the updated negotiation
 */
const updateNegotiationStatus = async (
  id: string,
  status: string
): Promise<ApiResponse<{ negotiation: Negotiation }>> => {
  try {
    // Construct URL with negotiation ID for status update
    const url = buildUrlWithParams(API_ROUTES.NEGOTIATIONS.STATUS, { id });
    
    // Make PUT request to update negotiation status
    const response = await axiosInstance.put(url, { status });
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Submits rate proposals for a negotiation
 *
 * @param data - Rate proposal submission data
 * @returns Promise resolving to the updated negotiation with submitted proposals
 */
const submitRateProposals = async (
  data: SubmitRateProposalRequest
): Promise<ApiResponse<{ negotiation: Negotiation }>> => {
  try {
    // Construct URL with negotiation ID for submission
    const url = buildUrlWithParams(API_ROUTES.NEGOTIATIONS.SUBMIT, { id: data.negotiationId });
    
    // Make POST request to submit rate proposals
    const response = await axiosInstance.post(url, data);
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Submits counter-proposals for rates in a negotiation
 *
 * @param data - Counter-proposal submission data
 * @returns Promise resolving to the updated negotiation with counter-proposals
 */
const submitCounterProposals = async (
  data: SubmitCounterProposalRequest
): Promise<ApiResponse<{ negotiation: Negotiation }>> => {
  try {
    // Construct URL with negotiation ID for counter-proposals
    const url = buildUrlWithParams(
      API_ROUTES.NEGOTIATIONS.BY_ID + '/counter',
      { id: data.negotiationId }
    );
    
    // Make POST request to submit counter-proposals
    const response = await axiosInstance.post(url, data);
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Submits an action (approve, reject, counter) for a specific rate
 *
 * @param negotiationId - ID of the negotiation containing the rate
 * @param rateAction - Action data including rate ID, action type, and optional data
 * @returns Promise resolving to the updated negotiation
 */
const submitRateAction = async (
  negotiationId: string,
  rateAction: { rateId: string; action: string; amount?: number; message?: string }
): Promise<ApiResponse<{ negotiation: Negotiation }>> => {
  try {
    // Determine the appropriate endpoint based on the action
    let endpointPath;
    if (rateAction.action === 'approve') {
      endpointPath = '/approve';
    } else if (rateAction.action === 'reject') {
      endpointPath = '/reject';
    } else if (rateAction.action === 'counter') {
      endpointPath = '/counter';
    } else {
      throw new Error(`Invalid rate action: ${rateAction.action}`);
    }
    
    // Construct URL with negotiation ID and action
    const url = buildUrlWithParams(
      API_ROUTES.NEGOTIATIONS.BY_ID + endpointPath,
      { id: negotiationId }
    );
    
    // Make POST request with the rate action data
    const response = await axiosInstance.post(url, {
      rateId: rateAction.rateId,
      amount: rateAction.amount,
      message: rateAction.message
    });
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Submits bulk actions for multiple rates simultaneously
 *
 * @param data - Bulk action request data
 * @returns Promise resolving to the updated negotiation
 */
const submitBulkRateAction = async (
  data: SubmitBulkActionRequest
): Promise<ApiResponse<{ negotiation: Negotiation }>> => {
  try {
    // Construct URL with negotiation ID for bulk action
    const url = buildUrlWithParams(
      API_ROUTES.NEGOTIATIONS.BY_ID + '/bulk-action',
      { id: data.negotiationId }
    );
    
    // Make POST request with the bulk action data
    const response = await axiosInstance.post(url, data);
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Toggles between real-time and batch negotiation modes
 *
 * @param negotiationId - ID of the negotiation to update
 * @param realTimeEnabled - Whether real-time mode should be enabled
 * @returns Promise resolving to the updated negotiation with new mode
 */
const toggleRealTimeMode = async (
  negotiationId: string,
  realTimeEnabled: boolean
): Promise<ApiResponse<{ negotiation: Negotiation }>> => {
  try {
    // Construct URL with negotiation ID for real-time mode toggle
    const url = buildUrlWithParams(
      API_ROUTES.NEGOTIATIONS.BY_ID + '/real-time',
      { id: negotiationId }
    );
    
    // Make PUT request with the real-time mode flag
    const response = await axiosInstance.put(url, { realTimeEnabled });
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Submits an approval decision for a negotiation in an approval workflow
 *
 * @param data - Approval request data
 * @returns Promise resolving to the updated negotiation with approval status
 */
const submitApproval = async (
  data: NegotiationApprovalRequest
): Promise<ApiResponse<{ negotiation: Negotiation }>> => {
  try {
    // Construct URL with negotiation ID for approval
    const url = buildUrlWithParams(
      API_ROUTES.NEGOTIATIONS.APPROVE,
      { id: data.negotiationId }
    );
    
    // Make POST request with the approval data
    const response = await axiosInstance.post(url, data);
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Fetches AI-generated recommendations for rate actions
 *
 * @param negotiationId - ID of the negotiation to get recommendations for
 * @returns Promise resolving to list of AI recommendations
 */
const getAIRecommendations = async (
  negotiationId: string
): Promise<ApiResponse<{ recommendations: AIRecommendation[] }>> => {
  try {
    // Construct URL for AI recommendations endpoint
    const url = buildUrl(
      API_ROUTES.AI.RECOMMENDATIONS.RATES + `?negotiationId=${negotiationId}`
    );
    
    // Make GET request to fetch AI recommendations
    const response = await axiosInstance.get(url);
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Fetches the history of changes for a negotiation
 *
 * @param negotiationId - ID of the negotiation to get history for
 * @returns Promise resolving to negotiation history entries
 */
const getNegotiationHistory = async (
  negotiationId: string
): Promise<ApiResponse<{ history: any[] }>> => {
  try {
    // Construct URL with negotiation ID for history
    const url = buildUrlWithParams(
      API_ROUTES.NEGOTIATIONS.BY_ID + '/history',
      { id: negotiationId }
    );
    
    // Make GET request to fetch history data
    const response = await axiosInstance.get(url);
    
    return response.data;
  } catch (error) {
    // Let the global error handler handle any errors
    throw error;
  }
};

/**
 * Service object that provides functions for interacting with the negotiations API
 */
export const negotiationsService = {
  getNegotiations,
  getNegotiationById,
  createNegotiation,
  updateNegotiation,
  updateNegotiationStatus,
  submitRateProposals,
  submitCounterProposals,
  submitRateAction,
  submitBulkRateAction,
  toggleRealTimeMode,
  submitApproval,
  getAIRecommendations,
  getNegotiationHistory
};