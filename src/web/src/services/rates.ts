/**
 * Rate Service
 *
 * Service layer for rate-related operations, providing functions to interact with
 * the backend API for rate requests, submissions, negotiations, approvals, and analytics.
 * This service supports the core rate negotiation functionality of the Justice Bid system.
 *
 * @version 1.0.0
 */

import { AxiosError } from 'axios'; // ^1.4.0
import { get, post, put, delete as del } from '../services/api';
import { 
  Rate, 
  RateHistory, 
  RateRequest, 
  RateSubmission,
  CounterProposeRateRequest
} from '../types/rate';
import { 
  RateAnalytics, 
  RateImpact
} from '../types/analytics';
import { RATE_STATUS } from '../constants/rates';
import { API_ROUTES } from '../constants/api';
import { formatCurrency } from '../utils/currency';
import { calculateRateIncrease } from '../utils/calculations';

/**
 * Fetches rates based on provided filters
 * 
 * @param filters - Object containing filter criteria for rates
 * @returns Promise resolving to an array of Rate objects
 */
export async function getRates(filters: {
  attorneyId?: string;
  clientId?: string;
  firmId?: string;
  staffClassId?: string;
  status?: string;
  effectiveDateStart?: string;
  effectiveDateEnd?: string;
  page?: number;
  pageSize?: number;
}): Promise<Rate[]> {
  try {
    // Construct query parameters string from filters
    const queryParams = new URLSearchParams();
    
    // Add each filter parameter if it exists
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    // Call API to get rates with filters
    const response = await get<{ rates: Rate[] }>(
      `${API_ROUTES.RATES.BASE}?${queryParams.toString()}`
    );
    
    return response.rates;
  } catch (error) {
    console.error('Error fetching rates:', error);
    throw error;
  }
}

/**
 * Fetches a single rate by its ID
 * 
 * @param id - ID of the rate to fetch
 * @returns Promise resolving to the requested Rate object
 */
export async function getRateById(id: string): Promise<Rate> {
  try {
    const response = await get<{ rate: Rate }>(
      API_ROUTES.RATES.DETAIL(id)
    );
    return response.rate;
  } catch (error) {
    console.error(`Error fetching rate with ID ${id}:`, error);
    throw error;
  }
}

/**
 * Fetches rate history for an attorney or staff class
 * 
 * @param attorneyId - ID of the attorney to fetch history for
 * @param clientId - ID of the client to fetch history for
 * @returns Promise resolving to an array of historical rate objects
 */
export async function getRateHistory(
  attorneyId: string,
  clientId: string
): Promise<RateHistory[]> {
  try {
    // Construct query with attorneyId and clientId
    const queryParams = new URLSearchParams({
      attorneyId,
      clientId
    });

    // Call API to get rate history
    const response = await get<{ history: RateHistory[] }>(
      `${API_ROUTES.RATES.BASE}/history?${queryParams.toString()}`
    );
    
    return response.history;
  } catch (error) {
    console.error('Error fetching rate history:', error);
    throw error;
  }
}

/**
 * Creates a new rate request from a law firm to a client
 * 
 * @param requestData - Data for the rate request
 * @returns Promise resolving to object containing the created request ID
 */
export async function createRateRequest(
  requestData: RateRequest
): Promise<{ requestId: string }> {
  try {
    // Validate required fields
    if (!requestData.firmId || !requestData.clientId) {
      throw new Error('Firm ID and Client ID are required for rate requests');
    }

    // Call API to create a rate request
    const response = await post<{ requestId: string }>(
      API_ROUTES.RATE_REQUESTS.BASE,
      requestData
    );
    
    return response;
  } catch (error) {
    console.error('Error creating rate request:', error);
    throw error;
  }
}

/**
 * Approves a rate request, allowing the law firm to submit rates
 * 
 * @param requestId - ID of the rate request to approve
 * @param approvalData - Data for the approval including deadline and message
 * @returns Promise resolving to success status
 */
export async function approveRateRequest(
  requestId: string,
  approvalData: {
    submissionDeadline: string;
    message?: string;
  }
): Promise<{ success: boolean }> {
  try {
    // Call API to approve the rate request
    const response = await post<{ success: boolean }>(
      API_ROUTES.RATE_REQUESTS.APPROVE(requestId),
      approvalData
    );
    
    return response;
  } catch (error) {
    console.error(`Error approving rate request ${requestId}:`, error);
    throw error;
  }
}

/**
 * Rejects a rate request from a law firm
 * 
 * @param requestId - ID of the rate request to reject
 * @param rejectionData - Data for the rejection including reason
 * @returns Promise resolving to success status
 */
