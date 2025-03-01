import { createSlice, PayloadAction } from '@reduxjs/toolkit'; //  ^1.9.5
import {
  AnalyticsState,
  ImpactAnalysisData,
  PeerComparisonData,
  HistoricalTrendsData,
  AttorneyPerformanceData,
  CustomReport,
  AnalyticsFilters
} from '../../types/analytics';
import { RootState } from '../index';

/**
 * Initial state for the analytics slice
 */
const initialState: AnalyticsState = {
  impactAnalysis: {
    data: null,
    loading: false,
    error: null
  },
  peerComparison: {
    data: null,
    loading: false,
    error: null
  },
  historicalTrends: {
    data: null,
    loading: false,
    error: null
  },
  attorneyPerformance: {
    data: null,
    loading: false,
    error: null
  },
  customReports: {
    list: [],
    current: null,
    loading: false,
    error: null
  },
  filters: {
    clientId: null,
    firmId: null,
    attorneyId: null,
    staffClassId: null,
    practiceArea: null,
    officeId: null,
    geography: null,
    dateRange: null,
    timeframe: null,
    peerGroupId: null,
    currency: 'USD',
    negotiationId: null,
    rateStatus: null,
    rateType: null
  }
};

/**
 * Redux slice for managing analytics state in the Justice Bid Rate Negotiation System.
 * Handles state for rate impact analysis, peer comparisons, historical trends,
 * attorney performance metrics, and custom reports.
 */
const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    /**
     * Sets the loading state for impact analysis
     * @param state - Current state
     * @param action - Payload action with loading status
     */
    setImpactAnalysisLoading: (state, action: PayloadAction<boolean>) => {
      state.impactAnalysis.loading = action.payload;
    },
    /**
     * Sets the impact analysis data
     * @param state - Current state
     * @param action - Payload action with impact analysis data
     */
    setImpactAnalysisData: (state, action: PayloadAction<ImpactAnalysisData | null>) => {
      state.impactAnalysis.data = action.payload;
    },
    /**
     * Sets the error state for impact analysis
     * @param state - Current state
     * @param action - Payload action with error message
     */
    setImpactAnalysisError: (state, action: PayloadAction<string | null>) => {
      state.impactAnalysis.error = action.payload;
    },
    /**
     * Sets the loading state for peer comparison
     * @param state - Current state
     * @param action - Payload action with loading status
     */
    setPeerComparisonLoading: (state, action: PayloadAction<boolean>) => {
      state.peerComparison.loading = action.payload;
    },
    /**
     * Sets the peer comparison data
     * @param state - Current state
     * @param action - Payload action with peer comparison data
     */
    setPeerComparisonData: (state, action: PayloadAction<PeerComparisonData | null>) => {
      state.peerComparison.data = action.payload;
    },
    /**
     * Sets the error state for peer comparison
     * @param state - Current state
     * @param action - Payload action with error message
     */
    setPeerComparisonError: (state, action: PayloadAction<string | null>) => {
      state.peerComparison.error = action.payload;
    },
    /**
     * Sets the loading state for historical trends
     * @param state - Current state
     * @param action - Payload action with loading status
     */
    setHistoricalTrendsLoading: (state, action: PayloadAction<boolean>) => {
      state.historicalTrends.loading = action.payload;
    },
    /**
     * Sets the historical trends data
     * @param state - Current state
     * @param action - Payload action with historical trends data
     */
    setHistoricalTrendsData: (state, action: PayloadAction<HistoricalTrendsData | null>) => {
      state.historicalTrends.data = action.payload;
    },
    /**
     * Sets the error state for historical trends
     * @param state - Current state
     * @param action - Payload action with error message
     */
    setHistoricalTrendsError: (state, action: PayloadAction<string | null>) => {
      state.historicalTrends.error = action.payload;
    },
    /**
     * Sets the loading state for attorney performance
     * @param state - Current state
     * @param action - Payload action with loading status
     */
    setAttorneyPerformanceLoading: (state, action: PayloadAction<boolean>) => {
      state.attorneyPerformance.loading = action.payload;
    },
    /**
     * Sets the attorney performance data
     * @param state - Current state
     * @param action - Payload action with attorney performance data
     */
    setAttorneyPerformanceData: (state, action: PayloadAction<AttorneyPerformanceData | null>) => {
      state.attorneyPerformance.data = action.payload;
    },
    /**
     * Sets the error state for attorney performance
     * @param state - Current state
     * @param action - Payload action with error message
     */
    setAttorneyPerformanceError: (state, action: PayloadAction<string | null>) => {
      state.attorneyPerformance.error = action.payload;
    },
    /**
     * Sets the loading state for custom reports
     * @param state - Current state
     * @param action - Payload action with loading status
     */
    setCustomReportsLoading: (state, action: PayloadAction<boolean>) => {
      state.customReports.loading = action.payload;
    },
    /**
     * Sets the list of custom reports
     * @param state - Current state
     * @param action - Payload action with custom reports list
     */
    setCustomReportsList: (state, action: PayloadAction<CustomReport[]>) => {
      state.customReports.list = action.payload;
    },
    /**
     * Sets the current custom report
     * @param state - Current state
     * @param action - Payload action with current custom report
     */
    setCurrentCustomReport: (state, action: PayloadAction<CustomReport | null>) => {
      state.customReports.current = action.payload;
    },
    /**
     * Sets the error state for custom reports
     * @param state - Current state
     * @param action - Payload action with error message
     */
    setCustomReportsError: (state, action: PayloadAction<string | null>) => {
      state.customReports.error = action.payload;
    },
    /**
     * Sets the analytics filters
     * @param state - Current state
     * @param action - Payload action with analytics filters
     */
    setAnalyticsFilters: (state, action: PayloadAction<AnalyticsFilters>) => {
      state.filters = action.payload;
    },
    /**
     * Resets the analytics state to initial values
     * @param state - Current state
     */
    resetAnalyticsState: (state) => {
      state.impactAnalysis = initialState.impactAnalysis;
      state.peerComparison = initialState.peerComparison;
      state.historicalTrends = initialState.historicalTrends;
      state.attorneyPerformance = initialState.attorneyPerformance;
      state.customReports = initialState.customReports;
      state.filters = initialState.filters;
    }
  }
});

