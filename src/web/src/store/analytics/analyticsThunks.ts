/**
 * Redux Toolkit thunks for handling asynchronous analytics operations in the Justice Bid Rate Negotiation System.
 * These thunks provide actions for fetching various analytics data from the backend API and updating the Redux store.
 */

import { createAsyncThunk } from '@reduxjs/toolkit'; // ^1.9.0
import { analyticsService } from '../../../services/analytics';
import * as types from '../../../types/analytics';
import { analyticsConstants } from '../../../constants/analytics';

/**
 * Async thunk to fetch rate impact analysis data
 */
export const fetchImpactAnalysis = createAsyncThunk<
  types.ImpactAnalysisData,
  types.ImpactAnalysisParams,
  { rejectValue: { message: string } }
>(
  `${analyticsConstants.ANALYTICS_SLICE_NAME}/fetchImpactAnalysis`,
  async (params: types.ImpactAnalysisParams, thunkAPI) => {
    try {
      // LD1: Call analyticsService.getImpactAnalysis with parameters
      const impactAnalysisData = await analyticsService.getImpactAnalysis(params);
      // LD1: Return the impact analysis data on success
      return impactAnalysisData;
    } catch (error: any) {
      // LD1: Handle errors by rejecting with error message
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk to fetch peer comparison data
 */
export const fetchPeerComparison = createAsyncThunk<
  types.PeerComparisonData,
  types.PeerComparisonParams,
  { rejectValue: { message: string } }
>(
  `${analyticsConstants.ANALYTICS_SLICE_NAME}/fetchPeerComparison`,
  async (params: types.PeerComparisonParams, thunkAPI) => {
    try {
      // LD1: Call analyticsService.getPeerComparison with parameters
      const peerComparisonData = await analyticsService.getPeerComparison(params);
      // LD1: Return the peer comparison data on success
      return peerComparisonData;
    } catch (error: any) {
      // LD1: Handle errors by rejecting with error message
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk to fetch historical rate trends data
 */
export const fetchHistoricalTrends = createAsyncThunk<
  types.HistoricalTrendsData,
  types.HistoricalTrendsParams,
  { rejectValue: { message: string } }
>(
  `${analyticsConstants.ANALYTICS_SLICE_NAME}/fetchHistoricalTrends`,
  async (params: types.HistoricalTrendsParams, thunkAPI) => {
    try {
      // LD1: Call analyticsService.getHistoricalTrends with parameters
      const historicalTrendsData = await analyticsService.getHistoricalTrends(params);
      // LD1: Return the historical trends data on success
      return historicalTrendsData;
    } catch (error: any) {
      // LD1: Handle errors by rejecting with error message
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk to fetch attorney performance analytics
 */
export const fetchAttorneyPerformance = createAsyncThunk<
  types.AttorneyPerformanceData,
  types.AttorneyPerformanceParams,
  { rejectValue: { message: string } }
>(
  `${analyticsConstants.ANALYTICS_SLICE_NAME}/fetchAttorneyPerformance`,
  async (params: types.AttorneyPerformanceParams, thunkAPI) => {
    try {
      // LD1: Call analyticsService.getAttorneyPerformance with parameters
      const attorneyPerformanceData = await analyticsService.getAttorneyPerformance(params.attorneyId, params);
      // LD1: Return the attorney performance data on success
      return attorneyPerformanceData;
    } catch (error: any) {
      // LD1: Handle errors by rejecting with error message
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk to create a new custom analytics report
 */
export const createCustomReport = createAsyncThunk<
  types.CustomReportData,
  types.CustomReportParams,
  { rejectValue: { message: string } }
>(
  `${analyticsConstants.ANALYTICS_SLICE_NAME}/createCustomReport`,
  async (params: types.CustomReportParams, thunkAPI) => {
    try {
      // LD1: Call analyticsService.createCustomReport with parameters
      const customReportData = await analyticsService.createCustomReport(params);
      // LD1: Return the created custom report data on success
      return customReportData;
    } catch (error: any) {
      // LD1: Handle errors by rejecting with error message
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk to fetch an existing custom report
 */
export const fetchCustomReport = createAsyncThunk<
  types.CustomReportData,
  string,
  { rejectValue: { message: string } }
>(
  `${analyticsConstants.ANALYTICS_SLICE_NAME}/fetchCustomReport`,
  async (reportId: string, thunkAPI) => {
    try {
      // LD1: Call analyticsService.getCustomReport with the report ID
      const customReportData = await analyticsService.getCustomReport(reportId);
      // LD1: Return the custom report data on success
      return customReportData;
    } catch (error: any) {
      // LD1: Handle errors by rejecting with error message
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);

/**
 * Async thunk to export analytics data to a file
 */
export const exportAnalyticsData = createAsyncThunk<
  string,
  types.ExportParams,
  { rejectValue: { message: string } }
>(
  `${analyticsConstants.ANALYTICS_SLICE_NAME}/exportAnalyticsData`,
  async (params: types.ExportParams, thunkAPI) => {
    try {
      // LD1: Call analyticsService.exportAnalyticsData with parameters
      await analyticsService.exportAnalyticsData(params.filters, params.format);
      // LD1: Return the exported file URL on success
      return 'exported';
    } catch (error: any) {
      // LD1: Handle errors by rejecting with error message
      return thunkAPI.rejectWithValue({ message: error.message });
    }
  }
);