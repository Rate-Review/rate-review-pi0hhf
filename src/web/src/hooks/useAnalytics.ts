import { useCallback, useEffect, useMemo, useState } from 'react'; // v18.2.0
import { useSelector, useDispatch } from 'react-redux'; // ^8.0.5
import { useQuery, useMutation } from 'react-query'; // ^3.39.0

import useQueryParams from '../hooks/useQueryParams';
import { RootState } from '../store';
import {
  fetchImpactAnalysis, fetchPeerComparison, fetchHistoricalTrends, fetchAttorneyPerformance, generateCustomReport
} from '../store/analytics/analyticsThunks';
import {
  selectImpactAnalysis, selectPeerComparison, selectHistoricalTrends, selectAttorneyPerformance, selectCustomReport, selectIsLoading, selectError
} from '../store/analytics/analyticsSlice';
import {
  ImpactAnalysisParams, PeerComparisonParams, HistoricalTrendsParams, AttorneyPerformanceParams, CustomReportParams, ImpactAnalysisData, PeerComparisonData, HistoricalTrendsData, AttorneyPerformanceData, CustomReportData, AnalyticsFilterParams
} from '../types/analytics';
import { calculatePercentageChange, aggregateByDimension } from '../utils/analytics';
import { formatCurrency } from '../utils/currency';
import { exportAnalyticsData } from '../services/analytics';

/**
 * A custom hook that provides analytics-related functionality, including data fetching, state management, and utility methods for working with analytics data in the Justice Bid Rate Negotiation System.
 *
 * @returns {object} An object containing analytics data and methods for working with analytics
 */
const useAnalytics = () => {
  // LD1: Initialize state for local analytics filters and parameters
  const [localFilters, setLocalFilters] = useState<AnalyticsFilterParams>({} as AnalyticsFilterParams);
  const [localParams, setLocalParams] = useState<ImpactAnalysisParams>({} as ImpactAnalysisParams);

  // LD1: Setup Redux hooks for accessing analytics state and dispatching actions
  const dispatch = useDispatch();
  const impactAnalysis = useSelector<RootState, ImpactAnalysisData | null>(selectImpactAnalysis);
  const peerComparison = useSelector<RootState, PeerComparisonData | null>(selectPeerComparison);
  const historicalTrends = useSelector<RootState, HistoricalTrendsData | null>(selectHistoricalTrends);
  const attorneyPerformance = useSelector<RootState, AttorneyPerformanceData | null>(selectAttorneyPerformance);
  const customReport = useSelector<RootState, CustomReportData | null>(selectCustomReport);
  const isLoading = useSelector<RootState, boolean>(selectIsLoading);
  const error = useSelector<RootState, string | null>(selectError);

  // LD1: Initialize query parameters handling using useQueryParams hook
  const { params: filters, setParams: setFilters } = useQueryParams<AnalyticsFilterParams>();

  // LD1: Setup data fetching methods for different analytics types (impact analysis, peer comparison, etc.)
  const fetchImpactAnalysisData = useCallback((params: ImpactAnalysisParams) => {
    dispatch(fetchImpactAnalysis(params));
  }, [dispatch]);

  const fetchPeerComparisonData = useCallback((params: PeerComparisonParams) => {
    dispatch(fetchPeerComparison(params));
  }, [dispatch]);

  const fetchHistoricalTrendsData = useCallback((params: HistoricalTrendsParams) => {
    dispatch(fetchHistoricalTrends(params));
  }, [dispatch]);

  const fetchAttorneyPerformanceData = useCallback((params: AttorneyPerformanceParams) => {
    dispatch(fetchAttorneyPerformance(params));
  }, [dispatch]);

  const generateCustomReportData = useCallback((params: CustomReportParams) => {
    dispatch(generateCustomReport(params));
  }, [dispatch]);

  // LD1: Implement data export functionality
  const exportData = useCallback(async (format: string) => {
    try {
      await exportAnalyticsData(filters, format);
    } catch (err) {
      console.error('Error exporting analytics data:', err);
    }
  }, [filters]);

  // LD1: Implement utility methods for analytics operations
  const getPercentageChange = useCallback((current: number, proposed: number) => {
    return calculatePercentageChange(current, proposed);
  }, []);

  const getFormattedCurrency = useCallback((amount: number, currencyCode: string) => {
    return formatCurrency(amount, currencyCode);
  }, []);

  const aggregateData = useCallback((data: any[], dimension: string) => {
    return aggregateByDimension(data, dimension);
  }, []);

  // LD1: Memoize complex calculations to optimize performance
  const memoizedValues = useMemo(() => ({
    impactAnalysis,
    peerComparison,
    historicalTrends,
    attorneyPerformance,
    customReport,
    isLoading,
    error,
    filters,
  }), [impactAnalysis, peerComparison, historicalTrends, attorneyPerformance, customReport, isLoading, error, filters]);

  // LD1: Return analytics data, loading/error states, and all methods in a single object
  return {
    ...memoizedValues,
    fetchImpactAnalysis: fetchImpactAnalysisData,
    fetchPeerComparison: fetchPeerComparisonData,
    fetchHistoricalTrends: fetchHistoricalTrendsData,
    fetchAttorneyPerformance: fetchAttorneyPerformanceData,
    generateCustomReport: generateCustomReportData,
    exportData,
    setFilters,
    getPercentageChange,
    getFormattedCurrency,
    aggregateData,
  };
};

export default useAnalytics;