// Extract the action creators
export const analyticsActions = analyticsSlice.actions;

// Export the reducer as the default export
export default analyticsSlice.reducer;

// Selectors
export const analyticsSelectors = {
  /**
   * Selector function to retrieve impact analysis state from the Redux store
   * @param state 
   * @returns Impact analysis state containing data, loading status, and error information
   */
  selectImpactAnalysis: (state: RootState) => state.analytics.impactAnalysis,
  /**
   * Selector function to retrieve peer comparison state from the Redux store
   * @param state 
   * @returns Peer comparison state containing data, loading status, and error information
   */
  selectPeerComparison: (state: RootState) => state.analytics.peerComparison,
  /**
   * Selector function to retrieve historical trends state from the Redux store
   * @param state 
   * @returns Historical trends state containing data, loading status, and error information
   */
  selectHistoricalTrends: (state: RootState) => state.analytics.historicalTrends,
  /**
   * Selector function to retrieve attorney performance state from the Redux store
   * @param state 
   * @returns Attorney performance state containing data, loading status, and error information
   */
  selectAttorneyPerformance: (state: RootState) => state.analytics.attorneyPerformance,
  /**
   * Selector function to retrieve custom reports state from the Redux store
   * @param state 
   * @returns Custom reports state containing list, current report, loading status, and error information
   */
  selectCustomReports: (state: RootState) => state.analytics.customReports,
  /**
   * Selector function to retrieve analytics filters from the Redux store
   * @param state 
   * @returns Current analytics filters configuration
   */
  selectAnalyticsFilters: (state: RootState) => state.analytics.filters
};