export async function rejectRateRequest(
  requestId: string,
  rejectionData: {
    message: string;
  }
): Promise<{ success: boolean }> {
  try {
    // Call API to reject the rate request
    const response = await post<{ success: boolean }>(
      API_ROUTES.RATE_REQUESTS.REJECT(requestId),
      rejectionData
    );
    
    return response;
  } catch (error) {
    console.error(`Error rejecting rate request ${requestId}:`, error);
    throw error;
  }
}

/**
 * Submits proposed rates for approval
 * 
 * @param submissionData - Data containing the rates to be submitted
 * @returns Promise resolving to submission ID
 */
export async function submitRates(
  submissionData: RateSubmission
): Promise<{ submissionId: string }> {
  try {
    // Validate submission data
    if (!submissionData.negotiationId || !submissionData.rates || submissionData.rates.length === 0) {
      throw new Error('Negotiation ID and at least one rate are required for submission');
    }

    // Calculate rate increases for validation
    for (const rate of submissionData.rates) {
      if (rate.currentRate > 0) {
        rate.percentageChange = calculateRateIncrease(rate.currentRate, rate.amount);
      }
    }

    // Call API to submit rates
    const response = await post<{ submissionId: string }>(
      API_ROUTES.NEGOTIATIONS.SUBMIT(submissionData.negotiationId),
      submissionData
    );
    
    return response;
  } catch (error) {
    console.error('Error submitting rates:', error);
    throw error;
  }
}

/**
 * Approves submitted rates
 * 
 * @param rateIds - Array of rate IDs to approve
 * @param approvalData - Data for the approval including message
 * @returns Promise resolving to success status
 */
export async function approveRates(
  rateIds: string[],
  approvalData: {
    message?: string;
  }
): Promise<{ success: boolean }> {
  try {
    // Call API to approve the specified rates
    const response = await post<{ success: boolean }>(
      `${API_ROUTES.RATES.BASE}/approve`,
      {
        rateIds,
        ...approvalData
      }
    );
    
    return response;
  } catch (error) {
    console.error('Error approving rates:', error);
    throw error;
  }
}

/**
 * Rejects submitted rates
 * 
 * @param rateIds - Array of rate IDs to reject
 * @param rejectionData - Data for the rejection including reason
 * @returns Promise resolving to success status
 */
export async function rejectRates(
  rateIds: string[],
  rejectionData: {
    message: string;
  }
): Promise<{ success: boolean }> {
  try {
    // Call API to reject the specified rates
    const response = await post<{ success: boolean }>(
      `${API_ROUTES.RATES.BASE}/reject`,
      {
        rateIds,
        ...rejectionData
      }
    );
    
    return response;
  } catch (error) {
    console.error('Error rejecting rates:', error);
    throw error;
  }
}

/**
 * Submits counter-proposed rates in response to submitted rates
 * 
 * @param counterProposals - Array of counter proposals
 * @returns Promise resolving to success status
 */
export async function counterProposeRates(
  counterProposals: Array<{
    rateId: string;
    amount: number;
    message?: string;
  }>
): Promise<{ success: boolean }> {
  try {
    // Validate counter-proposal data
    if (!counterProposals || counterProposals.length === 0) {
      throw new Error('At least one counter-proposal is required');
    }

    // Call API to submit counter-proposals
    const response = await post<{ success: boolean }>(
      `${API_ROUTES.RATES.BASE}/counter`,
      {
        counterProposals
      }
    );
    
    return response;
  } catch (error) {
    console.error('Error submitting counter-proposals:', error);
    throw error;
  }
}

/**
 * Gets rate impact analysis for proposed rates
 * 
 * @param negotiationId - ID of the negotiation to analyze
 * @param filters - Optional filters for the analysis
 * @returns Promise resolving to rate impact analysis data
 */
export async function getRateImpactAnalysis(
  negotiationId: string,
  filters: {
    staffClassId?: string;
    officeId?: string;
    practiceArea?: string;
    currency?: string;
  } = {}
): Promise<RateImpact> {
  try {
    // Construct query parameters string from filters
    const queryParams = new URLSearchParams({ negotiationId });
    
    // Add each filter parameter if it exists
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    // Call API to get rate impact analysis
    const response = await get<{ impact: RateImpact }>(
      `${API_ROUTES.ANALYTICS.IMPACT}?${queryParams.toString()}`
    );
    
    return response.impact;
  } catch (error) {
    console.error('Error fetching rate impact analysis:', error);
    throw error;
  }
}

/**
 * Gets analytics for rates
 * 
 * @param filters - Filters for the analytics
 * @returns Promise resolving to rate analytics data
 */
