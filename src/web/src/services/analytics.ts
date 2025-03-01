/**
 * Service for handling analytics-related API calls and data processing for the Justice Bid Rate Negotiation System.
 * This service provides functions for retrieving impact analysis, peer comparisons, historical trends, attorney performance metrics, and custom reports.
 * @version 1.0.0
 */

import axios from 'axios'; // ^1.4.0
import { api } from '../services/api';
import {
  AnalyticsTypes,
  ANALYTICS_ROUTES
} from '../api/apiRoutes';
import {
  processRateImpact,
  formatChartData
} from '../utils/analytics';

/**
 * Fetches rate impact analysis data based on provided parameters
 * @param params - Analytics parameters including filters, view type, and grouping dimensions
 * @returns Promise resolving to impact analysis data including total impact, highest/lowest impacts, and impact by category
 */
export const getImpactAnalysis = async (params: AnalyticsTypes.AnalyticsParams): Promise<AnalyticsTypes.RateImpactAnalysis> => {
  // Makes an API call to the impact analysis endpoint with the provided parameters
  const url = api.buildUrl(ANALYTICS_ROUTES.ANALYTICS.IMPACT);
  const response = await api.get(url, { params });

  // Processes the response data using the processRateImpact utility function
  const processedData = processRateImpact(response);

  // Returns the formatted impact analysis data
  return processedData;
};

/**
 * Fetches peer comparison data for rates
 * @param params - Analytics parameters including filters, view type, and grouping dimensions
 * @returns Promise resolving to peer comparison data including average rates, rate ranges, and comparisons against peer groups
 */
export const getPeerComparison = async (params: AnalyticsTypes.AnalyticsParams): Promise<AnalyticsTypes.PeerComparison> => {
  // Makes an API call to the peer comparison endpoint with the provided parameters
  const url = api.buildUrl(ANALYTICS_ROUTES.ANALYTICS.COMPARISON);
  const response = await api.get(url, { params });

  // Formats the response data using the formatChartData utility for visualization
  const formattedData = formatChartData(response, 'bar');

  // Returns the formatted peer comparison data
  return formattedData as any;
};

/**
 * Fetches historical rate trend data
 * @param params - Analytics parameters including filters, view type, and grouping dimensions
 * @returns Promise resolving to historical trend data including year-over-year changes and CAGR
 */
export const getHistoricalTrends = async (params: AnalyticsTypes.AnalyticsParams): Promise<AnalyticsTypes.HistoricalTrend> => {
  // Makes an API call to the historical trends endpoint with the provided parameters
  const url = api.buildUrl(ANALYTICS_ROUTES.ANALYTICS.TRENDS);
  const response = await api.get(url, { params });

  // Formats the response data for time-series visualization
  const formattedData = formatChartData(response, 'line');

  // Calculates additional metrics like CAGR and inflation comparison
  // Returns the formatted historical trend data
  return formattedData as any;
};

/**
 * Fetches performance analytics for attorneys
 * @param attorneyId - ID of the attorney to fetch performance data for
 * @param params - Analytics parameters including filters and metric types
 * @returns Promise resolving to attorney performance data including billing metrics and UniCourt performance data
 */
export const getAttorneyPerformance = async (attorneyId: string, params: AnalyticsTypes.AnalyticsParams): Promise<AnalyticsTypes.AttorneyPerformance> => {
  // Makes an API call to the attorney performance endpoint with the attorney ID and parameters
  const url = api.buildUrlWithParams(ANALYTICS_ROUTES.ANALYTICS.PERFORMANCE, { id: attorneyId });
  const response = await api.get(url, { params });

  // Combines billing performance metrics with UniCourt data if available
  // Returns the comprehensive attorney performance data
  return response;
};

/**
 * Creates a new custom report based on provided parameters
 * @param reportParams - Parameters for the custom report including name, description, filters, and chart configuration
 * @returns Promise resolving to created custom report data including ID and generation status
 */
export const createCustomReport = async (reportParams: AnalyticsTypes.ReportParams): Promise<AnalyticsTypes.CustomReport> => {
  // Makes a POST request to the custom reports endpoint with the report parameters
   const url = api.buildUrl(ANALYTICS_ROUTES.ANALYTICS.REPORTS);
  const response = await api.post(url, reportParams);

  // Returns the created report data including the report ID
  return response;
};

/**
 * Fetches a custom report by its ID
 * @param reportId - ID of the custom report to fetch
 * @returns Promise resolving to custom report data including results and metadata
 */
export const getCustomReport = async (reportId: string): Promise<AnalyticsTypes.CustomReport> => {
  // Makes a GET request to the specific custom report endpoint using the report ID
  const url = api.buildUrlWithParams(ANALYTICS_ROUTES.ANALYTICS.REPORT_BY_ID, { id: reportId });
  const response = await api.get(url);

  // Returns the report data including results if the report is complete
  return response;
};

/**
 * Fetches a list of all custom reports for the current user
 * @returns Promise resolving to array of custom report data
 */
export const listCustomReports = async (): Promise<AnalyticsTypes.CustomReport[]> => {
  // Makes a GET request to the custom reports endpoint
  const url = api.buildUrl(ANALYTICS_ROUTES.ANALYTICS.REPORTS);
  const response = await api.get(url);

  // Returns an array of all custom reports created by the user
  return response;
};

/**
 * Deletes a custom report by its ID
 * @param reportId - ID of the custom report to delete
 * @returns Promise resolving to void on successful deletion
 */
export const deleteCustomReport = async (reportId: string): Promise<void> => {
  // Makes a DELETE request to the specific custom report endpoint using the report ID
  const url = api.buildUrlWithParams(ANALYTICS_ROUTES.ANALYTICS.REPORT_BY_ID, { id: reportId });
  await api.delete(url);

  // Returns void on successful deletion
  return;
};

/**
 * Shares a custom report with specified users
 * @param reportId - ID of the custom report to share
 * @param userIds - Array of user IDs to share the report with
 * @returns Promise resolving to void on successful sharing
 */
export const shareCustomReport = async (reportId: string, userIds: string[]): Promise<void> => {
  // Makes a POST request to the report sharing endpoint with the report ID and array of user IDs
  const url = api.buildUrl(`/analytics/reports/${reportId}/share`); // Assuming there's a specific share endpoint
  const response = await api.post(url, { userIds });

  // Returns void on successful sharing operation
  return;
};

/**
 * Exports analytics data in the specified format
 * @param params - Analytics parameters including filters and data dimensions
 * @param format - Format to export the data in (e.g., PDF, Excel, CSV)
 * @returns Promise resolving to a Blob containing the exported data in the requested format
 */
export const exportAnalytics = async (params: AnalyticsTypes.AnalyticsParams, format: string): Promise<Blob> => {
  // Makes a POST request to the analytics export endpoint with the parameters and format
  const url = api.buildUrl('/analytics/export'); // Assuming there's a specific export endpoint
  const response = await api.post(url, { ...params, format }, { responseType: 'blob' });

  // Receives a blob response with the exported data
  // Returns the blob for client-side download
  return response;
};