export async function getRateAnalytics(filters: {
  clientId?: string;
  firmId?: string;
  startDate?: string;
  endDate?: string;
  staffClassId?: string;
  practiceArea?: string;
  geography?: string;
  peerGroupId?: string;
}): Promise<RateAnalytics> {
  try {
    // Construct query parameters string from filters
    const queryParams = new URLSearchParams();
    
    // Add each filter parameter if it exists
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    // Call API to get rate analytics
    const response = await get<{ analytics: RateAnalytics }>(
      `${API_ROUTES.ANALYTICS.BASE}?${queryParams.toString()}`
    );
    
    return response.analytics;
  } catch (error) {
    console.error('Error fetching rate analytics:', error);
    throw error;
  }
}

/**
 * Validates rates against client-defined rate rules
 * 
 * @param clientId - ID of the client whose rules to validate against
 * @param rates - Array of rates to validate
 * @returns Promise resolving to validation results
 */
export async function validateRateRules(
  clientId: string,
  rates: Array<{
    attorneyId: string;
    amount: number;
    currentRate?: number;
    effectiveDate: string;
  }>
): Promise<{
  valid: boolean;
  violations: Array<{
    rateId?: string;
    attorneyId: string;
    rule: string;
    message: string;
  }>;
}> {
  try {
    // Call API to validate rates against client rules
    const response = await post<{
      valid: boolean;
      violations: Array<{
        rateId?: string;
        attorneyId: string;
        rule: string;
        message: string;
      }>;
    }>(
      `${API_ROUTES.RATES.BASE}/validate`,
      {
        clientId,
        rates
      }
    );
    
    return response;
  } catch (error) {
    console.error('Error validating rates against client rules:', error);
    throw error;
  }
}

/**
 * Gets rate comparison data for peer groups
 * 
 * @param peerGroupId - ID of the peer group to compare with
 * @param filters - Optional filters for the comparison
 * @returns Promise resolving to peer group comparison data
 */
export async function getPeerGroupComparison(
  peerGroupId: string,
  filters: {
    staffClassId?: string;
    effectiveYear?: number;
    practiceArea?: string;
  } = {}
): Promise<object> {
  try {
    // Construct query parameters string from filters
    const queryParams = new URLSearchParams({ peerGroupId });
    
    // Add each filter parameter if it exists
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    // Call API to get peer comparison data
    const response = await get<{ comparison: object }>(
      `${API_ROUTES.ANALYTICS.COMPARISON}?${queryParams.toString()}`
    );
    
    return response.comparison;
  } catch (error) {
    console.error('Error fetching peer group comparison:', error);
    throw error;
  }
}

/**
 * Imports rates from a file
 * 
 * @param file - File containing rate data
 * @param importOptions - Options for the import process
 * @returns Promise resolving to import results
 */
export async function importRates(
  file: File,
  importOptions: {
    clientId?: string;
    firmId?: string;
    effectiveDate?: string;
    currency?: string;
    staffClassMapping?: Record<string, string>;
  } = {}
): Promise<{
  success: boolean;
  imported: number;
  errors: Array<{ row: number; message: string }>;
}> {
  try {
    // Create form data with file and import options
    const formData = new FormData();
    formData.append('file', file);
    
    // Add import options as JSON
    formData.append('options', JSON.stringify(importOptions));

    // Call API to upload and process the file
    const response = await post<{
      success: boolean;
      imported: number;
      errors: Array<{ row: number; message: string }>;
    }>(
      API_ROUTES.INTEGRATIONS.FILE.IMPORT,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    return response;
  } catch (error) {
    console.error('Error importing rates:', error);
    throw error;
  }
}

/**
 * Exports rates to a file format
 * 
 * @param filters - Filters to determine which rates to export
 * @param format - Format for the export (excel, csv, etc.)
 * @returns Promise resolving to file blob for download
 */
export async function exportRates(
  filters: {
    clientId?: string;
    firmId?: string;
    status?: string;
    effectiveDateStart?: string;
    effectiveDateEnd?: string;
  },
  format: string = 'excel'
): Promise<Blob> {
  try {
    // Construct query parameters string from filters and format
    const queryParams = new URLSearchParams({ format });
    
    // Add each filter parameter if it exists
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    // Call API to get exported rates as blob
    const response = await get<Blob>(
      `${API_ROUTES.INTEGRATIONS.FILE.EXPORT}?${queryParams.toString()}`,
      {
        responseType: 'blob'
      }
    );
    
    return response;
  } catch (error) {
    console.error('Error exporting rates:', error);
    throw error;
  }
}